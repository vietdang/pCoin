from __future__ import print_function
import os
import json

def parseData2CSV(filename, market, fileout):
	fout = open(fileout,'w')
	enable_header = 1
	with open(filename) as f: 
		for line in f:
			if(line.find(market) != -1):
				lineout=''
				line = line.replace('u\'','"')
				line = line.replace('\'','"')
				data = json.loads(line)

				if(enable_header):
					enable_header = 0
					for key in data:
						lineout += key+','
					lineout += '\r\n'
				try:
					for key, value in data.items():
						lineout += str(value)+','
					lineout += '\r\n'
					print(lineout)
					fout.write(lineout)
				except:
					print('ERROR')
	f.close()
	fout.close()

watchlist =[  
	'BTC-ADX', 
	'BTC-BCC', 
	'BTC-DGB', 
	'BTC-DGD', 
	'BTC-ETC', 
	'BTC-ETH', 
	'BTC-FUN', 
	'BTC-GNT', 
	'BTC-KMD', 
	'BTC-LSK', 
	'BTC-LTC', 
	'BTC-MAID', 
	'BTC-MCO', 
	'BTC-MONA', 
	'BTC-NAV', 
	'BTC-NEO', 
	'BTC-OK', 
	'BTC-OMG', 
	'BTC-PAY', 
	'BTC-QTUM', 
	'BTC-QWARK', 
	'BTC-RISE', 
	'BTC-SC', 
	'BTC-STRAT', 
	'BTC-WAVES', 
	'BTC-XEM', 
	'BTC-XVG', 
	'USDT-BCC', 
	'USDT-NEO', 
	'USDT-XMR', 
	'USDT-XRP', 
	'USDT-ZEC', 
	]
for market in watchlist:
	parseData2CSV('log_market_08092017.txt', market, market+'.csv')
