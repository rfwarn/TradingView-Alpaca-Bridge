# Settings. If using realTrading, setting are used from paper if not explicitly used in real settings.
options = {
    "using": "paperTrading",
    # "using": "realTrading",
    # Real copies values from "paper", replacing any that aren't there, then updates the copied values with different values in "real".
    "paperTrading": {
        # Enable/disable shorting. Not fully implemented yet.
        # ***Alert(s) needs to say 'short' and you have to close any long positions first.
        "short": False,
        # Hard set at the moment to 20% of the cash balance. Useful in paper testing if you have around 5 stock alerts you want to analyse.
        # Be careful, if more than one order is going through at the the same time, it may spend over the total cash available and go into margins. Mainly a problem in real money trading.
        # Behaves differently when testMode is enabled.
        "buyPerc": 0.2,
        # Balance is set in the function setBalance().
        "balance": 0,
        # Not used
        "buyBal": 0,
        # Gets open potisions to verify ordering. Multiple buys before selling not implemented yet.
        "positions": [],
        # Retrieves open orders is there are any for the symbol requested.
        "orders": [],
        # Gets all the open orders.
        "allOrders": [],
        # Testmode sets the balance to a predetermined amount set in createOrder.
        # Used to not factor in remaining balance * buyPerc after positions are opened.
        "testMode": True,
        # enabled will allow submission of orders.
        "enabled": True,
        # Setting to True will impose a predefined limit for trades. Will make a market order if set to False
        "limit": True,
        # How much to limit the buy/sell price. Order not filled before sell will be canceled. Change to %
        "limitamt": 0.05,
        # Limit threshold to change to % based
        "limitThreshold": 100,
        # limit percent for everything above a certain amount which is predefined for now below.
        "limitPerc": 0.0008,
        # Maxtime in seconds before first timeout for an order.
        "maxTime": 5,
        # Total max time hard set to 30 seconds
        "totalMaxTime": 8,
        # Buy and sell cancel preferences after max time.
        # Failsafe for limit order. Options are Cancel, Market.
        "buyTimeout": "Market",
        "sellTimeout": "Market",
    },
    "realTrading": {
        # Enable/disable shorting. Not fully implemented yet.
        # ***Alert(s) needs to say 'short' and you have to close any long positions first.
        "short": False,
        # Hard set at the moment to 20% of the cash balance. Useful in paper testing if you have around 5 stock alerts you want to analyse.
        # Be careful, if more than one order is going through at the the same time, it may spend over the total cash available and go into margins. Mainly a problem in real money trading.
        # Behaves differently when testMode is enabled.
        "buyPerc": 0.02,
        # Testmode sets the balance to a predetermined amount set in createOrder.
        # Used to not factor in remaining balance * buyPerc after positions are opened.
        "testMode": False,
        # Setting to True will impose a predefined limit for trades
        "limit": True,
    },
}
