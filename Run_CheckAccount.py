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
print "Account balances"
totalBTC = 0
totalUSDT = 0
if m>=0:
	for c in m:
		btc_size = c.get("SizeBTC")
		totalBTC +=btc_size
		usdt_size = c.get("SizeUSDT")
		totalUSDT += usdt_size
		print "Coin: {:.6s}, Total: {:.10f}, Available: {:.10f}, BTC={:.10f}, USDT={:.10f} ".format( c.get("Currency"), c.get("Balance"), c.get("Available"), btc_size, usdt_size)
		
print "-------------------------------------------"
print "# Total: \t{:.10f} (BTC) ~ {:.10f} ($)".format(totalBTC, totalUSDT)
