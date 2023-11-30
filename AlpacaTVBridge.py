from flask import Flask, request, Response
from waitress import serve
from getKeys import getKeys
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest,
    GetOrdersRequest,
    LimitOrderRequest,
)
from alpaca.trading.enums import OrderSide, TimeInForce
import os, logging, re, time, sys, json


try:
    from settings import options
except ModuleNotFoundError:
    from default_settings import options

from Data.get_stock_info import StockUpdater

# Create a logger
logger = logging.getLogger("AlpacaLogger")

# Set the log level to include all messages
logger.setLevel(logging.DEBUG)

# Create a file handler
handler = logging.FileHandler("AlpacaLogger.log")

# Create a formatter and add it to the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Pointer for the type you want to use (real/paper).
account = getKeys(options["using"])
accountReal = getKeys("realTrading")
accountPaper = getKeys("paperTrading")

# Load stocks
path = os.path.dirname(__file__)
with open(path + os.sep + "Data/stocks.json", "r") as f:
    stocks = json.load(f)
# teste = StockUpdater()

# Load settings
def loadSettings(paper, real, using):
    settings = paper.copy()
    for i in real.keys():
        try:
            settings[i]
        except:
            err = f"realTrading/paperTrading setting name discrepancy: '{i}' item in 'realTraing' settings. Please fix the spelling or remove it from realTrading settings."
            raise Exception(err)
    if using != "paperTrading":
        settings.update(options["realTrading"])
    return settings


settings = loadSettings(
    options["paperTrading"], options["realTrading"], options["using"]
)
settingsReal = loadSettings(
    options["paperTrading"], options["realTrading"], "realTrading"
)
settingsPaper = loadSettings(
    options["paperTrading"], options["realTrading"], "paperTrading"
)

# Check for configuration conflict that could cause unintended buying or errors.
if settings["enabled"] and settings["testMode"] and options["using"] == "realTrading":
    err = "testMode and real money keys being used, exiting. Change one or the other."
    raise Exception(err)
elif settings["fractional"] and settings["limit"]:
    err = (
        "fractional and limit can't be used together, exiting. Change one or the other."
    )
    raise Exception(err)

app = Flask(__name__)

# data examples from pine script strategy alerts:
# Compatible with 'Machine Learning: Lorentzian Classification' indicator alerts
# LDC Kernel Bullish ▲ | CLSK@4.015 | (1)...
# Also compatible with custom stratedy alerts (ex. strategy.entry, strategy.close_all, etc.)
# order sell | MSFT@337.57 | Directional Movement Index...


def acctInfo():
    temp = TradingClient(**account).get_account()
    print(f'***account: {"PAPER" if account["paper"] else "REAL MONEY"}')
    print(f"status: {temp.status}")
    print(f"account blocked: {temp.account_blocked}")
    print(f"trade_suspended_by_user: {temp.trade_suspended_by_user}")
    print(f"trading_blocked: {temp.trading_blocked}")
    print(f"transfers_blocked: {temp.transfers_blocked}")
    print(f"equity: {temp.equity}")
    print(f"currency: {temp.currency}")
    print(f"cash: {temp.cash}")
    print(f"buying_power: {temp.buying_power}")
    print(f"daytrading_buying_power: {temp.daytrading_buying_power}")
    print(f"shorting_enabled: {temp.shorting_enabled}")
    print(f"crypto_status: {temp.crypto_status}")
    try:
        print(f"Program argurment: {sys.argv[1]}")
    except:
        print(f"Program argurment: None")
    print("-------------------------------------------------")


@app.route("/", methods=["POST"])
def respond():
    req_data = str(request.data)
    logger.info(f"Recieved request with data: {req_data}")
    trader = AutomatedTrader(req=req_data)

    return Response(status=200)


class AutomatedTrader:
    """Trader client and functions for buying, selling, and validating of
    orders.'req' is the request that needs to be processed.
    """

    def __init__(self, testAccount=None, req="", newOptions={}):
        global settings
        global settingsPaper
        global settingsReal
        global account
        global accountReal
        global accountPaper
        global stocks
        self.testAccount = testAccount
        self.asset = None
        self.options = {
            # Gets open potisions for specific stock to verify ordering. Multiple buys before selling not implemented yet.
            "positions": [],
            # Gets all open positions.
            "allPositions": [],
            # Retrieves open orders is there are any for the symbol requested.
            "orders": [],
            # Gets all the open orders.
            "allOrders": [],
        }
        
        # Set request data and stock info.
        self.req = req
        self.setData()
        self.setStockInfo()
        
        # Use settings if they were imported successfully. More of a debug test since it fails if it's not there and it should be there.
        # self.options.update(settings)
        self.client = self.createClientAndSettings()
        # Count the items in options and if newOptions increases it, raise an exception.
        optCnt = len(self.options)
        self.options.update(newOptions)
        if len(self.options) != optCnt:
            raise Exception(
                "Extra options found. Verify newOption keys match option keys"
            )
        # Verify 'enabled' option is True. Used primarily for unittesting.
        if self.options["enabled"]:
            self.setOrders()
            self.setPosition()
            self.setAllPositions()
            self.setBalance()
            self.createOrder()

    def createClientAndSettings(self):
        # Creates the trading client based on real or paper account.
        if self.testAccount != None:
            self.options.update(settingsPaper) if self.testAccount['paper'] else self.options.update(settingsReal)
            return TradingClient(**self.testAccount)
        elif not settings["perStockPreference"]:
            self.options.update(settings)
            return TradingClient(**account)
            
        try:
            if self.asset['account']=='':
                self.options.update(settings)
                return TradingClient(**account)
            elif self.asset['account'].upper()=='real'.upper():
                self.options.update(settingsReal)
                return TradingClient(**accountReal)
            elif self.asset['account'].upper()=='paper'.upper():
                self.options.update(settingsPaper)
                return TradingClient(**accountPaper)
            else:
                logger.warning(f'Invalid stock account setting in stocks.json: {self.data["stock"]}. Defaulting to user settings.')
                self.options.update(settings)
                return TradingClient(**account)
        except TypeError:
                self.options.update(settings)
                return TradingClient(**account)

    def setData(self):
        # requests parsed for either Machine Learning: Lorentzian
        # Classification or custom alerts (noted in documentation how to setup).
        if self.req[:3] == "LDC":
            extractedData = re.search(
                # regex
                r"(bear|bull|open|close).+?(long|short)?.+[|] (.+)[@]\[*([0-9.]+)\]* [|]",
                self.req,
                flags=re.IGNORECASE,
            )
        else:
            extractedData = re.search(
                r"order (buy|sell) [|] (.+)[@]\[*([0-9.]+)\]* [|]",
                self.req,
                flags=re.IGNORECASE,
            )
        if extractedData == None:
            logger.error(f"Failed to extract incoming request data: {self.req}")
            raise Exception(f"Failed to extract incoming request data: {self.req}")
            # return Response(status=500)
        elif len(extractedData.groups()) == 3:
            self.data = {
                "action": extractedData.group(1),
                "position": None,
                "stock": extractedData.group(2),
                "price": float(extractedData.group(3)),
            }
        elif len(extractedData.groups()) == 4:
            self.data = {
                "action": extractedData.group(1),
                "position": extractedData.group(2),
                "stock": extractedData.group(3),
                "price": float(extractedData.group(4)),
            }
        else:
            err = f"invalid webhook received: {self.req}"
            logger.error(err)
            print(err)

    def setOrders(self):
        # get open orders
        stock = GetOrdersRequest(symbols=[self.data["stock"]])
        self.options["orders"] = self.client.get_orders(stock)

    def setStockInfo(self):
        for item in stocks:
            if item['symbol']==self.data['stock']:
                self.asset = item
                break

    def setPosition(self):
        # get stock positions
        try:
            self.options["positions"] = self.client.get_open_position(
                self.data["stock"]
            )
        except Exception as e:
            self.options["positions"] = None

    def setAllPositions(self):
        self.options["allPositions"] = self.client.get_all_positions()

    def setBalance(self):
        # set balance at beginning and after each transaction
        cash = float(self.client.get_account().cash)
        # nMBP = float(self.client.get_account().non_marginable_buying_power)
        acctBal = cash
        # acctBal = cash - (cash-nMBP)*2
        # acctBal = float(self.client.get_account().cash)
        self.options["balance"] = acctBal

    def createOrder(self):
        # Setup for creating and verifying orders

        # Clear uncompleted open orders. Shouldn't be any unless trading is unavailable...
        if len(self.options["orders"]) > 0:
            self.cancelOrderById()

        if self.options["testMode"]:
            # Testing with preset variables.
            self.options["balance"] = 100000
        # Check for negative balance.
        elif self.options["balance"] < 0:
            logger.warning(f'Negative balance: {self.options["balance"]}')
            self.options["balance"] = 0
        # Check and set balace for set value per trade.
        elif self.options["buyPerc"] == 0 and self.options["buyAmt"] > 0:
            self.options["balance"] = self.options["buyAmt"]

        if self.options["fractional"]:
            # Fractional shares to buy.
            amount = float(
                self.options["balance"] * self.options["buyPerc"] / self.data["price"]
                if self.options["buyPerc"] > 0
                else self.options["buyAmt"] / self.data["price"]
            )
        else:
            # Whole number shares to buy if fractional is not enabled. Rounds down.
            amount = int(
                self.options["balance"] * self.options["buyPerc"] / self.data["price"]
                if self.options["buyPerc"] > 0
                else self.options["buyAmt"] / self.data["price"]
            )

        # get position quantity
        posQty = (
            float(self.options["positions"].qty)
            if self.options["positions"] != None
            else 0
        )

        # Setup for buy/sell/open/close/bear/bull/short/long.
        # Open a short position.
        if self.data["action"] == "Open" and self.data["position"] == "Short":
            side = OrderSide.SELL
            # Close if shorting not enabled. Need to adjust for positive and negative positions. Done?
            if posQty < 0:
                logger.debug(f'Already shorted for: {self.data["stock"]}')
                amount = 0
                return
            if not self.options["short"] and posQty == 0:
                logger.info(
                    f'Shorting not enabled for: {self.data["stock"]}, {self.data["action"]}, {self.data["position"]}'
                )
                amount = 0
            elif not self.options["short"] and posQty > 0:
                logger.info(
                    f'Selling all positions. Shorting not enabled for: {self.data["stock"]}, {self.data["action"]}, {self.data["position"]}'
                )
                amount = posQty
            elif self.options["short"] and posQty > 0:
                # Can't short with long positions so need to figure out how to sell to 0 then short and vice versa.
                amount = posQty
            elif self.options["short"] and posQty == 0:
                pass
            elif self.options["short"] and posQty < 0:
                logger.info(
                    f'Already shorted for: {self.data["stock"]}, {self.data["action"]}, {self.data["position"]}'
                )
                amount = 0
                return
        # Close a short position.
        elif self.data["action"] == "Close" and self.data["position"] == "Short":
            side = OrderSide.BUY
            # Close positions for symbol
            if posQty > 0:
                logger.debug(
                    f'Short not needed. Already long for: {self.data["stock"]}'
                )
                amount = 0
                return
            elif posQty == 0:
                pass
            elif posQty < 0:
                amount = abs(posQty)
        # Open a long position.
        elif (
            self.data["action"].upper() == "Bull".upper()
            or self.data["action"].upper() == "buy".upper()
            or self.data["action"].upper() == "Open".upper()
        ) and (self.data["position"] == "Long" or self.data["position"] == None):
            side = OrderSide.BUY
            if self.options["positions"] != None:
                amount = 0
        # Close a long position.
        elif (
            self.data["action"].upper() == "Bear".upper()
            or self.data["action"].upper() == "sell".upper()
            or self.data["action"].upper() == "Close".upper()
        ) and (self.data["position"] == "Long" or self.data["position"] == None):
            side = OrderSide.SELL
            # Close positions for symbol. Setting to 0 so it won't run if there's already a position.
            amount = 0
            if self.options["positions"] != None and posQty > 0:
                amount += posQty
            # need to add short depending if shorting is enabled. Not needed?
            # if not self.options['short']:
            #   logger.info(f'Shorting not enabled for: {self.data["stock"]}, action: {self.data["action"]}, price: {self.data["price"]}, quantity: {self.order_data.qty}')
            #   return
        # Unhandled edge case.
        else:
            logger.error(
                f'Unhandled Order: {self.data["stock"]}, action: {self.data["action"]}, price: {self.data["price"]}'
            )
            raise ValueError(
                f'Unhandled action and/or position: {self.data["stock"]}, action: {self.data["action"]}, price: {self.data["price"]}'
            )

        # return if 0 shares are to be bought. Basically not enough left over for buying 1 share or more
        if amount == 0:
            logger.info(
                f'0 Orders requested: {self.data["stock"]}, action: {self.data["action"]}, price: {self.data["price"]}'
            )
            return
        # return if less then 0 shares are to be bought. Shouldn't happen right now
        elif amount < 0:
            logger.info(
                f'<0 Orders requested: {self.data["stock"]}, {self.data["action"]}, {self.data["price"]}, amount: {amount}'
            )
            return
        self.orderType(amount, side, self.options["limit"])
        self.submitOrder()

    def orderType(self, amount, side, limit):
        # Setup buy/sell order
        # Determine if using fractional amount of shares to buy.
        fractional = int(amount) != float(amount)
        # Market order if "limit" setting set to False
        if not limit:
            order_data = MarketOrderRequest(
                symbol=self.data["stock"],  # "MSFT"
                qty=amount,  # 100
                side=side,
                time_in_force=TimeInForce.DAY if fractional else TimeInForce.GTC,
            )
        # Limit order if "limit" setting set to True
        elif limit:
            # Predefined price to override limitAmt with limitPerc*price
            if self.data["price"] > self.options["limitThreshold"]:
                self.options["limitAmt"] = (
                    self.data["price"] * self.options["limitPerc"]
                )
            order_data = LimitOrderRequest(
                symbol=self.data["stock"],  # "MSFT"
                limit_price=round(
                    self.data["price"]
                    + (
                        self.options["limitAmt"]
                        if side == OrderSide.BUY
                        else -self.options["limitAmt"]
                    ),
                    2,
                ),
                qty=amount,  # amount of stock to buy.
                side=side,
                time_in_force=TimeInForce.DAY if fractional else TimeInForce.GTC,
            )
        self.order_data = order_data

    def submitOrder(self):
        try:
            self.order_data
        except AttributeError:
            return

        # Logic to factor in max position if enabled. Creates a log warning if positions exceed max. If it's at the max it won't buy
        if self.order_data.side == OrderSide.BUY:
            if self.options["maxPositions"] == 0:
                pass
            elif len(self.options["allPositions"]) > self.options["maxPositions"]:
                err = f'Over max positions: max positions - {self.options["maxPositions"]}, current positions - {[x.symbol for x in self.options["allPositions"]]}'
                logger.warning(err)
                raise Exception(err)
                return False
            elif len(self.options["allPositions"]) == self.options["maxPositions"]:
                logger.info(
                    f'At Max Positions. Order not created for: {self.data["stock"]}, {self.data["action"]}, {self.data["position"]}'
                )
                return False

        # escape and don't actually submit order if not enabled. For debugging/testing purposes.
        if not self.options["enabled"]:
            logger.debug(
                f'Not enabled, order not placed for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
            )
            return
        # Submit order
        self.order = self.client.submit_order(self.order_data)
        if self.options["verifyOrders"]:
            self.verifyOrder(self.order)
        # Need to add while look that checks if the order finished. if limit sell failed, change to market order or something like that. For buy just cancel or maybe open limit then cancel?

    def verifyOrder(self, order=None, timeout=False):
        # Verify order exited in 1 of 3 ways (cancel, fail, fill).
        # TODO: Need to add async stream method for checking for order completion.
        maxTime = self.options["maxTime"]
        totalMaxTime = self.options["totalMaxTime"]
        orderSideBuy = str(order.side) == "OrderSide.BUY"
        orderSideSell = str(order.side) == "OrderSide.SELL"
        now = time.time()
        id = order.client_order_id
        # While loop that checks the order status every 1 second.
        while (
            order.filled_at is None
            and order.failed_at is None
            and order.canceled_at is None
        ):
            if time.time() - now > maxTime and not timeout:
                logger.debug(
                    f'Order exeeded max time ({maxTime} seconds) for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
                )
                # Cancels order after initial maxtime. Determined in settings
                if (self.options["buyTimeout"] == "Cancel" and orderSideBuy) or (
                    self.options["sellTimeout"] == "Cancel" and orderSideSell
                ):
                    # cancel pending order
                    self.cancelOrderById(order.id.hex)
                    # Refreshes status of order before verifying to speed up the process.
                    order = self.client.get_order_by_client_id(id)
                    timeout = True
                    # verify canceled order
                    if not self.verifyOrder(order, True):
                        err = "cancel order failed"
                        logger.debug(
                            f'Order cancel failed for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
                        )
                        raise Exception(err)
                    else:
                        # competed at this point and returns True to indicate cancel was successful
                        return True
                # Changes order to market after initial maxtime. Determined in settings
                elif (self.options["buyTimeout"] == "Market" and orderSideBuy) or (
                    self.options["sellTimeout"] == "Market" and orderSideSell
                ):
                    # cancel pending order
                    self.cancelOrderById(order.id.hex)
                    # Refreshes status of order before verifying to speed up the process.
                    order = self.client.get_order_by_client_id(id)
                    timeout = True
                    # verify canceled order
                    if self.verifyOrder(order, True):
                        # Once order is canceled, find how many didn't get filled for new market order
                        amount = float(order.qty) - float(order.filled_qty)
                        # Set the new order. This will also set the new self.order_data based on the prior order info, the updated amount left to buy/sell, and False for limit to make it a market order.
                        self.orderType(amount, order.side, False)
                        # Submit the order and udpate the local variable.
                        order = self.client.submit_order(self.order_data)
                        logger.debug(
                            f'Timeout market order placed for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
                        )
                        # Verify new order completion.
                        if self.verifyOrder(order, True):
                            logger.debug(
                                f'Timeout market order succeeded for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
                            )
                            return True
                        else:
                            err = "market order failed"
                            logger.debug(
                                f'Timeout market order failed for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
                            )
                            return False
                    else:
                        err = "cancel order failed"
                        logger.debug(
                            f'Order cancel failed for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
                        )
                        raise Exception(err)
                else:
                    err = "buy or sell timeout setting not found. Check the spelling in the settings and relaunch the server"
                    self.cancelOrderById(order.id.hex)
                    logger.error(err)
                    raise Exception(err)
            elif time.time() - now > totalMaxTime:
                self.cancelOrderById(order.id.hex)
                # failsafe to exit loop
                logger.warning(
                    f'Cancelling, order exeeded totalMaxTime ({totalMaxTime} seconds) for: action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
                )
                # Refreshes status of order before verifying to speed up the process.
                order = self.client.get_order_by_client_id(id)
                timeout = True
                if self.verifyOrder(order, True):
                    logger.debug(
                        f'maxTimeout order successfully canceled for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
                    )
                    return False
                else:
                    err = f'maxTimeout order cancel failed for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
                    logger.debug(
                        f'Timeout market order failed for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
                    )
                    return False
            time.sleep(1)
            order = self.client.get_order_by_client_id(id)

        if order.canceled_at is not None:
            logger.debug(
                f'Order canceled for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
            )
            return True
        elif order.failed_at is not None:
            logger.warning(
                f'Order failed for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
            )
            return False
        elif order.filled_at is not None:
            logger.info(
                f'Order filled for: {self.data["stock"]}, action: {self.data["action"]} {self.order_data.type._value_}, price: {self.data["price"]}, quantity: {self.order_data.qty}'
            )
            return True

    def cancelOrderById(self, id=None):
        if not self.options["enabled"]:
            value = f'Trading not enabled, order not canceled for: {self.data["stock"]}, {self.data["action"]} {self.order_data.type._value_}, {self.data["price"]}'
            logger.debug(value)
            return value
        elif id != None:
            self.client.cancel_order_by_id(id)
            # self.verifyOrder()
            return
        for x in self.options["orders"]:
            self.client.cancel_order_by_id(x.id.hex)
            logger.info(
                f'Canceled order for: {self.data["stock"]}, {self.data["action"]}, {self.data["position"]}, id: {x.id.hex}'
            )

    def cancelAll(self):
        # Not used
        self.canxStatus = self.client.cancel_orders()


if __name__ == "__main__":
    # Display general account info.
    acctInfo()
    # Start the app
    try:
        if sys.argv[1] == "serveTV":
            serve(app, port=5000, threads=4, host="0.0.0.0")
        else:
            serve(app, port=5000, threads=4, host="127.0.0.1")
    except IndexError:
        serve(app, port=5000, threads=4, host="127.0.0.1")
