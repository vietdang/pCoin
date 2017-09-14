from bittrex import Bittrex
from utilities import *


class BittrexExchange(Bittrex):
	def __init__(self, key = None, secret = None):
		self.EXCHANGE_RATE = 0.9975  # 0.25% for each trading transaction
		self.SELL_ORDER = "LIMIT_SELL"
		self.BUY_ORDER = "LIMIT_BUY"
		Bittrex.__init__(self,key,secret)
		
		#Get market list
		try:
			m = self.get_market_summaries()
			#print m
			market_list = []
			for market in m.get("result"):
				market_list.append(market.get("MarketName"))
			#print market_list
		except:
			print "Error: Cannot get market summaries"
			exit(1)
		self.market_list = market_list
		self.coin_list = []
		#get coin list
		for m in self.market_list:
			c1, c2  = self.w_extract_market_name(m)
			if c2 not in self.coin_list:
				self.coin_list.append(c2)
				
	def w_extract_market_name(self,market):
		"""
		Extract market name "USDT-XMR" to ("USDT","XMR)
		"""
		return market.split("-")
		
	def w_get_market_list(self):
		"""
		Get Market name list
		:return: market name list
		:rtype : list
		"""
		return self.market_list
		
	def w_get_coin_list(self):
		"""
		Get Coins name list
		:return: coins name list
		:rtype : list
		"""
		return self.coin_list
		
	def w_get_market_name(self, coin1, coin2, err_print_en = True):
		"""
		Get marketname for pair of coins
		:param coin1: String literal for coin 1 (ex: USDT)
		:param coin2: String literal for coin 2 (ex: XMR)
		:param err_print_en: enable print error
		:return: (MarketName, BUY_ORDER/SELL_ORDER) 
		:rtype : str
		"""
		market = coin1 + "-" + coin2
		if market in self.market_list:
			return (market, self.BUY_ORDER)
		else:
			market = coin2 + "-" + coin1
			if market in self.market_list:
				return (market, self.SELL_ORDER)
			else:
				#Don't print error for specific purpose: Check whether the coin in coin list
				if (err_print_en):
					print "Error: Invalid coin pair {}".format(market)		
				return (None,None)
	def w_get_src_des_coin(self, market, orderType, err_print_en = True):
		"""
		Get source coin and dest coin
		:param market: String literal for maket (ex: USDT-XMR)
		:param orderType: String literal for order type (ex: BUY-SELL)
		:param err_print_en: enable print error
		:return: (MarketName, BUY_ORDER/SELL_ORDER) 
		:rtype : str
		"""
		if market in self.market_list:
			coin1,coin2  = self.w_extract_market_name(market)
			if (orderType == self.SELL_ORDER):
				return (coin2, coin1)
			else:
				return (coin1, coin2)	
		else:
			if (err_print_en):
				print "Error: None exist market "				
			return (None,None)	

	def w_get_price(self, market, type, unit = 0, depth = 20):
		"""
		Get price Ask Last Bid 
		:param market: String literal for coin1-coin2 (ex: USDT-XMR)
		:param type: Ask/Last/Bid
		:param unit: if unit != 0, get price with respect to order book
		:return: price
		:rtype : float
		"""
		if type.lower() == "ask":
			type = "Ask"
		elif type.lower() == "bid":
			type = "Bid"
		else:
			type = "Last"
								
		try:
			price = self.get_marketsummary(market).get("result")[0].get(type)
			if type == "Ask":
				ordertype = "sell" #do not change this, from bittrex.py
			elif type == "Bid" :
				ordertype = "buy" #do not change this
			else: #Dont need to check order book for Last 
				return price
				
			m = self.get_orderbook(market, ordertype, depth)
			if (m.get("message") != ""): 
				print "Fail to get order book of {}: {}".format(market, m.get("message"))
				return ERROR.CMD_UNSUCCESS
			else:
				order_price_list = m.get("result")
				#print order_price_list
				sum_quantity = 0
				for o in order_price_list:
					#print o
					quantity = o.get("Quantity")
					price = o.get("Rate")
					sum_quantity += quantity
					if (sum_quantity >= unit):
						return price		

		except:
			print("Error in get {} price".format(market))
			return ERROR.CONNECTION_FAIL

	
	def w_display_market_summary(self,market):
		"""
		Display target coin summary
		:return: error code
		:rtype : ERROR
		"""
		try:
			m = self.get_marketsummary(market)
			if m.get("success"):
				data = m.get("result")[0]
				bid = data.get("Bid")
				ask = data.get("Ask")
				last = data.get("Last")
				est_value = data.get("BaseVolume")/data.get("Volume")
				dLE = (last-est_value)/est_value*100
				print "Market: {}, Ask: {:.10f}, Bid: {:.10f}, Last: {:.10f}, EstValue: {:.10f}, dLE(%): {:.3f} %".format(market,ask,bid,last,est_value,dLE)
				return ERROR.CMD_SUCCESS
			else:
				print("Cannot display market summary of {}: ".format(market,m.get("message")))
				return ERROR.CMD_UNSUCCESS
		except:
			print "Cannot display market summary of ",market
			return ERROR.CONNECTION_FAIL