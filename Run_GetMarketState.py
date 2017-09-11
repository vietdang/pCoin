from worker_marketanalysis import BittrexMarketAnalysisWorker

wk = BittrexMarketAnalysisWorker()
market = "all"
# market = raw_input("Please enter your market: (or type: all) ")

if market == "all":
	watchlist = wk.market_list
else:
	watchlist =[market]

wk.get_market_state(watchlist)
