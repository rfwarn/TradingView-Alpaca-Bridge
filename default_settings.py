# Settings. If using realTrading, setting default to paperTrading if not explicitly used in realTrading settings. Swap commented "using" to switch back and forth.
options = {
    "using": "paperTrading",
    # "using": "realTrading",
    # Settings for paperTrading.
    "paperTrading": {
        # Allow for individual stock account preference. When set to True, if a stock in Data/stocks.json has the account
        #   as 'real' or 'paper', it will use that account for the transaction. Using the Data/get_stock_info.py with an
        #   argument of an individual ('JPM') or list (['JPM','ORCL']) will add the stock to stocks.json then edit the file
        #   and change the default value of '' to the preferred account. This allows individual stock control when the performance
        #   of the paper account is adaquate to test with the real account. Accounts respect the individualized settings in the settings file.
        "perStockPreference": True,
        # Allow for individual stock amount preference per stock. Setting to False will disable this option.
        #   This will also track the amount you have gained of lost with the particular stock after a trady allowing
        #   for compounding gains/losses on individual stocks.
        # An example would be if you set this to 2000 and a buy and sell action gained 10%, this value would change to
        #   2200 which is how much it would spend buying the stock next time.
        "perStockAmount": True,
        # Allows for compounding of individual stocks. perStockAmount must be True and value for symbol in
        # stocks.json must be present and have an amount >0. Can use "python get_stock_info.py -m" in the Data directory
        # to get stock preferences and "python get_stock_info.py -sm 1000 QQQ" for example to set am amount.
        # Verify orders also has to be True for this to work.
        "perStockAmountCompounding": True,
        # Enable/disable shorting. Not fully implemented yet.
        # ***Alert(s) needs to say 'short' and you have to close any long positions first.
        "short": False,
        # Set to percentage of the cash balance (0.2 = 20%, 0.02 = 2%...). If useMarinBuyingPower is >0, margin will also be factored in.
        # Useful in paper testing if you have around 5 stock alerts you want to analyze.
        # Be careful, if more than one order is going through at the the same time,
        #   it may spend over the total cash available and go into margins. Mainly a potential problem in real money trading.
        # Limits the amount of positions open at a time to help prevent overspending. Set to 0 to disable limit.
        #   Warning, if more than one order is processed before the others complete, it may exceed the maximum limit.
        #   High frequency algorithms and/or multiple alerts on different stock (~8 or more) are more likely to cause this since they trigger more often.
        "maxPositions": 0,
        # If testMode is enabled, it uses the % of 100000 (Ex. 0.2 = 20%, 0.02 = 2%...).
        "buyPerc": 0.2,
        # Sets a predefined amount to use for trading. Does not factor in account balance. Amount is USD. Bypassed if "testMode" is True or "buyPerc" is > 0.
        # Also overriden if perStockAmount is true and the value in 'amount' under the stock in stocks.json is >0 for that stock.
        "buyAmt": 2000,
        # Set to 0 to automatically set balance based off other settings (cash available, margin, see other settings)
        "balance": 0,
        # Uses relative available funds (cash remaining) * the buyPerc. Ignored if testMode is True.
        # "useRelativeBalance": True,
        # Amount of margin to use. Set to 0 to disable which will use cash only. If testMode is enabled this will have no effect.
        # Otherwise set to percent of margin to use (Ex. 1 = 100% of daytrading_buying_power, 0.5 = 50%...)
        # "useMarinBuyingPower": 0,
        # Enable fractional trading. ***Fractional orders must be market orders***. May add auto setting for this later.
        "fractional": False,
        # Testmode sets the balance to a predetermined amount hard set in createOrder ($100,000).
        # Great for paper trading and performance analysis.
        "testMode": True,
        # enabled will allow submission of orders.
        "enabled": True,
        # Enables or disables extended hours. Must be a limit order to work.
        "extendedHours": True,
        # Setting to True will impose a predefined limit for trades. Will make market orders if set to False.
        "limit": True,
        # How much to limit the buy/sell price. Order not filled before sell will be canceled. Change to %
        "limitAmt": 0.15,
        # Limit threshold to change to % based above it.
        "limitThreshold": 100,
        # Limit percent for everything above limitThreshold (Ex. Buy @$200 would make the limit $200.16 for a $0.16 limit)
        "limitPerc": 0.0008,
        # Enable/disable order verification. Suggested use for market orders or high frequency trading (roughly buy/sell within a minute).
        "verifyOrders": True,
        # Maxtime in seconds before first timeout for an order. Only used when verifyOrders is enabled.
        "maxTime": 8,
        # Total max time before canceling the order. Only used when verifyOrders is enabled.
        "totalMaxTime": 5,
        # Buy and sell cancel preferences after max time.
        # Failsafe for limit order. Options are [Cancel, Market].
        "buyTimeout": "Cancel",
        "sellTimeout": "Market",
        # A low point for the account to stop trading. Set to 0 to disable.
        # "minAccountStop": 0,
        # Sell all assets once hitting the low point to prevent further loss?
        # "minAccountSell": True,
    },
    # realTrading copies values from paperTrading and overrides any duplicates.
    # Will raise an Exception if there are items in realTrading that aren't in paperTrading.
    # See descriptions above.
    "realTrading": {
        "perStockPreference": True,
        "perStockAmount": True,
        "perStockAmountCompounding": True,
        "short": False,
        "maxPositions": 0,
        "buyPerc": 0,
        "buyAmt": 2000,
        "testMode": False,
        "limit": True,
        "fractional": False,
    },
}

if __name__ == "__main__":
    import os, filePath, shutil

    def getSettings(paper, real):
        paper = paper.copy()
        pc = paper.copy()
        pc.update(real)
        if len(pc) != len(paper):
            raise Exception(
                "Extra variables found in real settings. Please remove or fix any typos and try again"
            )
        return pc, paper

    def validateKeys(itemsA, itemsB, name):
        # Checks if all keys from itemA are in itemB. Then checks is any of the values are different
        status = True
        for k, v in itemsA.items():
            if not k in itemsB.keys():
                status = False
                print(f"Missing key found in settings.py {name} settings: {k}")
            else:
                if itemsB[k] != v:
                    print(f"{name} {k} setting: {itemsB[k]}, default: {v}")
        if status:
            return True
        return False

    real, paper = getSettings(options["paperTrading"], options["realTrading"])
    if filePath.fileName(__file__) == "default_settings.py":
        try:
            from settings import options as settingsFile

            setReal, setPaper = getSettings(
                settingsFile["paperTrading"], settingsFile["realTrading"]
            )
            if len(setPaper) > len(paper):
                raise Exception(
                    "Too many settings found in settings.py in the paperTrading section"
                )
            elif len(setPaper) < len(paper):
                print("Found a missing setting in paperSettings")
            elif len(setReal) > len(real):
                raise Exception(
                    "Too many settings found in settings.py in the realTrading section"
                )
            elif len(setReal) < len(real):
                print("Found a missing setting in realSettings")
            else:
                if validateKeys(paper, setPaper, "Paper"):
                    print("--Paper settings look good")
                if validateKeys(real, setReal, "Real"):
                    print("--Real settings look good")
        except ModuleNotFoundError:
            print("No settings file found. Creating...")
            shutil.copyfile(f"{__file__}", f"{filePath.filePath() + os.sep}settings.py")
