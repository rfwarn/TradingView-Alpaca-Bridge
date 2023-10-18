# TradingView-Alpaca-Bridge: Automated Trading with Python

This project is a python program that connects TradingView alerts with Alpaca API to execute buy and sell orders for stocks. It allows you to test and analyze your trading strategies in a fully automated way, using real or paper accounts. You can use any indicators or strategies from TradingView, or create your own, and let this program handle the order management for you.

**Operation:**

- Built on python 3.11.
- Best use case currently is opening and closing long positions.
- Uses TradingView webhook. Can use [ngrok](https://ngrok.com/), a cloud service (Links to come!), etc. to connect webhook trigger to order action on Alpaca.
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
  - Shorting
    - Can short but need to improve algorithms for it.
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
**Disclaimer:**

This program is for educational and informational purposes only. It is not intended to provide any financial, investment, or trading advice. The author and contributors of this program are not responsible for any losses, damages, or liabilities that may result from using this program. Users should do their own research and due diligence before using this program for real trading. Users should also read and understand the terms and conditions of TradingView and Alpaca before using their services. Use this program at your own risk.
***
**License**

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

[Licence](License): GPL v3
***
![](Assets/Capture.JPG)
