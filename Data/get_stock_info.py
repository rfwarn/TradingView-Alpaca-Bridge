""" Retrieves stock information (like if it accepts fractional trades) for quick reference and stores it in stocks.json.
Entered as an arguement individually in the terminal or as a list (['ex1', 'ex2']).
Can be entered as argument.
Will automatically run and add if stock not in stocks.py. """
import requests
import sys
import os
import json
import ast

# Get parent directory
path = os.path.dirname(__file__)
parent = os.path.abspath(os.path.join(path, os.pardir))
sys.path.append(parent)

from getKeys import getKeys

filename = os.path.join(path + os.sep + "stocks.json")

try:
    f = open(filename, "r")
except FileNotFoundError:
    f = open(filename, "x")
    f.write("[]")
finally:
    f.close()

with open(filename, "r") as f:
    stocks = json.load(f)


class StockUpdater:
# TODO: Add add and remove options. Code implemented but currently only add is setup for arguments. (--add/--remove)
# TODO: Add options for changing stock buy preferences (--account real ['MSFT', 'GOOG'], --account None MSFT).
    def __init__(self, stocklist=[]):
        self.stocklist = stocks

    def sort(self):
        # self.stocklist = sorted(self.stocklist, key=lambda stock: stock['symbol'])
        list.sort(self.stocklist, key=lambda stock: stock['symbol'])

    def stockSplitter(self, assetList):
        # For adding new stocks. Determines if the input is an indicidual stock or list.
        if isinstance(assetList, list):
            self.Multistock(assetList)
        elif isinstance(assetList, str):
            self.updateStockInfo(self.getStockInfo(assetList))
        else:
            raise Exception(f"stockSplitter received wrong type {type(assetList)}")
        sorted(self.stocklist, key=lambda stock: stock['symbol'])
        self.writeStockInfo()

    def Multistock(self, assetList):
        # Parses a list of stocks and uses getSockInfo function to retrieve informaion.
        assets = []
        for item in assetList:
            assets.append(self.updateStockInfo(self.getStockInfo(item)))

        return assets

    def getStockInfo(self, asset):
        # Get individual stock information and store it in stocks.JSON in the Data directory.
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
        # Adds or updates one asset. Adds account key to asset dictionary for user account preference ("paper", "real"). Also updates the asset data if there are changes.
        for n, stock in enumerate(self.stocklist):
            if asset["symbol"] == stock["symbol"]:
                if not "account" in stock:
                    self.stocklist[n]["account"] = ""
                self.stocklist[n].update(asset)
                break
        else:
            asset["account"] = ""
            self.stocklist.append(asset)
        return

    def stockRemover(self, asset):
        if isinstance(asset, list):
            for item in asset:
                self.removeStock(item)
        elif isinstance(asset, str):
            self.removeStock(asset)
        else:
            raise Exception(f"stockRemover received wrong type {type(asset)}")
        self.writeStockInfo()

    def removeStock(self, asset):
        # removes individual stocks (ex. "AAPL")
        for n, stock in enumerate(self.stocklist):
            if asset.upper() == stock["symbol"]:
                self.stocklist.pop(n)
                break
        else:
            print(f"Stock not found in stocks list to remove: {asset}")

    def writeStockInfo(self):
        self.sort()
        with open(filename, "w+") as f:
            json.dump(self.stocklist, f, indent=4)
            
    def getAccountPreference(self):
        if self.stocklist == []:
            print('Empty stocks list')
            return
        self.sort()
        real = []
        paper = []
        neither = []
        for stock in self.stocklist:
            if stock['account'] == '':
                neither.append(stock['symbol'])
            elif stock['account'].upper() == 'real'.upper():
                real.append(stock['symbol'])
            elif stock['account'].upper() == 'paper'.upper():
                paper.append(stock['symbol'])
        print(f"No preference: {neither},\nreal: {real},\npaper: {paper}")


if __name__ == "__main__":

    try:
        print(f"Adding: {sys.argv[1]}")
        try:
            inputList = ast.literal_eval(sys.argv[1])
        except ValueError:
            inputList = sys.argv[1]
        manualStockAdd = StockUpdater(stocks)
        manualStockAdd.stockSplitter(inputList)
    except IndexError:
        clstest = StockUpdater(stocks)
        # clstest.stockRemover('pltr')
        clstest.getAccountPreference()
        # clstest.stockSplitter("fcel")
        # clstest.stockRemover(["NVDA","MSFT"])
        # clstest.stockSplitter(["NVDA","MSFT"])
