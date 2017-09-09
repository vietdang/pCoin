from worker_buysell import BittrexBuySellWorker

try:
	import user
	key = user.key
	secret = user.secret
except:
	print "Cannot get accoutn"
	exit()
	


wk = BittrexBuySellWorker(key, secret)

m = wk.w_get_account_balances()
print "w_get_account_balances()"
if m:
	for c in m:
		print "Coin: {:.6s}, Total: {:.10f}, Available: {:.10f}".format( c.get("Currency"), c.get("Balance"), c.get("Available"))


		
coin = "BTC"
print "w_get_coin_available_balance(\"{}\"):".format(coin)
available = wk.w_get_coin_available_balance(coin)
total = wk.w_get_coin_total_balance(coin)
print "Coin: {:.6s}, Total: {:.10f}, Available: {:.10f}".format(coin,total,available)
