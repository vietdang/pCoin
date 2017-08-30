from bittrex import Bittrex
import ast
import traceback
import operator
import time
import inspect
from datetime import datetime
from error_handle import ERROR


class BittrexBuysellWorker(object):
	def __init__(self, key = None, secret = None, token = None):
		self.EXCHANGE_RATE = 0.9975  # 0.25% for each trading transaction
		self.api = Bittrex(key,secret)
		self.token = token 
		try:
			m = self.api.get_market_summaries()
			#print m
			market_list = []
			for market in m.get("result"):
				market_list.append(market.get("MarketName"))
			#print marketlist
		except:
			print "Error: Cannot get market summaries"
			exit(1)
		self.market_list = market_list
	def w_get_balance(self, coin):
		"""
		Get balance of a coin
		:return: current balance value
		:rtype : float
		"""
		try:
			m = self.api.get_balance(coin)
			print m
			if (m.get("success")):
				v= m.get("result").get("Balance")
				return v if v else 0
			else:
				print("Cannot get {} balance".format(coin))
				return ERROR.CMD_UNSUCCESS
		except:
			print("Error Account/Connection issue. Get {} balance failed".format(coin))
			return ERROR.CONNECTION_FAIL
	def w_get_market_name(self, coin1, coin2):
		"""
		Get marketname for pair of coins
		:param coin1: String literal for coin 1 (ex: USDT)
		:param coin2: String literal for coin 2 (ex: XMR)
		:return: (MarketName, "Buy"/"Sell") 
		:rtype : str
		"""
		market = coin1 + "-" + coin2
		if market in self.market_list:
			return (market, "Buy")
		else:
			market = coin2 + "-" + coin1
			if market in self.market_list:
				return (market, "Sell")
			else:
				print "Error: Invalid coin pair"				
				return (None,None)
				
	def w_get_price(self, market, type, unit = 0):
		"""
		Get price Ask Last Bid 
		:param market: String literal for coin1-coin2 (ex: USDT-XMR)
		:param coin2: Ask/Last/Bid
		:param unit: if unit != 0, get price with respect to order book
		:return: price
		:rtype : float
		"""
		if type is "Last" or "Bid" or "Ask":
			try:
				price = self.api.get_marketsummary(market).get("result")[0].get(type)
				return price
			except:
				print("Error in get {} price".format(market))
				return ERROR.CONNECTION_FAIL
			'''To do: unit != 0'''
	def w_get_open_order(self, market = None):
		"""
		Get list of uuid of open orders
		:param market: String literal for coin1-coin2 (ex: USDT-XMR)
		:return: uuid list
		:rtype : str
		"""
		return self.api.get_open_orders(market)
		
	def w_order_buy_sell(self, coin1, coin2, value1, price, timeout, cancel_on_timeout = True):
		"""
		Buy/Sell from coin c1 to coin coin2 at price 
		:param coin1: String literal for coin 1 (ex: USDT)
		:param coin2: String literal for coin 2 (ex: XMR)
		:param value1: The value of coin1 which is used to buy/sell
		:param price: buy/sell price, can be Ask, Last or Bid
		:return: uuid order
		:rtype : str
		"""
		
		value2_before = self.w_get_balance(coin2) #get current coin2 balance
		market, type = self.w_get_market_name(coin1, coin2)
		#print market, type
		#Buy and sell are seperated from market point of view.
		if (type == "Buy"):
			order_buy_sell = self.api.buy_limit
			quantity = value1/price*self.EXCHANGE_RATE
			value2 = quantity*self.EXCHANGE_RATE
		elif (type) == "Sell":			
			order_buy_sell = self.api.sell_limit
			quantity = value1
			value2 = quantity*price*self.EXCHANGE_RATE
		else:
			print  "Buy/Sell Error: Invalid market {}-{}".format(coin1,coin2)
			return ERROR.CMD_INVALID	
		print("@@@ From {} {} buy {} {} at price {}.".format(value1, coin1, value2, coin2, price))
		#Process buy/sell within timeout
		#Several posible cases:
		# 1. The price is too high/low, no one wants to buy/sell
		# 2. The connection drops while waiting the result
		# 3. The quantity is too low -> "INSUFFICIENT_FUNDS" response from server
		try:
			m = order_buy_sell(market, quantity, price)
			if (m.get("success") == True):
				uuid = m.get("result").get("uuid")
				process_time = time.time() + timeout
				while 1:
					value2_after = self.w_get_balance(coin2)
					if time.time() > process_time:
						if cancel_on_timeout: #Cancel order because of timeout
							self.w_cancel_order(uuid)	
							print "Cancel order!"
						else:
							print "Order is still open!"
							return uuid
						print "{} transaction was timeout".format(type)
						return ERROR.TIME_OUT
					if (value2_after < 0):
						#Error
						print "Error: in balance code {}".format(value2_after)
						return ERROR.CMD_UNSUCCESS
					if (value2_after - value2_before >= value2*0.9): #offset 10% for safety
						#buy success
						return uuid
			elif m.get("message") == "INSUFFICIENT_FUNDS":
				print("INSUFFICIENT_FUNDS issue")
				print m
				return ERROR.PARAMETERS_INVALID
			else:
				print m
				return ERROR.CMD_UNSUCCESS
		except:
			print "Error buy/sell. Conection failed."
			return ERROR.CONNECTION_FAIL
	def w_cancel_order(self, uuid):
		"""
		Cancel an order via uuid 
		:param uuid: order uuid
		:return: error code
		:rtype : ERROR
		"""
		try:
			#todo: need check timeout
			self.api.cancel(uuid)
			while uuid in self.api.get_open_orders():
				print "Wait for cancel order {}".format(uuid)
		
			return ERROR.CMD_SUCCESS
		except:
			print "Cannot cancel order {}".format(uuid)
			return ERROR.CONNECTION_FAIL
		
class PoloniexBuysellWorker(object):
	def __init__(self, api, token = None):
		#trading fees are dynamic. Decrease over volume. Get from server
		self.api = api
		self.BUY_RATE = api.returnFeeInfo().get("makerFee")  # 0.15% for maker
		self.SELL_RATE = api.returnFeeInfo().get("takerFee") #0.25% for taker
		
		self.token = token 
	'''
		To do
		'''
		
	