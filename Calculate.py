from worker_buysell import BittrexBuySellWorker
from worker_marketanalysis import BittrexMarketAnalysisWorker

from pymongo import MongoClient
#from config_market import MarketConfig
#from worker_marketanalysis import BittrexMarketAnalysisWorker
from datetime import datetime
from utilities import *
import time

analyst = BittrexMarketAnalysisWorker()
try:
	import user
	key = user.key
	secret = user.secret
except:
	print "Cannot get account"
	exit()
	
WINDOW_SIZE = 60
def calculate_best_trade(coin_src, coin_des, limitSellConditionPrice, limitBuyConditionPrice, fBufferRate, fOffsetRate, nConfirmBuy, nConfirmSell, maxsize = 9999, interval=1):
    client_mongo = MongoClient('mongodb://localhost:27017/')
    database_mongo = client_mongo['BittrexData']        # Select database with name "CryptoCoin". It's created if it's not existing.
    CFM_STEP = 3
    RJT_STEP = 1
    market, nextOrderType = analyst.w_get_market_name(coin_src, coin_des)
    print("fTopPrice, fTopConditionPrice, limitSellCon, fSellImmePrice, fBuyImmePrice, fBasePrice, fCurrentPrice, limitBuyCon, fBotConditionPrice, fBotPrice, fBufferValue, fOffsetValue, bBuySignal, bSellSignal,date,time")
    fCurrentPrice_List = []
    # Get data
    collection_mongo = database_mongo[market]
    firstMarketData = collection_mongo.find_one()
    fTopPrice = fBotPrice = firstMarketData.get("Last")
    nCfmSell = nConfirmSell*CFM_STEP
    nCfmBuy = nConfirmBuy*CFM_STEP
    STATE_SELL = 1
    STATE_BUY = 2
    nextState = STATE_SELL| STATE_BUY
    for marketInfo in collection_mongo.find():
        # In order to easy understand, definations of prices are described and sortder with descending order 
        # Base price:
        #	   * BasePrice = BaseVolume/Volume (Estimate price)
        # Values:
        #	   * BufferValue = fBufferRate*BasePrice
        #	   * OffsetValue = fOffsetRate*BasePrice
        # Price:
        #      * TopPrice: Maximum price in peak wave
        #      * TopConditionPrice =  TopPrice - BufferValue. 
        #      * TopTradePrice = TopConditionPrice - OffsetValue.    
        #      * SellImmePrice : Price is used to immediately sell a quantity coin .    
        #      * BasePrice (Estimate price)
        #      * BuyImmePrice : Price is used to immediately buy a quantity coin . 
        #      * BotTradePrice = BotConditionPrice + OffsetValue
        #      * BotConditionPrice =  BotPrice + BufferValue. 
        #      * BotPrice: Minimun price in bottom wave
        
        volume = marketInfo.get("BaseVolume")
        marketsize = marketInfo.get("Volume")
        fBasePrice = volume/marketsize #BasePrice (Estimate price)

        fBufferValue = fBasePrice*fBufferRate # BufferValue = fBufferRate*BasePrice
        fOffsetValue = fBasePrice*fOffsetRate	# OffsetValue = fOffsetRate*BasePrice (maybe unneccessary)
        
        fCurrentPrice = marketInfo.get("Last")
        fCurrentPrice_List.append(fCurrentPrice)
        if (len(fCurrentPrice_List) > WINDOW_SIZE):
            fCurrentPrice_List.pop(0)
        
        
        
        
        fTopPrice = max(fTopPrice,fCurrentPrice)
        #fTopConditionPrice = fTopPrice - fBufferValue
        '''fTopConditionPrice = (SMA60 -  2*SDTDEV + MaxPrice)/2 '''
        # fTopConditionPrice = (mean(fCurrentPrice_List) - 2*stddev(fCurrentPrice_List) + fTopPrice )/2
        fTopConditionPrice = (mean(fCurrentPrice_List) + fTopPrice )/2
        
        fTopTradePrice = fTopConditionPrice - fOffsetValue
        fSellImmePrice = marketInfo.get("Bid")
        fBuyImmePrice = marketInfo.get("Ask")
        fBotPrice = min(fBotPrice,fCurrentPrice)
        #fBotConditionPrice =  fBotPrice + fBufferValue
        '''fBotConditionPrice = (SMA60 +  2*SDTDEV + fBotPrice)/2 '''
        # fBotConditionPrice = (mean(fCurrentPrice_List) + 2*stddev(fCurrentPrice_List) + fBotPrice )/2
        fBotConditionPrice = (mean(fCurrentPrice_List) + fBotPrice )/2
        fUpper = mean(fCurrentPrice_List) + 2*stddev(fCurrentPrice_List)
        fLower = mean(fCurrentPrice_List) - 2*stddev(fCurrentPrice_List)
        
        fBotTradePrice = fBotConditionPrice + fOffsetValue

        
        
        # Check buy
        bBuySignal = False
        if (	(fCurrentPrice >  fBotConditionPrice) \
            and (nextState & STATE_BUY)
            and (fBuyImmePrice <  (limitBuyConditionPrice))):
            bBuySignal = True
        curr_time = marketInfo.get("TimeStamp")
        # Check sell
        bSellSignal = False
        if (	(fCurrentPrice <  fTopConditionPrice) \
            and (nextState & STATE_SELL)
            and (fSellImmePrice >  (limitSellConditionPrice))):
            bSellSignal = True
        # Cap nhat so lan xac nhan khi co tin hieu mua/ban
        # Sau so luong xac nhan thi no moi mua/ban
        if (bBuySignal == True):
            nCfmBuy -= CFM_STEP
        else:
           nCfmBuy = min(nConfirmBuy*CFM_STEP, nCfmBuy + RJT_STEP) 

        if (bSellSignal == True):
            nCfmSell -= CFM_STEP
        else:
            nCfmSell = min(nConfirmSell*CFM_STEP, nCfmSell + RJT_STEP)

        print"{:.8f}".format(fTopPrice),"{:.8f}".format( fTopConditionPrice),"{:.8f}".format( limitSellConditionPrice),\
                "{:.8f}".format( fSellImmePrice),"{:.8f}".format( fBuyImmePrice),"{:.8f}".format( fBasePrice),\
                "{:.8f}".format( fCurrentPrice),"{:.8f}".format( limitBuyConditionPrice),"{:.8f}".format( fBotConditionPrice),\
                "{:.8f}".format( fBotPrice),"{:.8f}".format( fBufferValue),"{:.8f}".format( fOffsetValue),\
                "{}".format( bBuySignal),"{}".format( bSellSignal),"{}".format( limitBuyConditionPrice),"{}".format( limitSellConditionPrice),\
                "{}".format(curr_time), nCfmBuy, nCfmSell

        if (nCfmBuy <= 0): ### BUY ###
            nCfmBuy = nConfirmBuy*CFM_STEP
            fBotPrice = fCurrentPrice # Reset
            # limitSellConditionPrice = fCurrentPrice/analyst.EXCHANGE_RATE
            limitSellConditionPrice = fUpper
            # limitSellConditionPrice = fBasePrice
            nextState = STATE_SELL
        if (nCfmSell <= 0):### SELL ###
            nCfmSell = nConfirmSell*CFM_STEP
            fTopPrice = fCurrentPrice # Reset
            # limitBuyConditionPrice = fCurrentPrice*analyst.EXCHANGE_RATE
            limitBuyConditionPrice = fLower
            # limitBuyConditionPrice = fBasePrice
            
            nextState = STATE_BUY

if __name__ == "__main__":
	#run_detect_round_change(0, 5)
	watchlist = [
		"USDT-NEO", 
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
	
	#Get pre-trade
	#auto_trade(20000,5, "BTC-KMD")
	#coin_src = "LMC"
	coin_src = "KMD"
	# coin_src = raw_input("Input SOURCE coin: ")
	coin_des = "BTC"
	# coin_des = raw_input("Input DEST coin: ")
	limitSellConditionPrice = 0.000509
	limitBuyConditionPrice = 0.000509

	fBufferRate = 0.01
	fOffsetRate = 0.001

	calculate_best_trade(coin_src, coin_des, limitSellConditionPrice, limitBuyConditionPrice, fBufferRate, fOffsetRate,9,9)
	
