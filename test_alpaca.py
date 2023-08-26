import unittest
from flasktest import AutomatedTrader
import os

paperTrading = {'API_KEY': os.environ.get('Alpaca_API_KEY'),
'SECRET_KEY': os.environ.get("Alpaca_SECRET_KEY"),
'paper': True}

realTrading = {'API_KEY': os.environ.get('Alpaca_API_KEY-real'),
'SECRET_KEY': os.environ.get("Alpaca_SECRET-real"),
'paper': False}

options = {
  # Enable/disable shorting. Not fully implemented yet. 
  # Alert(s) needs to say short and you have to close any long positions first.
  "short": False,
  # Hard set at the moment to 20% of the cash balance. Useful in paper testing if you have around 5 stock alerts you want to analyse.
  # Be careful, if more than one order is going through at the the same time, it may spend over the total cash available and go into margins. Mainly a problem in real money trading.
  # Behaves differently when testMode is enabled.
  "buyPerc": 0.2,
  # Balance is set in function below.
  "balance": 0,
  # Not used?
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
  # How much to limit the buy/sell price. Order not filled before sell will be canceled. Change to %
  "limitamt": 0.04,
  # limit percent for everything above a certain amount which is predefined for now below.
  "limitPerc": 0.0005
}

class TestAlpaca(unittest.TestCase):
  def test_createOrder(self):
    result = AutomatedTrader()