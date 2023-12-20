""" Retrieves stock information (like if it accepts fractional trades) for quick reference and stores it in stocks.json.
Set or clear stock account preference. When enabled in the settings, this allows for stocks to be selectively bought and 
sold on either rea or paper accounts. Clearing will default to what the settings "using" is set to. Entered as an arguement 
individually (get_stock_info.py -a ex1) in the terminal or as a list (get_stock_info.py -a 'ex1, ex2, etc...')."""
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

# with open(filename, "r") as f:
#     stocks = json.load(f)

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
# parser.add_argument("-sm", "--set amount", help="Sets stock amount preference")
# parser.add_argument("-m", "--amount", action="store_true", help="Gets stock amount preferences and prints them in a readable format")
parser.add_argument(
    "-ver",
    "--verify",
    action="store_true",
    help="Verifes stocks in stocks.json have account and amount preferences and adds them if they don't",
)

# parse arguments
try:
    args = parser.parse_args()
except Exception as e:
    print(e)


class StockUpdater:
    """Takes in a stock list as a list and write as a boolean. Set write to false for testing purposes otherwise it will overwrite the saved list (stocks.json)."""

    def __init__(self, stocklist=[], write=True):
        # By default, stocks from the main list should be passed in.
        self.stocklist = stocklist
        # Added for testing purposes so it doesn't make changes.
        self.write = write

    def getStockList(self):
        # Gets the list from the stocks.json file and loads them into stocklist.
        with open(filename, "r") as f:
            stocks = json.load(f)
        self.stocklist = stocks
        return stocks

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
        return self.stocklist

    def Multistock(self, assetList):
        # Parses a list of stocks and uses getSockInfo function to retrieve informaion.
        assets = []
        for item in assetList:
            assets.append(self.updateStockInfo(self.getStockInfo(item)))

        return assets

    def getStockInfo(self, asset):
        # Get individual stock information and store it in stocks.JSON in the Data directory.
        # Allows for testing when not called.
        account = getKeys("paperTrading")
        url = "https://paper-api.alpaca.markets/v2/assets/" + asset.upper()

        headers = {
            "accept": "application/json",
            "APCA-API-KEY-ID": account["api_key"],
            "APCA-API-SECRET-KEY": account["secret_key"],
        }

        response = requests.get(url, headers=headers)
        return json.loads(response.text)

    def findStock(self, asset):
        for stock in self.stocklist:
            if asset.upper() == stock["symbol"]:
                return stock
        else:
            return None

    def updateStockInfo(self, asset):
        # Adds or updates one asset at a time. Adds account key to asset dictionary for user account preference
        # ("paper", "real"). Also updates the asset data if there are changes.
        print(f"Adding stock: {asset['symbol']}")
        for n, stock in enumerate(self.stocklist):
            if asset["symbol"] == stock["symbol"]:
                if not "account" in stock:
                    self.stocklist[n]["account"] = ""
                if not "amount" in stock:
                    self.stocklist[n]["amount"] = 0
                self.stocklist[n].update(asset)
                break
        else:
            asset["account"] = ""
            self.stocklist.append(asset)
        return

    def verifyStockPreferences(self):
        # Verifies amount and account settings are present and adds them if they aren't.
        failTest = True
        for stock in self.stocklist:
            if not "account" in stock:
                stock["account"] = ""
                print(f"Added blank account for: {stock['symbol']}")
                failTest = False
            if not "amount" in stock:
                stock["amount"] = 0
                print(f"Added blank amount for: {stock['symbol']}")
                failTest = False
            elif not (isinstance(stock["amount"], float) or isinstance(stock["amount"], int)):
                print(f'Invalid value for: {stock["symbol"]} of: {type(stock["amount"])}. Expected float or int.')
                failTest = False
        if failTest:
            print('Verification pass')
        self.writeStockInfo()

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
    
    def setStockAmount(self):
        # Sets a specific stock amount to buy and sell which will grow or shrink with the asset.
        pass

    def writeStockInfo(self):
        self.sort()
        if self.write:
            with open(filename, "w+") as f:
                json.dump(self.stocklist, f, indent=4)
        else:
            print("Write not enabled")

    def printAccountPreference(self):
        if self.stocklist == []:
            empty = "Empty stocks list"
            print(empty)
            return empty
        self.sort()
        allstocks = []
        real = []
        paper = []
        neither = []
        for stock in self.stocklist:
            allstocks.append(stock["symbol"])
            if stock["account"] == "":
                neither.append(stock["symbol"])
            elif stock["account"].upper() == "real".upper():
                real.append(stock["symbol"])
            elif stock["account"].upper() == "paper".upper():
                paper.append(stock["symbol"])
            else:
                print(
                    f'Problem found. Stock "{stock}" does not have account setting. Try removing and adding it again.'
                )
        print(
            f"-----------",
            f"\nAll stocks: {allstocks}\n--------------------------------------------------------------",
            f"\nNo preference: {neither},\nreal: {real},\npaper: {paper}",
            f"\n-----------",
        )

    def printAmountPreference(self):
        pass

    def setAccountPreference(self, newStocks, accountPref):
        # Function to print stock preference changes.
        def printPrefChange(stock, pref):
            print(f"Stock preference for: {stock}, set to {pref if pref else 'clear'}")

        # Set or clear stock account preferences.
        changed = False
        if isinstance(newStocks, list):
            for stock in newStocks:
                stockPref = self.findStock(stock)
                if stockPref:
                    stockPref["account"] = accountPref
                    printPrefChange(stock, accountPref)
                    changed = True
                else:
                    print(f"Stock not found for: {stock}")
                    self.stockSplitter(stock)
        elif isinstance(newStocks, str):
            stockPref = self.findStock(newStocks)
            if stockPref:
                stockPref["account"] = accountPref
                printPrefChange(newStocks, accountPref)
                changed = True
            else:
                print(f"Stock not found for: {newStocks}")
                return
        else:
            raise Exception(
                f"setAccountPreference received wrong type {type(newStocks)}"
            )
        if changed:
            self.writeStockInfo()
        else:
            return "No changes made"


def getListOrString(arg1):
    # Detmine if argument is string or list
    try:
        inputList = ast.literal_eval(arg1)
        inputList = [stock.strip().upper() for stock in inputList]
    except ValueError:
        if "," in arg1:
            inputList = arg1.split(",")
            inputList = [stock.strip().upper() for stock in inputList]
        else:
            inputList = arg1.strip().upper()
    return inputList


if __name__ == "__main__":
    # Allows for adding, removing, and setting of stock preferences for account (paper/real)
    manualStock = StockUpdater()
    manualStock.getStockList()
    newArgs = ""
    if args.add:
        newArgs = getListOrString(args.add)
        manualStock.stockSplitter(newArgs)
    elif args.remove:
        newArgs = getListOrString(args.remove)
        manualStock.stockRemover(newArgs)
    elif args.clear:
        newArgs = getListOrString(args.clear)
        manualStock.setAccountPreference(newArgs, "")
    elif args.paper:
        newArgs = getListOrString(args.paper)
        manualStock.setAccountPreference(newArgs, "paper")
    elif args.real:
        newArgs = getListOrString(args.real)
        manualStock.setAccountPreference(newArgs, "real")
    elif args.verify:
        manualStock.verifyStockPreferences()
    elif args.amount:
        manualStock.printAmountPreference()
    else:
        # Print the list of stocks account preferences if no arguments are given.
        manualStock.printAccountPreference()
