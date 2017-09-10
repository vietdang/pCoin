from exchange_bittrex import BittrexExchange
from utilities import ERROR
import time



class BittrexBuySellWorker(BittrexExchange):
	#Should provide valid key and secret to run this worker
	def __init__(self, key, secret, token = None):
		if not key or not secret:
			print "Error in key and secret"
			exit()
		self.token = token
		BittrexExchange.__init__(self,key,secret)
		
		
	def w_get_coin_total_balance(self, coin):
		"""
		Get total balance of a coin
		:return: current total balance value
		:rtype : float
		"""
		try:
			m = self.get_balance(coin)
			#print m
			if (m.get("success")):
				v= m.get("result").get("Balance")
				return v if v else 0
			else:
				print("Cannot get {} balance".format(coin))
				return ERROR.CMD_UNSUCCESS
		except:
			print("Error Account/Connection issue. Get {} balance failed".format(coin))
			return ERROR.CONNECTION_FAIL
			
	def w_get_coin_available_balance(self, coin):
		"""
		Get available balance of a coin
		:return: current available balance value
		:rtype : float
		"""
		try:
			m = self.get_balance(coin)
			#print m
			if (m.get("success")):
				v= m.get("result").get("Available")
				return v if v else 0
			else:
				print("Cannot get {} balance".format(coin))
				return ERROR.CMD_UNSUCCESS
		except:
			print("Error Account/Connection issue. Get {} balance failed".format(coin))
			return ERROR.CONNECTION_FAIL
			
	def w_get_account_balances(self):
		"""
		Get current account balance of all coins
		:return: list of available balance and total balance of coins
		:rtype : dict
		"""
		try:
			m = self.get_balances()
			if (m.get("success")):
				acc = m.get("result")
				balance_list = []
				for coin in acc:
					if coin.get("Balance") != 0:
						balance_list.append(coin)
				return balance_list
						
				
			else:
				print("Cannot get account balances: {}".format(m.get("message")))
				return ERROR.CMD_UNSUCCESS
		except:
			print("Error Account/Connection issue. Get account balances failed")
			return ERROR.CONNECTION_FAIL
			
	def w_get_open_order(self, market = None):
		"""
		Get list of uuid of open orders
		:param market: String literal for coin1-coin2 (ex: USDT-XMR)
		:return: uuid list
		:rtype : str
		"""
		try:
			m = self.get_open_orders(market)
		except:
			print("Error in get_open_orders", m)
			m = ERROR.CONNECTION_FAIL
		return m
		
	def w_order_buy_sell(self, coin1, coin2, value1, price, timeout, cancel_on_timeout = True):
		"""
		Buy/Sell from coin c1 to coin coin2 at price 
		Possible cases:
			- timeout = 0 : nowait
			- timeout = n : wait for n seconds until success 
				+ cancel_on_timeout = True: cancel the order
				+ cancel_on_timeout = False: keep the order and exit
			- timeout = INFINITE: wait until success
		:param coin1: String literal for coin 1 (ex: USDT)
		:param coin2: String literal for coin 2 (ex: XMR)
		:param value1: The value of coin1 which is used to buy/sell
		:param price: buy/sell price, can be Ask, Last or Bid
		:return: uuid order
		:rtype : str
		"""
		
		#value2_before = self.w_get_available_balance(coin2) #get current coin2 balance
		market, type = self.w_get_market_name(coin1, coin2)
		#print market, type
		#Buy and sell are seperated from market point of view.
		if (type == self.BUY_ORDER):
			order_buy_sell = self.buy_limit
			quantity = value1/price*self.EXCHANGE_RATE
			value2 = quantity*self.EXCHANGE_RATE
		elif (type) == self.SELL_ORDER:			
			order_buy_sell = self.sell_limit
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
					try:
						#value2_after = self.w_get_available_balance(coin2)
						if time.time() > process_time:
							if cancel_on_timeout: #Cancel order because of timeout
								self.w_cancel_order(uuid)	
								print "Cancel order!"
							else:
								print "Order is still open!"
								return uuid
							print "{} transaction was timeout".format(type)
							return ERROR.TIME_OUT
						
							m = self.w_get_open_order(market)
							#print m
							if uuid not in m: #buy/sell success
								break
					except:
						print "except in wait order"
						time.sleep(3)
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
		
	def w_order_buy_sell_by_market(self, market, ordertype, size, price, timeout, cancel_on_timeout = True):
		"""
		Buy/Sell market by ordertype at price 
		:
		:param market: USDT-XMR
		:param ordertype: "LIMIT_BUY" / "LIMIT_SELL"
		:param size: The value of coin1 which is used to buy/sell
		:param price: buy/sell price, can be Ask, Last or Bid
		:return: uuid order
		:rtype : str
		"""
		coin1,coin2  = self.w_get_src_des_coin(market, ordertype)
		return self.w_order_buy_sell(coin1, coin2, size, price, timeout, cancel_on_timeout)
	
	def w_cancel_order(self, uuid):
		"""
		Cancel an order via uuid 
		:param uuid: order uuid
		:return: error code
		:rtype : ERROR
		"""
		try:
			#todo: need check timeout
			self.cancel(uuid)
			while uuid in self.get_open_orders():
				print "Wait for cancel order {}".format(uuid)
		
			return ERROR.CMD_SUCCESS
		except:
			print "Cannot cancel order {}".format(uuid)
			return ERROR.CONNECTION_FAIL
			
	def w_display_account_balances(self):
		"""
		Display all available coins with balances > 0 (include total and available)
		:return: error code
		:rtype : ERROR
		"""
		try:
			m = self.w_get_account_balances()
			print "Account balances:"
			if m:
				for c in m:
					print "Coin: {:.6s}, Total: {:.10f}, Available: {:.10f}".format( c.get("Currency"), c.get("Balance"), c.get("Available"))
			return ERROR.CMD_SUCCESS
		except:
			print "Cannot display account balance"
			return ERROR.CONNECTION_FAIL
			
	def w_display_coin_balances(self, coin):
		"""
		Display target coin balance(include total and available)
		:return: error code
		:rtype : ERROR
		"""
		try:
			available = self.w_get_coin_available_balance(coin)
			total = self.w_get_coin_total_balance(coin)
			if coin != "BTC":
				market, ordertype =self.w_get_market_name(coin,"BTC")
				BTC_XXX_bid = self.w_get_price(market,"Bid")
				est_btc_value = total*BTC_XXX_bid
			else:
				est_btc_value = total
			print "Coin balances:"
			print "Coin: {:.6s}, Total: {:.10f}, Available: {:.10f}, Est(BTC): {:.10f}".format(coin,total,available,est_btc_value)
			return ERROR.CMD_SUCCESS
		except:
			print "Cannot display account balance"
			return ERROR.CONNECTION_FAIL
			


	

