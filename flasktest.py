from flask import Flask, request, Response
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.models import Position
import os, logging, re, json, time

# Create a logger
logger = logging.getLogger('my_logger')

# Set the log level to include all messages
logger.setLevel(logging.DEBUG)

# Create a file handler
handler = logging.FileHandler('my_app.log')

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Get the API keys from the environment variables. These are for Paper keys. Below are keys for real trading in Alpaca
paperTrading = {'api_key': os.environ.get('Alpaca_API_KEY'),
'secret_key': os.environ.get("Alpaca_SECRET_KEY"),
'paper': True}

# Real money trading
realTrading = {'api_key': os.environ.get('Alpaca_API_KEY-real'),
'secret_key': os.environ.get("Alpaca_SECRET-real"),
'paper': False}


# Get file path
def filePath():
  return os.path.dirname(__file__)

# Load config. If file isn't found, print error in console and use defaults in class.
try:
  with open(filePath() + os.sep + 'settings.json') as f:
    settings = json.load(f)
    # Pointer for the type you want to use (real/paper).
    account = settings['using']
    settings = settings[account]
except FileNotFoundError:
  
  print('settings.json file not found, using internal settings.')

app = Flask(__name__)

# data examples from pine script strategy alerts:
  # Compatible with 'Machine Learning: Lorentzian Classification' indicator alerts
  # LDC Kernel Bullish ▲ | CLSK@4.015 | (1)...
  # Also compatible with custom stratedy alerts (ex. strategy.entry, strategy.close_all, etc.)
  # order sell | MSFT@337.57 | Directional Movement Index...

def acctInfo():
  temp = TradingClient(**account).get_account()
  print(f'***account: {"PAPER" if account["paper"] else "REAL MONEY"}')
  print(f'status: {temp.status}')
  print(f'account blocked: {temp.account_blocked}')
  print(f'trade_suspended_by_user: {temp.trade_suspended_by_user}')
  print(f'trading_blocked: {temp.trading_blocked}')
  print(f'transfers_blocked: {temp.transfers_blocked}')
  print(f'equity: {temp.equity}')
  print(f'currency: {temp.currency}')
  print(f'cash: {temp.cash}')
  print(f'buying_power: {temp.buying_power}')
  print(f'daytrading_buying_power: {temp.daytrading_buying_power}')
  print(f'shorting_enabled: {temp.shorting_enabled}')
  print(f'crypto_status: {temp.crypto_status}')
  print('-------------------------------------------------')
  # print(f'{temp.}')
  # print(f'{temp.}')
  # print(f'')

@app.route('/', methods=['POST'])
def respond():
    # print(request.data)
    
    req_data = str(request.data)
    logger.info(f'Recieved request with data: {req_data}')
    trader = AutomatedTrader(**account, req=req_data)
    
    
    return Response(status=200)
    # return "Hello World"
  
class AutomatedTrader:
  """ Trader client and functions """
  def __init__(self, api_key, secret_key, paper=True, req='', newOptions={}):
    self.options = {
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
    # Use settings if they were imported successfully.
    if settings:
      self.options = settings
    # Count the items in options and if newOptions changes this raise an exception.
    optCnt = len(self.options)
    self.options.update(newOptions)
    if len(self.options)!=optCnt:
      raise Exception('Extra options found. Verify newOption keys match option keys')
    # Load keys, request data, and create trading client instance.
    self.api_key = api_key
    self.secret_key = secret_key
    self.paper = paper
    self.client = self.createClient()
    self.req = req
    # Check for configuration conflict that could cause unintended buying.
    if self.options['enabled'] and self.options['testMode'] and not self.paper:
      err = 'testMode and real money keys being used, exiting. Switch one or the other.'
      logger.error(err)
      raise Exception(err)
    # Verify 'enabled' option is True. Used primarily for unittesting.
    elif self.options['enabled']:
      self.setData()
      self.setOrders()
      self.setPosition()
      self.setBalance()
      self.createOrder()

  def createClient(self):
    # Creates the trading client based on real or paper account.
    return TradingClient(self.api_key, self.secret_key, paper=self.paper) 

  def createOrder(self):
    # Setting papameters for market order
    # Clear uncompleted open orders. Shouldn't be any unless it's after hours...
    if len(self.options['orders'])>0:
      self.cancelOrderById()
      
    if self.options['testMode']:
      # Testing with preset variables
      self.options["balance"] = 100000
    # Check for negative balance
    elif self.options['balance']<0:
      logger.debug(f'Negative balance: {self.options["balance"]}')
      self.options['balance'] = 0
      
    # shares to buy in whole numbers
    amount = int(self.options['balance']*self.options['buyPerc']/self.data['price'])
    
    # get position quantity
    posQty = float(self.options['positions'].qty) if self.options['positions']!=None else 0
    
    # Setup for open/close/bear/bull/short/long
    if self.data['action'] == "Open" and self.data['position'] == "Short":
      side = OrderSide.SELL
      # Close if shorting not enabled. Need to adjust for positive and negative positions. Done?
      if posQty<0:
        logger.debug(f'Already shorted for: {self.data["stock"]}')
        amount = 0
        return
      if not self.options['short'] and posQty==0:
        logger.info(f'Shorting not enabled for: {self.data["stock"]}, {self.data["action"]}, {self.data["position"]}')
        amount = 0
      elif not self.options['short'] and posQty>0:
        logger.info(f'Selling all positions. Shorting not enabled for: {self.data["stock"]}, {self.data["action"]}, {self.data["position"]}')
        amount = posQty
      elif self.options['short'] and posQty>0:
        # Can't short with positions so need to figure out how to sell then short.
        amount = posQty
      elif self.options['short'] and posQty==0:
        pass
      elif self.options['short'] and posQty<0:
        logger.info(f'Already shorted for: {self.data["stock"]}, {self.data["action"]}, {self.data["position"]}')
        amount = 0
        return
    elif self.data['action'] == "Close" and self.data['position'] == "Short":
      side = OrderSide.BUY
      # Close positions for symbol
      if posQty>0:
        logger.debug(f'Short not needed. Already long for: {self.data["stock"]}')
        amount = 0
        return
      elif posQty==0:
        pass
      elif posQty<0:
        amount = abs(posQty)
    elif (self.data['action'] == "Bull" or self.data['action'] == "buy" or self.data['action'] == "Open") and (self.data['position'] == "Long" or self.data['position'] == None):
      side = OrderSide.BUY
      if self.options['positions'] != None:
        amount = 0
      
    elif (self.data['action'] == "Bear" or self.data['action'] == "sell" or self.data['action'] == "Close") and (self.data['position'] == "Long" or self.data['position'] == None):
      side = OrderSide.SELL
      # Close positions for symbol. Setting to 0 so it won't run if there's already a position.
      amount = 0
      if self.options['positions'] != None and posQty>0:
        amount += posQty
      # need to add short depending if shorting is enabled. Not needed?
      # if not self.options['short']:
      #   logger.info(f'Shorting not enabled for: {self.data["stock"]}, {self.data["action"]}, {self.data["price"]}')
      #   return
    else:
      logger.error(f'Unhandled Order: {self.data["stock"]}, {self.data["action"]}, {self.data["position"]}')
      
    # return if 0 shares are to be bought. Basically not enough left over for buying 1 share or more
    if amount==0:
      logger.info(f'0 Orders requested: {self.data["stock"]}, {self.data["action"]}, {self.data["price"]}')
      return
    # return if less then 0 shares are to be bought. Shouldn't happen right now
    elif amount<0:
      logger.info(f'<0 Orders requested: {self.data["stock"]}, {self.data["action"]}, {self.data["price"]}, amount: {amount}')
      return
    
    # Setup buy/sell order
    
    # market order, limit set to False
    if not self.options['limit']:
      order_data = MarketOrderRequest(
        symbol=self.data['stock'], # "MSFT"      
        qty=amount, # 100
        side=side,
        time_in_force=TimeInForce.GTC
        )
    # Limit order, limit set to True
    elif self.options['limit']:
      # Predefined price to override limitamt with limitPerc*price
      if self.data['price']>self.options['limitThreshold']:
        self.options['limitamt'] = self.data['price']*self.options['limitPerc']
      order_data = LimitOrderRequest(
        symbol=self.data['stock'], # "MSFT"
        limit_price=round(self.data['price']+(self.options['limitamt'] if side==OrderSide.BUY else -self.options['limitamt']),2),
        qty=amount, # 100
        side=side,
        time_in_force=TimeInForce.GTC
        )
    self.order_data = order_data
    self.submitOrder()

  def submitOrder(self):
    try:
      self.order_data
    except AttributeError:
      return
    if not self.options['enabled']:
      # escape and don't actually submit order if not enabled. For debugging/testing purposes.
      logger.debug(f'Not enabled, order not placed for: {self.data["stock"]}, {self.data["action"]}, {self.data["price"]}')
      return
    # Market order
    self.order = self.client.submit_order(self.order_data)
    self.verifyOrder()
    # Need to add while look that checks if the order finished. if limit sell failed, change to market order or something like that. For buy just cancel or maybe open limit then cancel?

  def verifyOrder(self, order=None):
    # TODO: Need to add async stream method for checking for order completion.
    maxTime = 10
    now = time.time()
    id = self.order.client_order_id
    while self.order.filled_at==None and self.order.failed_at==None and self.order.canceled_at==None:
      if time.time() - now > maxTime:
        self.cancelOrderById(self.order.id.hex)
        logger.debug(f'Order exeeded max time for: {self.data["stock"]}, {self.data["action"]}, {self.data["price"]}')
      elif time.time() - now > 50:
        # failsafe to exit loop
        logger.warn(f'Order exeeded 50 seconds for: {self.data["stock"]}, {self.data["action"]}, {self.data["price"]}')
        break
      self.order = self.client.get_order_by_client_id(id)
      time.sleep(1)
    if self.order.canceled_at!=None:
      logger.debug(f'Order canceled for: {self.data["stock"]}, {self.data["action"]}, {self.data["price"]}')
    elif self.order.failed_at!=None:
      logger.warn(f'Order failed for: {self.data["stock"]}, {self.data["action"]}, {self.data["price"]}')
    elif self.order.filled_at!=None:
      logger.info(f'Order filled for: {self.data["stock"]}, {self.data["action"]}, {self.data["price"]}')

  def setBalance(self):
    # set balance at beginning and after each transaction
    cash = float(self.client.get_account().cash)
    nMBP = float(self.client.get_account().non_marginable_buying_power)
    acctBal = cash
    # acctBal = cash - (cash-nMBP)*2
    # acctBal = float(self.client.get_account().cash)
    self.options['balance'] = acctBal

  def setPosition(self):
    # get stock positions
    try:
      self.options['positions'] = self.client.get_open_position(self.data['stock'])
    except Exception as e:
      # logger.warning(e)
      self.options['positions'] = None
  def setOrders(self):
    # get open orders
    self.options['allOrders'] = self.client.get_orders()
    for x in self.options['allOrders']:
      print(x.symbol, x.qty)
    stock = GetOrdersRequest(symbols=[self.data['stock']])
    # self.options['stockOrders'] = self.client.get_orders(stock)
    self.options['orders'] = self.client.get_orders(stock)

  def setData(self):
    # requests parsed
    if self.req[:3]=='LDC':
      extractedData = re.search(r'(bear|bull|open|close).+?(long|short)?.+[|] (.+)[@]\[*([0-9.]+)\]* [|]', self.req, flags=re.IGNORECASE)
    else:
      extractedData = re.search(r'order (buy|sell) [|] (.+)[@]\[*([0-9.]+)\]* [|]', self.req, flags=re.IGNORECASE)
    if extractedData == None:
      logger.error(f'Failed to extract incoming request data{self.req}')
      # return Response(status=500)
    elif len(extractedData.groups()) == 3:
      self.data = {'action': extractedData.group(1),
      'position': None,
      'stock': extractedData.group(2),
      'price': float(extractedData.group(3))}
    elif len(extractedData.groups()) == 4:
      self.data = {'action': extractedData.group(1),
      'position': extractedData.group(2),
      'stock': extractedData.group(3),
      'price': float(extractedData.group(4))}
    else: 
      logger.error('invalid webhook received')
      print('invalid webhook received')
      
  def cancelAll(self):
    self.canxStatus = self.client.cancel_orders()
  
  def cancelOrderById(self, id=None):
    if not self.options['enabled']:
      value = f'Trading not enable, order not canceled for: {self.data["stock"]}, {self.data["action"]}, {self.data["price"]}'
      logger.debug(value)
      return value
    elif id!=None:
      self.client.cancel_order_by_id(id)
      # self.verifyOrder()
      return
    for x in self.options['orders']:
      self.client.cancel_order_by_id(x.id.hex)
      logger.info(f'Canceled order for: {self.data["stock"]}, {self.data["action"]}, {self.data["position"]}, id: {x.id.hex}')

if __name__ == '__main__':
  # General account info.
  acctInfo()
  app.run(port=5000, debug=False, threaded=True)
  