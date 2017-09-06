from bittrex import Bittrex
from worker_buysell import *
from datetime import datetime
from utilities import *
import operator
import time
import os 

'''Make sure get correct local time in Windows Cygwin platform '''

	
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
			
def detect_market_change(prev_marketsumaries_list, watchlist=[]):
	try:
		''' A list of dictionary for each market 
			{ marketname:(basevolume, servertime, speed, delta_time) } 
			'''
		curr_marketsumaries_list = {}
		m = user.w_get_api().get_market_summaries()
		marketsummaries = m.get("result")

		# get time:
		epoch = datetime(1970, 1, 1)
		
		for market in marketsummaries:
			marketname = market.get("MarketName")
			if watchlist and (marketname not in watchlist): #Only watch several coins. If watchlist is None then watch all coins
				continue
					
			#basevolume = market.get("BaseVolume")
			volume = market.get("BaseVolume")
			marketsize = market.get("Volume")
			
			timestamp = market.get("TimeStamp")  #'2017-08-14T15:03:14.013'
			p_ask = market.get("Ask")
			p_bid = market.get("Bid")
			p_last =market.get("Last")
			est_value = volume/marketsize
			try:
				pattern = '%Y-%m-%dT%H:%M:%S.%f'
				servertime = (datetime.strptime(timestamp, pattern) - epoch).total_seconds()
			except:
				pattern = '%Y-%m-%dT%H:%M:%S'
				servertime = (datetime.strptime(timestamp, pattern) - epoch).total_seconds()
		
			#print marketname, volume, servertime
			'''Calculate speed change due to previous status '''
			if (prev_marketsumaries_list):
				delta_volume = volume - prev_marketsumaries_list.get(marketname).get("BaseVolume")
				delta_time = servertime - prev_marketsumaries_list.get(marketname).get("ServerTime")
				delta_price = (p_bid - prev_marketsumaries_list.get(marketname).get("Bid"))/p_bid
				delta_order = (p_ask - p_bid)/p_ask
				if (delta_time != 0):
					speed = (delta_volume/volume)/(delta_time)
				else:
					speed = 0
			else:
				speed = 0
				delta_time = 0
				delta_price = 0
				delta_order = -1 #invalid value
			curr_marketsumaries_list.update( {marketname: {"BaseVolume":volume, 
													"ServerTime":servertime, 
													"VolumeSpeed":speed, 
													"DeltaTime":delta_time, 
													"Ask":p_ask, 
													"Bid":p_bid,
													"Last":p_last,
													"DeltaPrice":delta_price,
													"MarketSize":marketsize,
													"EstValue":est_value,
													"DeltaOrder":delta_order}})
		#print curr_marketsumaries_list
		return curr_marketsumaries_list
		
	except Exception as e:
		print(e.message)
		print "Error in line", err_line_track()
		
def run_detect_order_change(run_times, interval, watchlist=[]):
	marketsumaries_list = {}
	i = 1
	while 1:
		curr_time = str(datetime.now().time())
		''' Get prev and curr marketsummaries information '''
		marketsumaries_list = detect_market_change(marketsumaries_list,watchlist)

		
		try:
			''' Only check if satisfy condition '''
			if marketsumaries_list:
				for marketname, status in marketsumaries_list.items():
					#print m
					#print m.items()
					
					#print marketname
					delta_price = status.get("DeltaPrice") *100
					speed = status.get("VolumeSpeed")
					p_ask = status.get("Ask")
					p_bid = status.get("Bid")
					p_last = status.get("Last")
					deltatime = status.get("DeltaTime")
					est_value = status.get("EstValue")
					delta_order = status.get("DeltaOrder") *100
					change = (p_bid-est_value)
					change_percent = (p_bid-est_value)*100/est_value
					if speed != 0:
						change_volume_speed = change_percent/speed
					else:
						change_volume_speed = 0
					''' Analysis market status '''
					message =""
					
					if delta_price >0:
						message += "Up___"
					elif delta_price <0:
						message += "Down_"
					else:
						message += "Keep_"
						continue
						
					
					if delta_order < 0.1: #0.1%
						message += "Strong_"
					else:
						message += "_______"
						
					if abs(deltatime) <3:
						message += "Fast_"
					else:
						message += "____"
					deta_Est_last = est_value - p_last
					print("{}\t{}\t{}\tdBE={:.8f} ~ {:.2f}(%)\tdBid(%)={:.4f}\tBid={:.8f}\tEst={:.8f}\tdEL={:.8f}\tLast={:.8f}\tAsk={:.8f}\tdOrder={:.8f}\tdTime={:.2f}\tC/V={:.8f}"\
					.format(marketname, message, curr_time, change, change_percent, delta_price, p_bid, est_value, deta_Est_last, p_last, p_ask, delta_order,  deltatime, change_volume_speed))

		except Exception as e:
			print(e.message)
			print "Error in line", err_line_track()
			
		time.sleep(interval)
		
		if run_times == 1: #Run n times until reaching 1
			break;
		elif run_times == 0: #Run forever
			continue
		else:
			run_times -= 1
		i+=1
	
	
def run_detect_market_change(run_times, interval, watchlist=[]):
	#print "{ marketname:(basevolume, servertime, speed, delta_time, p_ask, delta_price_ask, marketsize) } "
	marketsumaries_list = {}
	i = 1
	while 1:
		if os.getenv("TZ"):
			os.unsetenv("TZ")
		curr_time = str(datetime.now())
		#print "round" , i
		marketsumaries_list = detect_market_change(marketsumaries_list,watchlist)
		#print marketsumaries_list
		
		'''Check the max and min of market
			{ marketname:(basevolume, servertime, speed, delta_time, p_ask, delta_price_ask, marketsize) } 
		'''
		market_change_list = []
		try:
			if marketsumaries_list:
				for marketname, status in marketsumaries_list.iteritems():					
					delta_time = status.get("DeltaTime")
					speed = status.get("VolumeSpeed")
					if (delta_time <= 20) and (speed > 0.00):
						market_change_list.append({marketname:status})
						
				if market_change_list:
					for m in market_change_list:
						#print m
						#print m.items()
						marketname, status =m.items()[0]
						#print marketname
						delta_price = status.get("DeltaPrice") *100
						speed = status.get("VolumeSpeed")
						p_ask = status.get("Ask")
						p_bid = status.get("Bid")
						p_last = status.get("Last")
						deltatime = status.get("DeltaTime")
						est_value = status.get("EstValue")
						message =""
						if delta_price > 1:
							message = "Up___Strong_"
						elif delta_price > 0:
							message = "Up__________"
						elif delta_price < -1:
							message = "Down_Strong_"
						elif delta_price < 0:
							message = "Down________"
						else:
							message = "Keep________"
						if abs(deltatime) <3:
							message += "Fast"
						else:
							message += "____"
						print "{}\t{}\t{}\tSpeed={:.8f}\tPriceChange(%)={:.8f}\tDeltaTime={:.2f}\tAsk={:.8f}\tBid={:.8f}\tLast={:.8f}\tEstValue={:.8f}\tChange={:.8f}".format(message, curr_time, marketname, speed, delta_price, deltatime, p_ask, p_bid, p_last,est_value, p_bid-est_value )
				#market_max, stat_max = max(marketsumaries_list.iteritems(),key=lambda item:item[1][2])
				#if (stat_max[2] > 0.01):
				#	print "Round", i, "__  Up __", curr_time, market_max, stat_max
				
				#market_min, stat_min = min(marketsumaries_list.iteritems(),key=lambda item:item[1][2])
				#if (stat_min[2] < -0.01):
				#	print "Round", i, "__ Down__", curr_time, market_min, stat_min
		except Exception as e:
			print(e.message)
			print "Error in line", err_line_track()
			
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
	watchlist = [
		"USDT-NEO", 
		#"BTC-OK",
		#"USDT-BCC",
		#"USDT-BTC",
		#"USDT-DASH",
		#"USDT-ETC",
		#"USDT-ETH",
		#"USDT-LTC",
		#"USDT-NEO",
		#"USDT-XMR",
		#"USDT-XRP",
		#"USDT-ZEC",
		]
	run_detect_market_change(20000,1, watchlist)
	
	