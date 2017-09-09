from worker_buysell import BittrexBuySellWorker
from worker_marketanalysis import BittrexMarketAnalysisWorker
from datetime import datetime
from utilities import ERROR
import time

try:
	import user
	key = user.key
	secret = user.secret
except:
	key = None
	secret = None

	
print "key, secret",key, secret

buysell_Wk = BittrexBuySellWorker(key, secret)

def test_order_buy_sell():
	print "Local Time: " + str(datetime.now())
	v =  buysell_Wk.w_get_coin_available_balance("BTC")
	p = buysell_Wk.w_get_price("BTC-XMR", "Bid")
	p = 0.5*p  #Test timeout by buying with very low price
	#print p, v
	r = buysell_Wk.w_order_buy_sell("BTC","XMR", v, p, 3 )
	#r = buysell_Wk.w_order_buy_sell("XMR","BTC", v, p, 3)
	if (r < 0): #Error
		print r 
		if r == ERROR.TIME_OUT:
			#retry with actual price
			print "Test order TIME_OUT ok"
		else:
			print "Test order TIME_OUT fail"
			
	uuid = buysell_Wk.w_order_buy_sell("BTC","XMR", v, p, 3 , False)
	#market, _ = buysell_Wk.w_get_market_name("BTC","XMR")
	#r = buysell_Wk.w_get_open_order(market)
	#print buysell_Wk.w_cancel_order(r[0])
	print uuid
	print buysell_Wk.w_cancel_order(uuid)
	
def test_get_price_by_value():
	market = "BTC-CURE"
	print "Market {}".format(market)
	v = 30
	type = "Ask"
	p0 = p = buysell_Wk.w_get_price(market, type)
	p = buysell_Wk.w_get_price(market, type, v)
	print "{} price={:06.9f}  - Final price ={:06.9f} - value={:06.9f}".format(type, p0, p, v)
	
	v = 2000
	type = "Ask"
	p0 = buysell_Wk.w_get_price(market, type)
	p = buysell_Wk.w_get_price(market, type, v)
	print "{} price={:06.9f}  - Final price ={:06.9f} - value={:06.9f}".format(type, p0, p, v)
	
	v = 2000
	type = "Bid"
	p0 = buysell_Wk.w_get_price(market, type)
	p = buysell_Wk.w_get_price(market, type, v)
	print "{} price={:06.9f}  - Final price ={:06.9f} - value={:06.9f}".format(type, p0, p, v)
	
	
def MAIN():
	test_order_buy_sell()
	test_get_price_by_value()
	
	
if __name__ == "__main__":
	MAIN()