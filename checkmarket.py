from bittrex import Bittrex
import ast
import traceback
import operator
import time
import inspect
from datetime import datetime
try:
	import user
	key = user.key
	secret = user.secret
except:
	key = None
	secret = None

UsdtCoin =[
"BCC",
"BTC",
"DASH",
"ETC",
"ETH",
"LTC",
"NEO",
"XMR",
"XRP",
"ZEC",
]

EXCHANGE_RATE = 0.9975

print key, secret
api = Bittrex(key,secret)
data = api.get_markets()

money = 100

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno
	
def get_new_round():
	''' Need return buying path . Currently only use static path
	meaning keep going this path regarding the current price
	'''
	marketsummaries = api.get_market_summaries().get("result")
	#print marketsummaries[0].get("TimeStamp")
	print "Local Time: " + str(datetime.now())
	#print 'Coin\tr\tcw1\tccw1\tcw2\tccw2'
	path =[]
	for XXX in UsdtCoin:
		try:
			if XXX is "BTC":
				continue
			
			[(usdt_xxx_ask, usdt_xxx_last, usdt_xxx_bid )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'USDT-'+XXX ] 
			[(usdt_btc_ask, usdt_btc_last, usdt_btc_bid )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'USDT-BTC' ]
			[(btc_xxx_ask, btc_xxx_last, btc_xxx_bid    )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'BTC-'+XXX ]
			
			[(usdt_eth_ask, usdt_eth_last, usdt_eth_bid )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'USDT-ETH' ]
			if (XXX != "ETH"):
				[(eth_xxx_ask, eth_xxx_last, eth_xxx_bid )] = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'ETH-'+XXX ]
			else:
				eth_xxx_ask = eth_xxx_last = eth_xxx_bid = 1
			#print type(usdt_btc)
			#print usdt_btc
			''' note: 
			cw1 clockwise        :  usdt -> btc -> xxx -> usdt
			ccw1 counterclockwise:  usdt -> xxx -> btc -> usdt
			cw2 clockwise        :  usdt -> eth -> xxx -> usdt
			ccw2 counterclockwise:  usdt -> xxx -> eth -> usdt
			'''
			#use Last as conditions
			#usdt_xxx_ask = usdt_xxx_bid = usdt_xxx_last
			#usdt_btc_ask = usdt_btc_bid = usdt_btc_last
			#btc_xxx_ask  = btc_xxx_bid  = btc_xxx_last
			#usdt_eth_ask = usdt_eth_bid = usdt_eth_last
			#eth_xxx_ask  = eth_xxx_bid  = eth_xxx_last
			
			
			cw1 = ((usdt_xxx_bid/usdt_btc_ask)/btc_xxx_ask) *  EXCHANGE_RATE * EXCHANGE_RATE * EXCHANGE_RATE
			ccw1 = (usdt_btc_bid / usdt_xxx_ask )* btc_xxx_bid  *  EXCHANGE_RATE * EXCHANGE_RATE * EXCHANGE_RATE
			
			cw2 = ((usdt_xxx_bid /usdt_eth_ask)/eth_xxx_ask )*  EXCHANGE_RATE * EXCHANGE_RATE * EXCHANGE_RATE
			ccw2 = (usdt_eth_bid / usdt_xxx_ask) * eth_xxx_bid  *  EXCHANGE_RATE * EXCHANGE_RATE * EXCHANGE_RATE
			
			r = max(cw1, ccw1, cw2, ccw2)
			#print '{}\t{}\t{}\t{}\t{}\t{}'.format(XXX, r, cw1, ccw1, cw2, ccw2)
			if r == cw1:
				s = "cw1"
			elif r == ccw1:
				s = "ccw1"
			elif r == cw2:
				s = "cw2"
			else:
				s = "ccw2"
			path.append((r,XXX,s)) #add current best
		except:
			print "Error: "+  XXX
			traceback.print_exc()
			pass
	#print path	
	index, value = max(enumerate(path), key=operator.itemgetter(1))
	#print index, value
	return value

def get_current_money(coin):
	return currCoin
	

def get_route(path):
	''' note: 
	cw1 clockwise        :  usdt -> btc -> xxx -> usdt
	ccw1 counterclockwise:  usdt -> xxx -> btc -> usdt
	cw2 clockwise        :  usdt -> eth -> xxx -> usdt
	ccw2 counterclockwise:  usdt -> xxx -> eth -> usdt
	'''
	if (path[0] > 1): #only process if profit is greater than 1
		if (path[2] == "cw1"):
			route = ("USDT", "BTC", path[1], "USDT")
		elif (path[2] == "ccw1"):
			route = ("USDT", path[1], "BTC", "USDT")
		elif (path[2] == "cw2"):
			route = ("USDT", "ETH", path[1], "USDT")
		elif (path[2] == "ccw2"):
			route = ("USDT", path[1], "ETH", "USDT")
		else:
			print "Error no path"
			return	
		return route
	return None
	
def order_buy_sell(c1, c2, v):
	order_ok = 0
	if (v>0):		
		balance_prev = get_available_balance(c2) #return new balance if sold
		try:
			#buy
			p_bid  = api.get_marketsummary(c1+"-"+c2).get("result")[0].get("Bid")
			p_last = api.get_marketsummary(c1+"-"+c2).get("result")[0].get("Last")
			p_ask  = api.get_marketsummary(c1+"-"+c2).get("result")[0].get("Ask")
			price =[p_bid, (p_bid + p_ask)/2 , p_last, p_ask]
			i =0
			p = price[i]
			pair = c1+"-"+c2
			print "from {} {} buy {} at price {}".format(v, c1, c2, p)
			#print v/p
			while not order_ok:
				u =  api.buy_limit(pair, v/p*EXCHANGE_RATE, p)
				print u
				#print v/p
				if u.get("message") == "INSUFFICIENT_FUNDS":
					v = v*0.99
					print("Retry buy with {}".format(v))
				else:
					uuid = u.get("result").get("uuid")
					print "Balance Prev: {}. Line: {}".format(balance_prev, lineno())
					retry = 0
					while 1:
						try:
							balance_after = get_available_balance(c2) #return new balance if sold
							print "Balance After: {}".format(balance_after)
						except:
							print "cannot get balance now"
							pass
						
						time.sleep(1)
						retry +=1
						m = api.get_order(uuid)
						#print m
						wait = m.get("result").get("IsOpen")
						if not wait:
							order_ok = 1
							break
						if (retry > 10):
							retry = 0
							i+=1
							if (i>=3):
								i = 3
							p = price[i]
							api.cancel(uuid)
							break
					
				#time.sleep(2)
			p = 1/p #for simulation
		except:
			try:
			#sell
				
				p_bid  = api.get_marketsummary(c2+"-"+c1).get("result")[0].get("Bid")
				p_last = api.get_marketsummary(c2+"-"+c1).get("result")[0].get("Last")
				p_ask  = api.get_marketsummary(c2+"-"+c1).get("result")[0].get("Ask")
				price =[p_ask, (p_bid + p_ask)/2 , p_last, p_bid]
				i =0
				p = price[i]
				pair = c2+"-"+c1
				print "from {} {} sell {} at price {}".format(v, c1, c2, p)
				while not order_ok:
					u = api.sell_limit(pair, v, p)
					print u
					if u.get("message") == "INSUFFICIENT_FUNDS":
						v = v*0.99
						print("Retry sell with {}".format(v))
					else:
						uuid = u.get("result").get("uuid")
						print "Balance Prev: {}. Line: {}".format(balance_prev, lineno())
						retry = 0
						while 1:
							try:
								balance_after = get_available_balance(c2) #return new balance if sold
							except:
								print "cannot get balance now"
								pass
							print "Balance After: {}".format(balance_after)
							time.sleep(1)
							retry +=1
							m = api.get_order(uuid)
							#print m
							wait = m.get("result").get("IsOpen")
							if not wait:
								order_ok = 1
								break
							if (retry > 10):
								retry = 0
								i+=1
								if (i>=3):
									i = 3
								p = price[i]
								api.cancel(uuid)
								break
						break
					#time.sleep(2)
				
			except:
				p = 0
				print "Error cannot get price"
		if (pair):
			print p, pair
			if (u):
				print "order result: {}".format(u)
				try:
					uuid = u.get("result").get("uuid")
					print uuid
					wait = 1
					while(wait):
						try:
							m = api.get_order(uuid)
							#print m
							wait = m.get("result").get("IsOpen")
							print "Waiting for completing order {} {} {}".format(pair,wait,uuid)
							if (wait):
								time.sleep(5)
						except:
							print "Loop in order"
							time.sleep(5)
							pass
				except:
					print "Buying/Selling failed"
					return 0
				wait = 1
				while wait:
					t = get_available_balance(c2) #return new balance if sold
					if abs((t -  v * p * EXCHANGE_RATE)/(v * p * EXCHANGE_RATE)<0.01):
						break
					print "Stuck in balance"
					time.sleep(2)
			if (key != None):
				return t				
			else:
				return v * p * EXCHANGE_RATE	
	return 0
		
def get_available_balance(coin):
	if key != None:
		m = api.get_balance(coin)
		print m
		if (m.get("success")):
			return m.get("result").get("Balance")
		else:
			print("Cannot get {} balance".format(coin))
			return 0
	else:
		return currCoin


currCoin = 10 #simulation if key = None
offsetCoin = 0
tradingAmount = 11
if key != None:
	currCoin = get_available_balance("USDT")
	
#currWallet = (bestpath[1], get_current_money(bestpath[1]))

#print currWallet
count = 0
biggest = 0
count_1 = 0
while 1:

	while 1:
		bestpath = get_new_round()
		
		profit = bestpath[0]
		if profit > biggest:
			biggest = profit
		if profit > 1:
			count_1 +=1
			
		if profit > 1.001: 
			count += 1
			print "----------------------------------"
			print "Local Time: " + str(datetime.now())
			print bestpath
			print "{} Buy this round - Total rounds: {} - Profit: {} - Biggest profit: {} - Count of >1: {}".format(currCoin,count,profit,biggest,count_1)
			
			break
		else:
			#print "{} Skip this round - Total rounds: {} - Profit: {} - Biggest profit: {} - Count of >1: {}".format(currCoin,count,profit,biggest,count_1)
			time.sleep(10)
	
	
	route = get_route(bestpath)
	print route
	
	print '{} {}'.format(currCoin,route[0])
	currCoin = get_available_balance(route[0])
	print currCoin
	
	if (currCoin>20):
		print("Quit! Enough money. Stop trading. Current balance: {}".format(currCoin))
		quit()
	elif (currCoin <10.5):
		print("Warning! Stop trading. Current balance: {}".format(currCoin))
		quit()
	
	#currCoin = order_buy_sell(route[0], route[1], currCoin)
	#
	#print '{} {}'.format(currCoin,route[1])
	##time.sleep(5)
	#currCoin = order_buy_sell(route[1], route[2], currCoin)
	#print '{} {}'.format(currCoin,route[2])
	##time.sleep(5)
	#currCoin = order_buy_sell(route[2], route[3], currCoin)
	#print '{} {}'.format(currCoin,route[3])
	
	#time.sleep(5)
	

