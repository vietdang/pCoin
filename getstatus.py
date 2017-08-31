
from bittrex import Bittrex
import ast
import traceback
import time
import datetime
try:
	import user
	key = user.key
	secret = user.secret
except:
	key = None
	secret = None


print key, secret
api = Bittrex(key,secret)




while 1:
	start = datetime.datetime.now()
	
	n =api.get_marketsummary("BTC-SEQ").get("result")[0].get("Bid")
	m =api.get_market_summaries().get("result")
	[p]  = [d.get("Bid") for d in m if d['MarketName'] == 'BTC-SEQ' ] 
	
	finish = datetime.datetime.now()
	print start, finish, finish - start,  n, p