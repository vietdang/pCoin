from worker_marketanalysis import BittrexMarketAnalysisWorker

wk = BittrexMarketAnalysisWorker()

watchlist = [
	#"BTC-ETC",
	"BTC-NAV",
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
wk.run_detect_order_change(20000,1, watchlist)
