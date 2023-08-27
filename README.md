# TradingView-Alpaca-alerts
A python program that receives alerts from TradingView (indicators and strategies) and creates buy/sell orders on Alpaca with real and paper accounts.

- Right now, this is good for trying strategies out with a paper account (not real trading).
- Generate report will create a CSV daily report for buying and selling with alpaca paperor real stocks. Default is 7 days prior.
- Uses TradingView webhook. Can use ngrok, cloud service, etc. to connect webhook to flask server.
- Compatible with **'Machine Learning: Lorentzian Classification'** indicator alerts (match Close Long, Open Long, etc.)
  - <font color=orange>LDC Kernel Bullish ▲ | CLSK@4.015 | </font>(1)...
- Also compatible with strategy alerts (ex. strategy.entry, strategy.close_all, etc.)
  - <font color=orange>order sell | MSFT@337.57 | </font>Directional Movement Index...
  -   Add the following to the beginning of a strategy alert for buying/selling order: `{{strategy.order.action}} | {{ticker}}@{{close}} | {{strategy.order.id}}`.
- Stop loss and other similar features should be handled in pine script. 


**Known issues:**
- Going short from long position or vice versa doesn't work. Need to wait for order to zero out position then open an order. 
- Need to see about adding something to fill or kill after x time, especially for limit orders. 
- If more than one buy trigger happens too close together the cash available won't reflect both orders and can overspend. There are other failsafes in place to prevent overspending if account balance is negative.
