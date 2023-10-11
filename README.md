# TradingView-Alpaca-Bridge

A python program that receives alerts from TradingView (indicators and strategies) and creates buy/sell orders on Alpaca with real and paper accounts. This allows for fully automated trading strategy testing and analysis.

**Operation:**

- Uses TradingView webhook. Can use ngrok, cloud service, etc. to connect webhook to server.
  - Add the following to the beginning of a strategy/indicator alert for buying/selling order: `{{strategy.order.action}} | {{ticker}}@{{close}} | {{strategy.order.id}} `...
- Sets position size by incoming price from alpaca and settings (I like it this way to more accurately use backtesting in tradingview without having to worry about a wrong setting on that end).
- Stop loss and other similar features should be handled in pine script.
- Cancels any open order for the specified stock if another order is received then processes new order.
  - Buying 
    - Any open order for that stock will be canceled and a new one created.
    - If you already have a position with that stock, no order will be placed to prevent overbuying.
- Checks position before shorting/going long to prevent overbuying/overselling.
- Buy price is received from TradingView webhook for position size calculation based on user settings.
- Great for trying strategies out with paper trading. Use at your own risk for real trading. Should work but haven't tested it much yet in real money trading. I'll update after trying it out.
- Generate report will create a CSV 30 day report (default) for buying and selling with alpaca paper or real stocks.
- Compatible with jdehorty's **'Machine Learning: Lorentzian Classification'** indicator alerts (match Close Long, Open Long, etc. when creating alerts).
  - Ex. <font color=orange>LDC Kernel Bullish ▲ | CLSK@4.015 | (1)</font>...
- Also compatible with strategy alerts (ex. strategy.entry, strategy.close_all, etc.).
  - <font color=orange>order sell | MSFT@337.57 | </font>Directional Movement Index...

---

**Future plans:**

- Generate stock/strategy performance analysis dashboard from reports generated.
- Implement order tracking to ensure completion or cancel.
- Use order tracking for changing from long to short positions and vice versa.

---

**API keys:**
Add these to your environment an/or .env file:
```
Paper trading keys:
"Alpaca_API_KEY=ASDF..."
"Alpaca_SECRET_KEY=WERT..."

Real money trading keys:
"Alpaca_API_KEY-real=GREJ..."
"Alpaca_SECRET-real=XCVJH..."
```
***
**Settings (adjusted in the settings.json file):**

    {
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
      # Not used?
      "req": "",
      # Setting to True will impose a predefined limit for trades
      "limit": True,
      # How much to limit the buy/sell price. Order not filled before sell will be canceled. Change to buyPerc setting once stock price >limitThreshold.
      "limitamt": 0.04,
      # Limit threshold $ amount to change to % based limit
      "limitThreshold": 100,
      # limit percent for everything above a certain amount which is predefined for now below.
      "limitPerc": 0.0005,
      # Maxtime in seconds before canceling an order
      "maxTime":10
    }

![](Assets/Capture.JPG)
