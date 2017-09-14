# Before run this file need install and run the following items. 
# 1. MongoDB: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/
# 2. pymongo: http://api.mongodb.com/python/current/installation.html?_ga=2.136188276.453062380.1505352094-1101017367.1505352094
import pymongo
from pymongo import MongoClient
from worker_marketanalysis import BittrexMarketAnalysisWorker
from datetime import datetime
import time

client_mongo = MongoClient('mongodb://localhost:27017/')
database_mongo = client_mongo['BittrexData']        # Select database with name "CryptoCoin". It's created if it's not existing.
collection_mongo = database_mongo["BTC-ETH"]        # Select collection with name "BittrexData". It's created if it's not existing.



analyst = BittrexMarketAnalysisWorker()
# Get and save data to mongodb
while 1: 
        curr_time = str(datetime.now())
        m = analyst.get_market_summaries()
        marketsummaries = m.get("result")
        for market in marketsummaries:
                marketname = market.get("MarketName")
                collection_mongo = database_mongo[marketname]
                res = collection_mongo.insert(market)
        print "Collect and save Bittrex data at {}".format(curr_time)
        time.sleep(4.4)

        # Get data
        # collection_mongo = database_mongo["BTC-ADX"]
        # for item in collection_mongo.find():
        #         print item
