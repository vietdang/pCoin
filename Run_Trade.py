from worker_buysell import BittrexBuySellWorker
from worker_marketanalysis import BittrexMarketAnalysisWorker
from utilities import ERROR

try:
	import user
	key = user.key
	secret = user.secret
	
except:
	print "Cannot get account"
	exit()
	
print "Begin Trade"
bs_wk = BittrexBuySellWorker(key, secret)
ma_wk = BittrexMarketAnalysisWorker()

	
def buy_sell_manual():
	bs_wk.w_display_account_balances()
	'''Ask user put input coin'''
	coin_src = raw_input("Please input source coin: ").upper()
	coin_des = raw_input("Please input destination coin: ").upper()
	'''Show current coin balance'''
	bs_wk.w_display_coin_balances(coin_src)
	market, ordertype = ma_wk.w_get_market_name(coin_src, coin_des)
	'''Show current price and market parameters'''
	ma_wk.w_display_market_summary(market)
	'''Ask user value to buy '''
	while 1:
		value = raw_input(("How much {} do you want to spend? (all, half, <YourNumber>): ").format(coin_src)).lower()		
		if value=="all":
			value = bs_wk.w_get_coin_available_balance(coin_src)
			break
		elif value == "half":
			value = bs_wk.w_get_coin_available_balance(coin_src)/2
			break
		else: #it's must be a number
			try:
				value = float(value)
				break
			except:
				value = 0
				
	value_des_before = bs_wk.w_get_coin_available_balance(coin_des)
	'''Ask user price to buy '''
	while 1:
		buy_price = raw_input( "Which buy_price? Ask/Bid/Last/<YourNumber>: ").lower()
		if buy_price == "ask" or buy_price == "bid" or buy_price == "last":
			buy_price = bs_wk.w_get_price(market,buy_price, value )
			break
		else:
			try:
				buy_price = float(buy_price)
				break
			except:
				buy_price = 0
				
	'''Ask user price to sell '''
	while 1:
		sell_price = raw_input( "Which sell_price? Ask/Bid/Last/<YourNumber>: ").lower()
		if sell_price == "ask" or sell_price == "bid" or sell_price == "last":
			sell_price = bs_wk.w_get_price(market,sell_price, value )
			break
		else:
			try:
				sell_price = float(sell_price)
				break
			except:
				sell_price = 0
				
				
	res = bs_wk.w_order_buy_sell(coin_src, coin_des, value, buy_price, 5*60*60, True) #wait for 5 hours
	
	if res == ERROR.TIME_OUT:
		print "Cannot buy because of TIME_OUT"
		exit()
		
	value_des_after =  bs_wk.w_get_coin_available_balance(coin_des)
	value_des = value_des_after - value_des_before
	
	if value_des == 0:
		print "Error, value_des_after == value_des_before"
		exit()
	
	
	res = bs_wk.w_order_buy_sell(coin_des, coin_src, value_des, sell_price, 5*60*60, False)
	if res == ERROR.TIME_OUT:
		print "Cannot buy because of TIME_OUT"
		exit()
	else:
		print "Congratulation. Buy/sell successful"
		
	
	bs_wk.w_display_coin_balances(coin_src)
	
def quick_trade():

	market = "BTC-STRAT"
	coin_src , coin_des = bs_wk.w_get_market_name()
	res = bs_wk.w_get_coin_available_balance(coin_src)
	
if __name__ == "__main__":
	buy_sell_manual()
	
