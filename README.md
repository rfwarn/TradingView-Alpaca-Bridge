# TradingView-Alpaca-alerts
A python program that receives alerts from TradingView and makes buy/sell orders on Alpaca. Real or paper. Logs requests.

- Uses TradingView webhook.
- Add this to the beginning of a strategy alert for buying/selling order `{{strategy.order.action}} | {{ticker}}@{{close}} | {{strategy.order.id}}`.
