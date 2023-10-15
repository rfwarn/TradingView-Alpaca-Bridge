# TradingView-Alpaca-Bridge

A python program that receives alerts from TradingView (indicators and strategies) and creates buy/sell orders on Alpaca with real and paper accounts. This allows for fully automated trading strategy testing and analysis.

**Operation:**

- Built on python 3.11.
- Uses TradingView webhook. Can use ngrok, cloud service, etc. to connect webhook to server.
  - Add the following to the beginning of a strategy/indicator alert for buying/selling order: `{{strategy.order.action}} | {{ticker}}@{{close}} | {{strategy.order.id}} `...
- Sets position size by incoming price from alpaca and settings (I like it this way to more accurately use backtesting in tradingview without having to worry about a wrong setting on that end).
  - Currently only but and sells whole number amounts. Fractional trading will be added later.
- If there's already an open order, it will cancel it and place new order as long as there is no position for buying, etc. 
- Stop loss and other similar features need to be handled in pine script.
- Cancels any open order for the specified stock if another order is received then processes new order.
  - Buying 
    - Any open order for that stock will be canceled and a new one created.
    - This help for fast market movements on limit orders or if there are other open trades placed outside this program.
    - If you already have a position with the stock you are buying/selling, no order will be placed to prevent overbuying. No pyramiding is possible at this time with this program.
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
- Use order tracking for changing from long to short positions and vice versa.
- Add fractional trading option.

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

![](Assets/Capture.JPG)
