import json

import okx.Account_api as Account
import okx.Funding_api as Funding
import okx.Market_api as Market
import okx.Public_api as Public
import okx.Trade_api as Trade
import okx.status_api as Status
import okx.subAccount_api as SubAccount
import okx.TradingData_api as TradingData
import okx.Broker_api as Broker
import okx.Convert_api as Convert
import time
import numpy as np
import os

start_time = time.time()

os.system("clear")

st = 0
flag = '0'
api_key = "XXXXXXXXXXXX"
secret_key = "XXXXXXXXXXXXX"
passphrase = "XXXXXXXXXX"

tradingDataAPI = TradingData.TradingDataAPI(api_key, secret_key, passphrase, False, flag)
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
convertAPI = Convert.ConvertAPI(api_key, secret_key, passphrase, False, flag)
marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, True, flag)
publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag)
tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)

coin = input("交易對 (XXX-USDT): ")
every_exchange_amount = float(input("單次交易量(USDT) : "))
exchange_ret = float(input("回撤比率(%) : "))/100
exchange_spread = float(input("安全範圍(%) : "))/100


text = ""

while True:

	
	try:
		result = marketAPI.get_index_candlesticks(coin)
		price = float(str(result).split(", ")[3].replace("'", ""))
		total = float(str(fundingAPI.get_asset_valuation(ccy = 'USDT')).split(", ")[4].split("'")[3])
		if st == 0:
			np.save("price", price)
			np.save("get", total)
			high_price = price
			low_price = price
			st = 1
		if price > high_price:
			high_price = price

		if price < low_price:
			low_price = price

		if price > np.load("price.npy")*(1+exchange_spread) and high_price > price*(1+exchange_ret):

			try:
				tradeAPI.close_positions(coin, 'cross', ccy='USDT')
			except:
				q = 0
			result = tradeAPI.place_order(instId=coin, tdMode='cash', side='sell', ordType='market', sz=str(every_exchange_amount/price), ccy='USDT')			
			
			if "'code': '0'," in result:
				np.save("price", price)
				high_price = price
				low_price = price
				text += " 賣出成功!!!  交易價格 : "+str(price)
				
		if price < np.load("price.npy")*(1-exchange_spread) and low_price < price*(1-exchange_ret):

			try:
				tradeAPI.close_positions(coin, 'cross', ccy='USDT')
			except:
				q = 0
			result = tradeAPI.place_order(instId=coin, tdMode='cash', side='buy', ordType='market', sz=str(every_exchange_amount), ccy='USDT')
			
			if "'code': '0'," in result:
				np.save("price", price)
				high_price = price
				low_price = price
				text += " 買入成功!!!  交易價格 : "+str(price)
			
		os.system("clear")
		print(text)
		print("\n ------------------------------------------\n", "當前價格 :", '%.10f'%price,"\n","目前最高價 :",high_price,"\n","目前最低價 :",low_price,"\n","平衡價格 :", np.load("price.npy"),"\n ------------------------------------------")
		print(" 總資金(USDT) :", total, "\n", "獲利(USDT) :", total-np.load("get.npy"),  "\n","獲利年化 :", ((total-np.load("get.npy"))/total)*86400/(time.time()-start_time), "%\n ------------------------------------------\n")
		time.sleep(20)
	except:
		print(" error : 網路錯誤 或是 資金不足")
		time.sleep(20)
		
