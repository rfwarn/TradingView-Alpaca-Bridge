""" Retrieves stock information (like if it's fractional) for quick reference in repository.
Entered individually in the terminal or as a list (['ex1', 'ex2']).
Can be entered as argument.
Will automatically run and add if stock not in stocks.py. """
import requests
import sys
import os
import json

# Get parent directory
path = os.path.dirname(__file__)
parent = os.path.abspath(os.path.join(path, os.pardir))
sys.path.append(parent)

from AlpacaTVBridge import getKeys

filename = os.path.join(path + os.sep + 'stocks.json')

try:
    f = open(filename, 'r')
except FileNotFoundError:
    f = open(filename, 'x')
    f.write('[]')
finally:
    f.close()
    
with open(filename, 'r+') as f:
    stocks = json.load(f)

class StockUpdater:
    def __init__(self, stocks):
        self.stocks = stocks
        
    def stockSplitter(self, assetList):
        # newStocks = []
        if isinstance(assetList, list):
            # newStocks = self.Multistock(assetList)
            self.Multistock(assetList)
        elif isinstance(assetList, str):
            # newStocks.append(self.getStockInfo(assetList))
            self.updateStockInfo(self.getStockInfo(assetList))
        else:
            raise Exception(f'stockSplitter received wrong type {type(assetList)}')
        self.writeStockInfo()

    def Multistock(self, assetList):
        # Parses a list of stocks and uses getSockInfo function to retrieve informaion.
        assets = []
        for item in assetList:
            assets.append(self.updateStockInfo(self.getStockInfo(item)))
            
        return assets

    def getStockInfo(self, asset):
        # Get individual stock information and store it in stocks.JSON in the Data directory.
        # asset = "CLSK".upper()
        # asset = "CLSK".upper()
        account = getKeys("paperTrading")
        url = "https://paper-api.alpaca.markets/v2/assets/" + asset.upper()

        headers = {
            "accept": "application/json",
            "APCA-API-KEY-ID": account["api_key"],
            "APCA-API-SECRET-KEY": account["secret_key"],
        }

        response = requests.get(url, headers=headers)
        return json.loads(response.text)

    def updateStockInfo(self, asset):
        # Takes in the stock list and one asset. Adds account key to asset dictionary for user account preference ("paper", "real").
        for n, stock in enumerate(self.stocks):
            if asset['symbol'] == stock['symbol']:
                if not 'account' in stock:
                    self.stocks[n]['account'] = ""
                self.stocks[n].update(asset)
                break
        else:
            asset['account'] = ""
            self.stocks.append(asset)
        return

    def stockRemover(self, asset):
        if isinstance(asset, list):
            for item in asset:
                self.removeStock(item)
        elif isinstance(asset, str):
            self.removeStock(asset)
        else:
            raise Exception(f'stockRemover received wrong type {type(assetList)}')
        self.writeStockInfo()

    def removeStock(self, asset):
        # removes individual stocks (ex. "AAPL")
        for n, stock in enumerate(self.stocks):
            if asset.upper() == stock['symbol']:
                self.stocks.pop(n)
                break
        else:
            print(f"Stock not found: {asset}")

    def writeStockInfo(self):
        with open(filename, 'w+') as f:
            # f.write(stocks)
            json.dump(self.stocks, f, indent=4)

if __name__ == '__main__':
    try:
        print(f'Adding: {sys.argv[1]}')
        manualStockAdd = StockUpdater(stocks)
        manualStockAdd.stockSplitter(sys.argv[1])
    except IndexError:
        None
        # print('no arg provided')
        # clstest = StockUpdater(stocks)
        # clstest.stockSplitter("fcel")
        # clstest.stockRemover('goog')
        # clstest.stockRemover(["NVDA","MSFT"])
        # clstest.stockSplitter(["NVDA","MSFT"])

