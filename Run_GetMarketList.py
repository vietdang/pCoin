from worker_marketanalysis import BittrexMarketAnalysisWorker

wk = BittrexMarketAnalysisWorker()

wk.run_check_market_list("market_list.txt")
