from worker_marketanalysis import BittrexMarketAnalysisWorker

wk = BittrexMarketAnalysisWorker()

market = raw_input("Please enter your market: (or type: all) ")

if market == "all":
	watchlist = [
	#"BTC-ETC",
	#"BTC-NAV",
	#"BTC-QTUM",
	#"USDT-NEO", 
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
else:
	watchlist =[market]

wk.run_detect_order_change(20000,1, watchlist)
