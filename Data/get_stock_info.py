""" Retrieves stock information (like if it accepts fractional trades) for quick reference and stores it in stocks.json.
Entered as an arguement individually (get_stock_info.py -a ex1) in the terminal or as a list (get_stock_info.py -a 'ex1, ex2, etc...')."""
import requests
import sys
import os
import json
import ast
import argparse

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

# create an argument parser
parser = argparse.ArgumentParser(
    prog="Get stock info",
    description="Retrieves stock information and stores it in stocks.json. Can be entered individually like 'MSFT' or in a series like 'MSFT, FCEL'.",
)

# add arguments
parser.add_argument("-a", "--add", help="Adds a stock(s) to stocks.json")
parser.add_argument("-rm", "--remove", help="Removes a stock(s) from stocks.json")
parser.add_argument(
    "-c", "--clear", help="Clears a stock(s) preference from stocks.json"
)
parser.add_argument("-rl", "--real", help="Sets a stock(s) preference to real")
parser.add_argument("-p", "--paper", help="Sets a stock(s) preference to paper")

# parse arguments
try:
    args = parser.parse_args()
except Exception as e:
    print(e)


class StockUpdater:
    # TODO: Add add and remove options. Code implemented but currently only add is setup for arguments. (--add/--remove)
    # TODO: Add options for changing stock buy preferences (--account real ['MSFT', 'GOOG'], --account None MSFT).
    def __init__(self, stocklist=[]):
        self.stocklist = stocks

    def sort(self):
        list.sort(self.stocklist, key=lambda stock: stock["symbol"])

    def stockSplitter(self, assetList):
        # For adding new stocks. Determines if the input is an indicidual stock or list.
        if isinstance(assetList, list):
            self.Multistock(assetList)
        elif isinstance(assetList, str):
            self.updateStockInfo(self.getStockInfo(assetList))
        else:
            raise Exception(f"stockSplitter received wrong type {type(assetList)}")
        sorted(self.stocklist, key=lambda stock: stock["symbol"])
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
        print(f"Adding stock: {asset['symbol']}")
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
        # removes individual stocks or a list of stocks. Main app
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
        asset = asset.upper()
        print(f"Removing stock: {asset}")
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
            print("Empty stocks list")
            return
        self.sort()
        real = []
        paper = []
        neither = []
        for stock in self.stocklist:
            if stock["account"] == "":
                neither.append(stock["symbol"])
            elif stock["account"].upper() == "real".upper():
                real.append(stock["symbol"])
            elif stock["account"].upper() == "paper".upper():
                paper.append(stock["symbol"])
            else:
                print(f'Problem found. Stock "{stock}" does not have account setting. Try removing and adding it again.')
        print(f"No preference: {neither},\nreal: {real},\npaper: {paper}")
        
    def setAccountPreference(self, arg):
        pass


def getListOrString(arg1):
    # Detmine if argument is string or list
    try:
        inputList = ast.literal_eval(arg1)
    except ValueError:
        if "," in arg1:
            inputList = arg1.split(",")
            inputList = [stock.strip() for stock in inputList]
        else:
            inputList = arg1
    return inputList


if __name__ == "__main__":
    manualStock = StockUpdater(stocks)
    newArgs = ""
    if args.add:
        newArgs = getListOrString(args.add)
        manualStock.stockSplitter(newArgs)
    elif args.remove:
        newArgs = getListOrString(args.remove)
        manualStock.stockRemover(newArgs)
    elif args.clear:
        newArgs = getListOrString(args.clear)
        manualStock.setAccountPreference(newArgs)
    elif args.paper:
        newArgs = getListOrString(args.paper)
        manualStock.setAccountPreference(newArgs)
    elif args.real:
        newArgs = getListOrString(args.real)
        manualStock.setAccountPreference(newArgs)
    else:
        # Print the list of stocks account preferences if no arguments are given.
        manualStock.getAccountPreference()
    # print(f"argv: {sys.argv} - {len(sys.argv)}")
    # if len(sys.argv) == 2:
    #     # Default to add if only 1 arguement is passed in (list or indiviudal stock)
    #     print(f"Adding: {sys.argv[1]}")
    #     # print(f"Adding: {sys.argv}")
    #     inputList = getListOrString(sys.argv[1])
    #     manualStock = StockUpdater(stocks)
    #     manualStock.stockSplitter(inputList)
    # elif len(sys.argv) == 3:
    #     if sys.argv[1] in ["-a", "--add"]:
    #         inputList = getListOrString(sys.argv[2])
    #         print(f"Adding: {sys.argv[2]}")
    #         manualStock.stockSplitter(inputList)
    #     elif sys.argv[1] in ["-r", "--remove"]:
    #         inputList = getListOrString(sys.argv[2])
    #         print(f"Removing: {sys.argv[2]}")
    #         manualStock.stockRemover(inputList)
    #     else:
    #         raise Exception("Second argument invalid")
    # elif len(sys.argv) == 1:
    #     # Print the list of stocks account preferences if no arguments are given.
    #     manualStock.getAccountPreference()
    # else:
    #     raise Exception("too many arguments passed in")
