from bittrex import Bittrex
from buysell_worker import BittrexBuysellWorker
from datetime import datetime
from error_handle import ERROR
import time

try:
	import user
	key = user.key
	secret = user.secret
except:
	key = None
	secret = None
	
print key, secret

user = BittrexBuysellWorker(key, secret)

def test_order_buy_sell():
	print "Local Time: " + str(datetime.now())
	v =  user.w_get_balance("BTC")
	p = user.w_get_price("BTC-XMR", "Bid")
	p = 0.5*p  #Test timeout by buying with very low price
	#print p, v
	r = user.w_order_buy_sell("BTC","XMR", v, p, 3 )
	#r = user.w_order_buy_sell("XMR","BTC", v, p, 3)
	if (r < 0): #Error
		print r 
		if r == ERROR.TIME_OUT:
			#retry with actual price
			print "Test order TIME_OUT ok"
		else:
			print "Test order TIME_OUT fail"
			
	uuid = user.w_order_buy_sell("BTC","XMR", v, p, 3 , False)
	#market, _ = user.w_get_market_name("BTC","XMR")
	#r = user.w_get_open_order(market)
	#print user.w_cancel_order(r[0])
	print uuid
	print user.w_cancel_order(uuid)
	
def test_get_price_by_value():
	market = "BTC-CURE"
	print "Market {}".format(market)
	v = 30
	type = "Ask"
	p0 = p = user.w_get_price(market, type)
	p = user.w_get_price(market, type, v)
	print "{} price={:06.9f}  - Final price ={:06.9f} - value={:06.9f}".format(type, p0, p, v)
	
	v = 2000
	type = "Ask"
	p0 = user.w_get_price(market, type)
	p = user.w_get_price(market, type, v)
	print "{} price={:06.9f}  - Final price ={:06.9f} - value={:06.9f}".format(type, p0, p, v)
	
	v = 2000
	type = "Bid"
	p0 = user.w_get_price(market, type)
	p = user.w_get_price(market, type, v)
	print "{} price={:06.9f}  - Final price ={:06.9f} - value={:06.9f}".format(type, p0, p, v)
	
	
def MAIN():
	#test_order_buy_sell()
	test_get_price_by_value()
	
	
if __name__ == "__main__":
	MAIN()