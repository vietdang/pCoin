from worker_market import *

watchlist = [
	#"USDT-NEO", 
	"BTC-PAY",
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
run_detect_order_change(20000,1, watchlist)