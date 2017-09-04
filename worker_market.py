from bittrex import Bittrex
from worker_buysell import *
from datetime import datetime
from utilities import *
import operator
import time

try:
	import user
	key = user.key
	secret = user.secret
except:
	key = None
	secret = None
	
#print key, secret
user = BittrexBuysellWorker(key, secret)
EXCHANGE_RATE = 0.9975
market_list = user.w_get_market_list()
coin_list = []
#get coin list
for m in market_list:
	c1, c2  = w_extract_market_name(m)
	if c2 not in coin_list:
		coin_list.append(c2)

def get_route(coin_status):

	''' note: 
	coin_status = (best_round , best_rate, best_coin)
	cw1 clockwise        :  usdt -> btc -> xxx -> usdt
	ccw1 counterclockwise:  usdt -> xxx -> btc -> usdt
	cw2 clockwise        :  usdt -> eth -> xxx -> usdt
	ccw2 counterclockwise:  usdt -> xxx -> eth -> usdt
	cw3 clockwise        :  btc  -> xxx -> eth -> btc
	ccw3 counterclockwise:  btc  -> eth -> xxx -> btc
	'''
	coin, round , rate = coin_status
	
	if (round == "cw1"):
		route = ("USDT", "BTC", coin, "USDT")
	elif (round == "ccw1"):
		route = ("USDT", coin, "BTC", "USDT")
	elif (round == "cw2"):
		route = ("USDT", "ETH", coin, "USDT")
	elif (round == "ccw2"):
		route = ("USDT", coin, "ETH", "USDT")
	elif (round == "cw3"):
		route = ("BTC", "ETH", coin, "BTC")
	elif (round == "ccw3"):
		route = ("BTC", coin, "ETH", "BTC")
	else:
		print "Error no coin_status"
		return	
	return route

	
def detect_round_change():
	''' note: 
	cw1 clockwise        :  usdt -> btc -> xxx -> usdt
	ccw1 counterclockwise:  usdt -> xxx -> btc -> usdt
	cw2 clockwise        :  usdt -> eth -> xxx -> usdt
	ccw2 counterclockwise:  usdt -> xxx -> eth -> usdt
	cw3 clockwise        :  btc  -> xxx -> eth -> btc
	ccw3 counterclockwise:  btc  -> eth -> xxx -> btc
	'''	
	try:
		m = user.w_get_api().get_market_summaries()
		marketsummaries = m.get("result")
		[(usdt_btc_ask, usdt_btc_last, usdt_btc_bid )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'USDT-BTC' ]
		[(usdt_eth_ask, usdt_eth_last, usdt_eth_bid )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'USDT-ETH' ]
		[(btc_eth_ask,  btc_eth_last,  btc_eth_bid  )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'BTC-ETH' ]
		
		coin_stats = []   #list of best round for each coin
		
		for coin in coin_list:
			#print coin
			if coin == "BTC":
				continue
			
			#usdt_xxx_ask = usdt_xxx_last = usdt_xxx_bid = 1
			#btc_xxx_ask = btc_xxx_last = btc_xxx_bid = 1
			#eth_xxx_ask = eth_xxx_last = eth_xxx_bid = 1
			
			#USDT-XXX
			market_usdt, type = user.w_get_market_name("USDT", coin, False)
			if market_usdt:
				[(usdt_xxx_ask, usdt_xxx_last, usdt_xxx_bid )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == market_usdt ] 
			#BTC-XXX
			market_btc, type = user.w_get_market_name("BTC", coin, False)
			if market_btc:
				[(btc_xxx_ask, btc_xxx_last, btc_xxx_bid )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == market_btc ] 
			#ETH-XXX
			market_eth, type = user.w_get_market_name("ETH", coin, False)
			if market_eth:
				[(eth_xxx_ask, eth_xxx_last, eth_xxx_bid )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == market_eth ] 
			
			cw1 = ccw1 = cw2 = ccw2 =  cw3 = ccw3 = 0
			#calculate round rate
			if market_usdt and market_btc:
				cw1 = ((usdt_xxx_bid/usdt_btc_ask)/btc_xxx_ask) *  EXCHANGE_RATE * EXCHANGE_RATE * EXCHANGE_RATE
				ccw1 = (usdt_btc_bid / usdt_xxx_ask )* btc_xxx_bid  *  EXCHANGE_RATE * EXCHANGE_RATE * EXCHANGE_RATE
			
			if market_usdt and market_eth:
				cw2 = ((usdt_xxx_bid /usdt_eth_ask)/eth_xxx_ask )*  EXCHANGE_RATE * EXCHANGE_RATE * EXCHANGE_RATE
				ccw2 = (usdt_eth_bid / usdt_xxx_ask) * eth_xxx_bid  *  EXCHANGE_RATE * EXCHANGE_RATE * EXCHANGE_RATE
			
			if market_btc and market_eth:
				cw3 = ((btc_xxx_bid /btc_eth_ask)/eth_xxx_ask )*  EXCHANGE_RATE * EXCHANGE_RATE * EXCHANGE_RATE
				ccw3 = (btc_eth_bid / btc_xxx_ask) * btc_xxx_bid  *  EXCHANGE_RATE * EXCHANGE_RATE * EXCHANGE_RATE

			
			rate = max(cw1, ccw1, cw2, ccw2,  cw3, ccw3)
			package = {
				"cw1":cw1, "ccw1": ccw1, 
				"cw2":cw2, "ccw2": ccw2, 
				"cw3":cw3, "ccw3": ccw3, 			
			}
			#	print package
			
			round, rate = max(package.iteritems(), key=operator.itemgetter(1))
			#print round, rate
			
			coin_stats.append((coin,round,rate))
			
		#find best changes:
		#print coin_stats
		best_coin, best_round , best_rate = max(coin_stats,key=lambda item:item[2])
		#print best_coin, best_round , best_rate
		return best_coin, best_round , best_rate
		
	except Exception as e:
		print(e.message)
		print "Error connection issue. Can't get marketsummaries"
		if (m):
			print m.get("message")

def run_detect_round_change(run_times,interval):
	while (1):			
		curr_time = str(datetime.now())
		coin, path, rate = round = detect_round_change()
		print "{}\t{}\t{}\t{}\t{}".format(curr_time, coin, path, get_route(round), rate )
		time.sleep(interval)
		
		if run_times == 1: #Run n times until reaching 1
			break;
		elif run_times == 0: #Run forever
			continue
		else:
			run_times -= 1
			
def detect_volume_change(prev_volume_list):
	try:
		''' A list of dictionary for each market 
			{ marketname:(basevolume, servertime, speed) } 
			'''
		curr_volume_list = {}
		m = user.w_get_api().get_market_summaries()
		marketsummaries = m.get("result")

		# get time:
		epoch = datetime(1970, 1, 1)
		
		for market in marketsummaries:
			#basevolume = market.get("BaseVolume")
			volume = market.get("BaseVolume")
			marketname = market.get("MarketName")
			timestamp = market.get("TimeStamp")  #'2017-08-14T15:03:14.013'
			try:
				pattern = '%Y-%m-%dT%H:%M:%S.%f'
				servertime = (datetime.strptime(timestamp, pattern) - epoch).total_seconds()
			except:
				pattern = '%Y-%m-%dT%H:%M:%S'
				servertime = (datetime.strptime(timestamp, pattern) - epoch).total_seconds()
		
			#print marketname, volume, servertime
			'''Calculate speed change due to previous status '''
			if (prev_volume_list):
				delta_volume = volume - prev_volume_list.get(marketname)[0]
				delta_time = servertime - prev_volume_list.get(marketname)[1]
				if (delta_time):
					speed = (delta_volume/volume)/(delta_time)
				else:
					speed = 0
			else:
				speed = 0
			curr_volume_list.update( {marketname: (volume, servertime, speed) })
		return curr_volume_list
		
	except Exception as e:
		print(e.message)
		print err_line_track()
		
			
def run_detect_volume_change(run_times, interval):
	prev_volume_list = {}
	i = 1
	while 1:
		curr_time = str(datetime.now())
		#print "round" , i
		prev_volume_list = detect_volume_change(prev_volume_list)
		#print prev_volume_list
		
		'''Check the max and min of market'''
		try:
			market_max, stat_max = max(prev_volume_list.iteritems(),key=lambda item:item[1][2])
			if (stat_max[2] > 0.01):
				print "Round", i, "__  Up __", curr_time, market_max, stat_max
			
			market_min, stat_min = min(prev_volume_list.iteritems(),key=lambda item:item[1][2])
			if (stat_min[2] < -0.01):
				print "Round", i, "__ Down__", curr_time, market_min, stat_min
		except Exception as e:
			print(e.message)
			print err_line_track()
			
		time.sleep(interval)
		
		if run_times == 1: #Run n times until reaching 1
			break;
		elif run_times == 0: #Run forever
			continue
		else:
			run_times -= 1
		i+=1

if __name__ == "__main__":
	#run_detect_round_change(0, 5)
	run_detect_volume_change(20000,1)
	
	