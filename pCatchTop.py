from bittrex import Bittrex
import ast
import traceback
import operator
import time
import inspect
from datetime import datetime

#print "test"
RUN_RELEASE = 1
if (RUN_RELEASE == 0):
	RUN_TEST = 1
else:
	RUN_TEST = 0
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
	print marketsummaries[0].get("TimeStamp")
	print "Local Time: " + str(datetime.now())
	print 'Coin\tr\tcw1\tccw1\tcw2\tccw2'
	path =[]
	for XXX in UsdtCoin:
		try:
			if XXX is "BTC":
				continue
			
			[(usdt_xxx_ask, usdt_xxx_last, usdt_xxx_bid )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'USDT-'+XXX ] 
			[(usdt_btc_ask, usdt_btc_last, usdt_btc_bid )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'USDT-BTC' ]
			[(btc_xxx_ask, btc_xxx_last, btc_xxx_bid	)]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'BTC-'+XXX ]
			
			[(usdt_eth_ask, usdt_eth_last, usdt_eth_bid )]  = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'USDT-ETH' ]
			if (XXX != "ETH"):
				[(eth_xxx_ask, eth_xxx_last, eth_xxx_bid )] = [(d.get("Ask"),d.get("Last"),d.get("Bid")) for d in marketsummaries if d['MarketName'] == 'ETH-'+XXX ]
			else:
				eth_xxx_ask = eth_xxx_last = eth_xxx_bid = 1
			#print type(usdt_btc)
			#print usdt_btc
			''' note: 
			cw1 clockwise		:  usdt -> btc -> xxx -> usdt
			ccw1 counterclockwise:  usdt -> xxx -> btc -> usdt
			cw2 clockwise		:  usdt -> eth -> xxx -> usdt
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
			print '{}\t{}\t{}\t{}\t{}\t{}'.format(XXX, r, cw1, ccw1, cw2, ccw2)
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
	print path	
	index, value = max(enumerate(path), key=operator.itemgetter(1))
	print index, value
	return value

def get_current_money(coin):
	return currCoin
	

def get_route(path):
	''' note: 
	cw1 clockwise		:  usdt -> btc -> xxx -> usdt
	ccw1 counterclockwise:  usdt -> xxx -> btc -> usdt
	cw2 clockwise		:  usdt -> eth -> xxx -> usdt
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
	
def order_sell(c1, c2, v):
	order_ok = 1
	if (v>0):		
		balance_prev = get_available_balance(c2) #return new balance if sold
		try:
			#buy
			p = api.get_marketsummary(c1+"-"+c2).get("result")[0].get("Last")
			#p = api.get_marketsummary(c1+"-"+c2).get("result")[0].get("Ask")
			pair = c1+"-"+c2
			print "from {} {} buy {} at price {}".format(v, c1, c2, p)
			#print v/p
			while 1:
				u =  api.buy_limit(pair, v/p*EXCHANGE_RATE, p)
				#print u
				#print v/p
				if u.get("message") == "INSUFFICIENT_FUNDS":
					v = v*0.9999
					print("Retry buy with {}".format(v))
				else:
					print "Balance Prev: {}. Line: {}".format(balance_prev, lineno())
					while 1:
						balance_after = get_available_balance(c2) #return new balance if sold
						print "Balance After: {}".format(balance_after)
						if (balance_after != balance_prev):
							break
					break
				#time.sleep(2)
			p = 1/p #for simulation
		except:
			try:
			#sell
				#p = api.get_marketsummary(c2+"-"+c1).get("result")[0].get("Last")
				p1 = api.get_marketsummary(c2+"-"+c1).get("result")[0].get("Bid")
				p2 = api.get_marketsummary(c2+"-"+c1).get("result")[0].get("Ask")
				#p = (p1+p2)/2
				p =  p1
				pair = c2+"-"+c1
				print "from {} {} sell {} at price {}".format(v, c1, c2, p)
				while 1:
					u = api.sell_limit(pair, v, p)
					#print u
					if u.get("message") == "INSUFFICIENT_FUNDS":
						v = v*0.9999
						print("Retry sell with {}".format(v))
					else:
						print "Balance Prev: {}. Line: {}".format(balance_prev, lineno())
						while 1:
							balance_after = get_available_balance(c2) #return new balance if sold
							print "Balance After: {}".format(balance_after)
							if (balance_after != balance_prev):
								break
						break
					#time.sleep(2)
				
			except:
				p = 0
				print "Error cannot get price"
		if (pair):
			print p, pair
			if (u):
				#print u
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
				time.sleep(1)
				t = get_available_balance(c2) #return new balance if sold
			if (key != None):
				return t				
			else:
				return v * p * EXCHANGE_RATE	
	return 0
		
def get_available_balance(coin):
	if key != None:
		m = api.get_balance(coin)
		print m
		v = m.get("result").get("Balance")
		if (v):
			return v
		else:
			print("Cannot get {} balance".format(coin))
			return 0
	#else:
		#return currCoin

		
def get_price(coin1, coin2, type):
	try:
		m = api.get_marketsummary(coin1+"-"+coin2)
		#print m 
		price = m.get("result")[0].get(type)
	except:
		try:
			m = api.get_marketsummary(coin2+"-"+coin1)
			#print m 
			price = m.get("result")[0].get(type)
		except:
			print m
			price = 0
	return price
	
def wait_top(coin_top, coin_base, wait_wave_num):
	#compare 3 times, if drop, this is the top, need to sell immediately
	count_price_drop = 0;
	price_prev = get_price(coin_top, coin_base, "Bid");
	while 1:
		price_current = get_price(coin_top, coin_base, "Bid")
		change_rate = 0;
		if(price_prev!=0):
			change_rate = 100*(price_current-price_prev)/price_prev
		
		print "{} Current Price: {}, Change rate: {}".format(str(datetime.now()), price_current, change_rate)
		if(change_rate < 0):
			count_price_drop = count_price_drop + 1
			if (count_price_drop > wait_wave_num):
				break
		price_prev = price_current

def wait_descrease_wave(coin_top, coin_base, wait_wave_num, interval):
	#compare 3 times, if drop, this is the top, need to sell immediately
	count_price_drop = wait_wave_num;
	price_prev = get_price(coin_top, coin_base, "Bid");
	while 1:
		price_current = get_price(coin_top, coin_base, "Bid")
		change_rate = 0;
		if(price_prev!=0):
			change_rate = 100*(price_current-price_prev)/price_prev
		
		print "{} Current Price: {}, Change rate: {}, remain wait time: {}".format(str(datetime.now()), price_current, change_rate, count_price_drop)
		if(change_rate < 0):
			count_price_drop = count_price_drop - 1
			if (count_price_drop < 1):
				break
		price_prev = price_current
		if (interval != 0):
			# Wait interval (s)
			time.sleep(interval)
		
def func_buy_sell_limit(coin_src, coin_target, size, price):
	try:
		#buy
		#only check
		p = api.get_marketsummary(coin_src+"-"+coin_target).get("result")[0].get("Last")
		market = coin_src + "-" + coin_target
		
		#print v/p
		while 1:
			if (RUN_TEST):
				var = raw_input("Please enter 'b' to buy: ")
				if (var != 'b'):
					continue
			u =  api.buy_limit(market, size/price*EXCHANGE_RATE, price)
			print "from {} {} buy {} at price {}. Line {}".format(size, coin_src, coin_target, price, lineno())
			print u
			#print v/p
			if u.get("message") == "INSUFFICIENT_FUNDS":
				size = size*0.9999
				print("Retry buy with {}".format(size))
			else:
				break
	except:
		try:
		#sell
			market = coin_target + "-" + coin_src
			while 1:
				if (RUN_TEST):
					var = raw_input("Please enter 's' to sell: ")
					if (var != 's'):
						continue
				u = api.sell_limit(market, size, price)
				print "from {} {} sell {} at price {}. Line {}".format(size, coin_src, coin_target, price, lineno())
				print u
				if u.get("message") == "INSUFFICIENT_FUNDS":
					size = size*0.9999
					print("Retry sell with {}".format(size))
				else:
					break			
		except:
			print "Error cannot get price"
	print "Exit func_buy_sell_limit"

def is_trade_order_success(coin_src, coin_target, size, price, timeout_ms):
	market=coin_src + '-' + coin_target
	balance_prev = get_available_balance(coin_target)
	print "Order and wait to success: {}-{}, size {}, price {}, timeout {}, balance_prev {}".format(coin_src, coin_target, size, price, timeout_ms, balance_prev)

	u = func_buy_sell_limit(coin_src, coin_target, size, price)
	print u
	
	print "Wait completing order..."
	while 1:
		#check balance to confirm successfully
		#TODO: get balance
		balance_current = get_available_balance(coin_target)
		if(balance_current != balance_prev):
			print "Order success: Pre {} -> Cur {} ".format(balance_prev, balance_current)
			return 1 #success
		#check timeout
	print "Order failed"
	return 0 #fail
def func_surf_wave(coin_src, coin_target):
		
	#get size
	size = get_available_balance(coin_src)
	print "Balance: {}".format(size)
	#input pump coin
	coin_target = raw_input("Pump coin: ")
	while 1:
		#get price ask
		price_ask = get_price(coin_src, coin_target, "Ask")
		
		price = price_ask
		#buy
		if (is_trade_order_success(coin_src, coin_target, size, price, 2000)):
			break
	#wait top
	wait_top(coin_target, coin_src,1)
	
	#get size
	size = get_available_balance(coin_target)
	#sell
	while 1:
		#get price bid
		price_bid = get_price(coin_src, coin_target, "Bid")
		
		price = price_bid
		#sell
		if (is_trade_order_success(coin_target, coin_src, size, price, 2000)):
			break
	
	#wait top
	wait_top(coin_target, coin_src, 10)
def func_pump_wave(coin_src):
			
	#get size
	size = get_available_balance(coin_src)
	print "Balance: {}".format(size)
	#input pump coin
	coin_target = raw_input("Pump coin: ")
	print "{} Execute buy/sell coin: {} - {}".format(str(datetime.now()), coin_src, coin_target)
	while 1:
		#get price ask
		price_ask = get_price(coin_src, coin_target, "Ask")
		
		price = price_ask
		#buy
		if (is_trade_order_success(coin_src, coin_target, size, price, 2000)):
			break
	#wait top
	wait_descrease_wave(coin_target, coin_src, 1, 0)
	
	#get size
	size = get_available_balance(coin_target)
	#sell
	while 1:
		#get price bid
		price_bid = get_price(coin_src, coin_target, "Bid")
		
		price = price_bid
		#sell
		if (is_trade_order_success(coin_target, coin_src, size, price, 2000)):
			break
	
	#wait top
	wait_descrease_wave(coin_target, coin_src, 10, 1)
def main_surf_top():
	#parse params
	coin_src = "BTC"
	#coin_target = "LTC"
	#print "Start with {}-{}".format(coin_src, coin_target)
	if (RUN_TEST):
		var = raw_input("Please enter Y/N to start/stop: ")
		if (var == 'y'):
			print "Wait 2 seconds to confirm...^_^"
			time.sleep(2)
		else:
			print "STOP"
			return 0
	#func_surf_wave(coin_src, coin_target)
	func_pump_wave(coin_src)
def func_calc_diff():

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
			print "----------------------------------"
			profit = bestpath[0]
			if profit > biggest:
				biggest = profit
			if profit > 1:
				count_1 +=1
				
			if profit > 1.003: 
				count += 1
				
				print "{} Buy this round - Total rounds: {} - Profit: {} - Biggest profit: {} - Count of >1: {}".format(currCoin,count,profit,biggest,count_1)
				
				break
			else:
				print "{} Skip this round - Total rounds: {} - Profit: {} - Biggest profit: {} - Count of >1: {}".format(currCoin,count,profit,biggest,count_1)
				time.sleep(10)
		
		
		route = get_route(bestpath)
		print route
		
		print '{} {}'.format(currCoin,route[0])
		currCoin = get_available_balance(route[0])
		print currCoin
		
		if (currCoin>20):
			print("Quit! Enough money. Stop trading. Current balance: {}".format(currCoin))
			quit()
		elif (currCoin <11.0):
			print("Warning! Stop trading. Current balance: {}".format(currCoin))
			quit()
		
		currCoin = order_sell(route[0], route[1], currCoin)
		
		print '{} {}'.format(currCoin,route[1])
		#time.sleep(5)
		currCoin = order_sell(route[1], route[2], currCoin)
		print '{} {}'.format(currCoin,route[2])
		#time.sleep(5)
		currCoin = order_sell(route[2], route[3], currCoin)
		print '{} {}'.format(currCoin,route[3])
		
		#time.sleep(5)
def wait_reach_percent(coin_top, coin_base, price, percent):
	#compare price follow percent
	while 1:
		price_current = get_price(coin_top, coin_base, "Bid")
		percent_current = (abs(price_current - price) * 100) / price
		print "Current Price: {}. Percent: {}".format(price_current, percent_current)
		if(percent_current >= percent):
			break
	
def main_catch_percent():
	#parse params
	coin_src = "USDT"
	coin_target = "LTC"
	percent = 40
	print "Start with {}-{}".format(coin_src, coin_target)
	if (RUN_TEST):
		var = raw_input("Please enter Y/N to start/stop: ")
		if (var == 'y'):
			print "Wait 2 seconds to confirm...^_^"
			time.sleep(2)
		else:
			print "STOP"
			return 0	
		
	#get size
	size = get_available_balance(coin_src)
	print "Balance: {}".format(size)
	
	while 1:
		#get price ask
		price_ask = get_price(coin_src, coin_target, "Ask")
		
		price = price_ask
		#buy
		if (is_trade_order_success(coin_src, coin_target, size, price, 2000)):
			break
	#wait reach percent
	wait_reach_percent(coin_target, coin_src, price, percent)
	
	#get size
	size = get_available_balance(coin_target)
	#sell
	while 1:
		#get price bid
		price_bid = get_price(coin_src, coin_target, "Bid")
		
		price = price_bid
		#sell
		if (is_trade_order_success(coin_target, coin_src, size, price, 2000)):
			break
			

def MAIN():
	#print get_price("BTC", "XMR", "Ask")
	main_surf_top()
	#main_catch_percent()

print "test"
if __name__ == "__main__":
	MAIN()
