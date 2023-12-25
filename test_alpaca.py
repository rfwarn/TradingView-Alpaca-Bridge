from AlpacaTVBridge import AutomatedTrader, getKeys, loadSettings
from filePath import filePath
import unittest, os, json, pytest

try:
    from settings import options
except:
    from default_settings import options

paperTrading = getKeys("paperTrading")
realTrading = getKeys("realTrading")
path = filePath()

limitTests = (
    "order sell | MSFT@433.02 | Directional Movement Index",
    "order buy | MSFT@227.52 | Directional Movement Index",
)

marketLDC = {
    "Bull": "LDC Kernel Bullish \xe2\x96\xb2 | CLSK@4.015 | (1) TEST",
    "Bear": "LDC Kernel Bearish \xe2\x96\xb2 | CLSK@4.015 | (1) TEST",
    "Open": "LDC Open Long \xe2\x96\xb2 | MSFT@327.30 | (1) TEST",
    "OpenCLSK": "LDC Open Long \xe2\x96\xb2 | CLSK@3.83 | (1) TEST",
    "OpenFCEL": "LDC Open Long \xe2\x96\xb2 | FCEL@23.30 | (1) TEST",
    "Close": "LDC Close Short \xe2\x96\xb2 | CLSK@4.01 | (1) TEST",
    "Short": "LDC Open Short \xe2\x96\xb2 | CLSK@4.015 | (1) TEST",
    "ShortFCEL": "LDC Open Short \xe2\x96\xb2 | FCEL@2.47 | (1) TEST",
    "ShortMSFT": "LDC Open Short \xe2\x96\xb2 | MSFT@327.30 | (1) TEST",
    "Long": "LDC Close Long \xe2\x96\xb2 | CLSK@4.015 | (1) TEST",
    "LongFCEL": "LDC Close Long \xe2\x96\xb2 | FCEL@23.30 | (1) TEST",
    "Position": "LDC Open Position \xe2\x96\xb2 | CLSK@4.015 | (1) TEST",
    "CPositionNVDA": "LDC Close Position  \xe2\x96\xb2\xe2\x96\xbc | NVDA@[386.78] | (1) TEST",
}


class TestAlpaca(unittest.TestCase):
    # realClient = AutomatedTrader(realTrading, newOptions={})
    paperClient = AutomatedTrader(
        paperTrading, req=marketLDC["Long"], newOptions={"enabled": False, "perStockPreference": False}
    )

    fastTiming = {"maxTime": 3, "totalMaxTime": 4}

    class DebugPos:
        symbol = "testing"

    p1 = DebugPos()
    debugPositions = [p1, p1]
    # [x.symbol for x in self.options["allPositions"]]

    # For debugging
    # def setUp(self):
    #   print("In method", self._testMethodName)

    def test_settings(self):
        # Verify settings file can be loaded properly
        setcheck = [options["paperTrading"]]
        for x in setcheck:
            self.assertEqual(type(x["testMode"]), bool)
            self.assertEqual(type(x["limit"]), bool)
            self.assertEqual(type(x["buyPerc"]), float)
        optionsChk = options["realTrading"].copy()
        optionsChk["asdf"] = "testfail"
        with self.assertRaises(Exception):
            loadSettings(options["paperTrading"], optionsChk, "realTrading")

    def test_extraOptions(self):
        # Test for typos in newOptions which would have unintended effects.
        with self.assertRaises(Exception):
            AutomatedTrader(
                paperTrading,
                req="order sell | MSFT@337.57 | TEST",
                newOptions={"enabled": True, "newVal": True},
            )

    def test_failsafe(self):
        # Test failsafe that prevents trading if testMode is enabled when using real money. testMode uses a default cash amount which can cause real problems if not using a paper account.
        with self.assertRaises(Exception):
            AutomatedTrader(
                realTrading, req="", newOptions={"enabled": True, "testMode": True, "perStockPreference": False}
            )

    def test_fractionalLimit(self):
        # Test failsafe that prevents trying to place an order as a limit with fractional enabled which Alpaca does not support.
        with self.assertRaises(Exception):
            AutomatedTrader(
                realTrading, req="", newOptions={"fractional": True, "limit": True, "perStockPreference": False}
            )

    def test_validateRealKeys(self):
        # Test to see if keys are valid
        AutomatedTrader(
            realTrading,
            req="order sell | MSFT@337.57 | TEST",
            newOptions={"enabled": False, "perStockPreference": False},
        )

    def test_data1(self):
        # Testing of the different predefined alert types.
        result = AutomatedTrader(
            paperTrading,
            req="order sell | MSFT@337.57 | TEST",
            newOptions={"enabled": False, "perStockPreference": False},
        )
        result.setData()
        self.assertEqual(result.data["action"], "sell")
        self.assertEqual(result.data["position"], None)
        self.assertEqual(result.data["stock"], "MSFT")
        self.assertEqual(result.data["price"], 337.57)

    def test_data2(self):
        result = AutomatedTrader(
            paperTrading,
            req="order buy | MSFT@337.57 | TEST",
            newOptions={"enabled": False, "perStockPreference": False},
        )
        result.setData()
        self.assertEqual(result.data["action"], "buy")
        self.assertEqual(result.data["position"], None)
        self.assertEqual(result.data["stock"], "MSFT")
        self.assertEqual(result.data["price"], 337.57)

    def test_data3(self):
        result = AutomatedTrader(
            paperTrading, req=marketLDC["Bear"], newOptions={"enabled": False, "perStockPreference": False}
        )
        result.setData()
        self.assertEqual(result.data["action"], "Bear")
        self.assertEqual(result.data["position"], None)
        self.assertEqual(result.data["stock"], "CLSK")
        self.assertEqual(result.data["price"], 4.015)

    def test_data4(self):
        result = AutomatedTrader(
            paperTrading, req=marketLDC["Bull"], newOptions={"enabled": False, "perStockPreference": False}
        )
        result.setData()
        self.assertEqual(result.data["action"], "Bull")
        self.assertEqual(result.data["position"], None)
        self.assertEqual(result.data["stock"], "CLSK")
        self.assertEqual(result.data["price"], 4.015)

    def test_data5(self):
        result = AutomatedTrader(
            paperTrading, req=marketLDC["Open"], newOptions={"enabled": False, "perStockPreference": False}
        )
        result.setData()
        self.assertEqual(result.data["action"], "Open")
        # self.assertEqual(result.data["position"], "Long")
        self.assertEqual(result.data["position"], "Long".upper())
        self.assertEqual(result.data["stock"], "MSFT")
        self.assertEqual(result.data["price"], 327.3)

    def test_data6(self):
        result = AutomatedTrader(
            paperTrading, req=marketLDC["Long"], newOptions={"enabled": False, "perStockPreference": False}
        )
        result.setData()
        self.assertEqual(result.data["action"], "Close")
        # self.assertEqual(result.data["position"], "Long")
        self.assertEqual(result.data["position"], "Long".upper())
        self.assertEqual(result.data["stock"], "CLSK")
        self.assertEqual(result.data["price"], 4.015)

    def test_data7(self):
        result = AutomatedTrader(
            paperTrading, req=marketLDC["Short"], newOptions={"enabled": False, "perStockPreference": False}
        )
        result.setData()
        self.assertEqual(result.data["action"], "Open")
        # self.assertEqual(result.data["position"], "Short")
        self.assertEqual(result.data["position"], "Short".upper())
        self.assertEqual(result.data["stock"], "CLSK")
        self.assertEqual(result.data["price"], 4.015)

    def test_data8(self):
        result = AutomatedTrader(
            paperTrading, req=marketLDC["Close"], newOptions={"enabled": False, "perStockPreference": False}
        )
        result.setData()
        self.assertEqual(result.data["action"], "Close")
        # self.assertEqual(result.data["position"], "Short")
        self.assertEqual(result.data["position"], "Short".upper())
        self.assertEqual(result.data["stock"], "CLSK")
        self.assertEqual(result.data["price"], 4.01)

    def test_orders(self):
        self.paperClient.setData()
        self.paperClient.setOrders()
        self.assertEqual(type(self.paperClient.options["orders"]), list)

    def test_balance(self):
        result = AutomatedTrader(
            paperTrading,
            req=marketLDC["Close"],
            newOptions={"enabled": False, "testMode": True, "perStockPreference": False},
        )
        result.setBalance()

    def test_createLimitOrder(self):
        result = AutomatedTrader(
            paperTrading,
            req=marketLDC["OpenFCEL"],
            newOptions={"enabled": False, "limit": True, "fractional": False, 
                "testMode": True,
                "perStockPreference": False,
                "perStockAmount": False,
                "perStockAmountCompounding": False,},
        )
        limitPrice = 23.3 + options["paperTrading"]["limitAmt"]
        result.setData()
        result.setPosition()
        result.createOrder()
        self.assertEqual(result.order_data.limit_price, limitPrice)
        self.assertEqual(result.order_data.qty, 858.0)
        self.assertEqual(result.order_data.symbol, "FCEL")

    def test_createMarketOrder(self):
        result = AutomatedTrader(
            paperTrading,
            req=marketLDC["OpenFCEL"],
            newOptions={"enabled": False, "limit": False, "fractional": False,
                "testMode": True,
                "perStockPreference": False,
                "perStockAmount": False,
                "perStockAmountCompounding": False,},
        )
        result.setData()
        result.setPosition()
        result.createOrder()
        self.assertEqual(result.order_data.qty, 858.0)
        self.assertEqual(result.order_data.symbol, "FCEL")
        with self.assertRaises(AttributeError):
            result.order_data.limit_price

    def test_createMarketOrderBuy(self):
        result = AutomatedTrader(
            paperTrading,
            req="order buy | MSFT@233.41 | Strat buy TEST",
            # req="order buy | CLSK@5.965 | Strat buy TEST",
            newOptions={
                "enabled": True,
                "limit": False,
                "buyTimeout": "Cancel",
                "fractional": True, 
                "perStockPreference": False,
                **self.fastTiming,
            },
        )
        result.setData()
        result.setPosition()
        result.createOrder()

    def test_createMarketOrderSell(self):
        result = AutomatedTrader(
            paperTrading,
            req="order sell | MSFT@233.41 | Close position TEST",
            # req="order sell | CLSK@5.965 | Close position TEST",
            newOptions={
                "enabled": True,
                "limit": False,
                "buyTimeout": "Market",
                "perStockPreference": False,
                "fractional": False,
                **self.fastTiming,
            },
        )
        result.setData()
        result.setPosition()
        result.createOrder()

    def test_createLimitOrderBuy(self):
        result = AutomatedTrader(
            paperTrading,
            req="order buy | MSFT@233.41 | Strat buy TEST",
            # req="order buy | CLSK@5.965 | Strat buy TEST",
            newOptions={
                "enabled": True,
                "limit": True, 
                "perStockPreference": False,
                "buyTimeout": "Market",
                **self.fastTiming,
            },
        )
        result.setData()
        result.setPosition()
        result.createOrder()

    def test_createLimitOrderSell(self):
        result = AutomatedTrader(
            paperTrading,
            # req="order sell | CLSK@5.965 | Close position TEST",
            req="order sell | MSFT@233.41 | Close position TEST",
            newOptions={
                "enabled": True,
                "limit": True,
                "buyTimeout": "Market", 
                "perStockPreference": False,
                "fractional": False,
                **self.fastTiming,
            },
        )
        result.setData()
        result.setPosition()
        result.createOrder()

    def test_badRequest(self):
        with self.assertRaises(Exception):
            result = AutomatedTrader(
                paperTrading,
                req="123 TEST",
                newOptions={"enabled": True, "limit": False, "perStockPreference": False},
            )
            result.setData()

    def test_buyAmt(self):
        result = AutomatedTrader(
            paperTrading,
            req="order buy | MSFT@233.41 | Strat buy TEST",
            newOptions={
                "enabled": False,
                "buyPerc": 0,
                "buyAmt": 2000,
                "testMode": False,
                "limit": False,
                "fractional": True, 
                "perStockPreference": False,
                **self.fastTiming,
            },
        )
        result.setData()
        result.setPosition()
        result.createOrder()
        self.assertEqual(result.order_data.qty, 8.568613169958443)

    def test_MaxPos1(self):
        result = AutomatedTrader(
            paperTrading,
            req="order buy | MSFT@233.41 | Strat buy TEST",
            newOptions={
                "enabled": False,
                "limit": False,
                "fractional": False,
                "testMode": True,
                "maxPositions": 0,
                "perStockPreference": False,
                "perStockAmount": False,
                "perStockAmountCompounding": False,
                "allPositions": self.debugPositions,
                **self.fastTiming,
            },
        )
        result.setData()
        result.setPosition()
        result.createOrder()

    def test_MaxPos2(self):
        result = AutomatedTrader(
            paperTrading,
            req="order buy | MSFT@233.41 | Strat buy TEST",
            newOptions={
                "enabled": False,
                "limit": False,
                "fractional": False,
                "testMode": True,
                "maxPositions": 2,
                "perStockPreference": False,
                "perStockAmount": False,
                "perStockAmountCompounding": False,
                "allPositions": self.debugPositions,
                **self.fastTiming,
            },
        )
        result.setData()
        result.setPosition()
        result.createOrder()

    def test_MaxPos3(self):
        result = AutomatedTrader(
            paperTrading,
            req="order buy | MSFT@233.41 | Strat buy TEST",
            newOptions={
                "enabled": False,
                "limit": False,
                "fractional": False,
                "testMode": True,
                "maxPositions": 1,
                "perStockPreference": False,
                "perStockAmount": False,
                "perStockAmountCompounding": False,
                "allPositions": self.debugPositions,
                **self.fastTiming,
            },
        )
        result.setData()
        result.setPosition()
        with self.assertRaises(Exception):
            result.createOrder()

    def test_MaxPos4(self):
        result = AutomatedTrader(
            paperTrading,
            req="order sell | MSFT@233.41 | Strat sell TEST",
            newOptions={
                "enabled": False,
                "limit": False,
                "fractional": False,
                "testMode": True,
                "maxPositions": 1,
                "perStockPreference": False,
                "perStockAmount": False,
                "perStockAmountCompounding": False,
                "allPositions": self.debugPositions,
                **self.fastTiming,
            },
        )
        result.setData()
        result.setPosition()
        result.createOrder()

    def test_stockPrefAmount(self):
        result = AutomatedTrader(
            paperTrading,
            req="order buy | MSFT@368.31 | Strat buy TEST",
            newOptions={
                "enabled": False,
                "limit": False,
                "testMode": False,
                "buyPerc": 0,
                "buyAmt": 2000,
                "fractional": False,
                "perStockPreference": False,
                "perStockAmount": True,
                **self.fastTiming,
            },
            testStocklist=[{
        "id": "b6d1aa75-5c9c-4353-a305-9e2caa1925ab",
        "class": "us_equity",
        "exchange": "NASDAQ",
        "symbol": "MSFT",
        "name": "Microsoft Corporation Common Stock",
        "status": "active",
        "tradable": True,
        "marginable": True,
        "maintenance_margin_requirement": 30,
        "shortable": True,
        "easy_to_borrow": True,
        "fractionable": True,
        "attributes": [],
        "account": "",
        "amount": 1000
    }]
        )
        result.setData()
        result.setPosition()
        result.createOrder()
        self.assertEqual(result.order_data.qty, 2)
        self.assertEqual(result.options['buyAmt'], 1000)

    def test_stockPrefAmountCompound(self):
        result = AutomatedTrader(
            paperTrading,
            req="order buy | MSFT@368.31 | Strat buy TEST",
            newOptions={
                "enabled": False,
                "limit": False,
                "testMode": False,
                "buyPerc": 0,
                "buyAmt": 2000,
                "fractional": False,
                "perStockPreference": False,
                "perStockAmount": True,
                **self.fastTiming,
            },
            testStocklist=[{
        "id": "b6d1aa75-5c9c-4353-a305-9e2caa1925ab",
        "class": "us_equity",
        "exchange": "NASDAQ",
        "symbol": "MSFT",
        "name": "Microsoft Corporation Common Stock",
        "status": "active",
        "tradable": True,
        "marginable": True,
        "maintenance_margin_requirement": 30,
        "shortable": True,
        "easy_to_borrow": True,
        "fractionable": True,
        "attributes": [],
        "account": "",
        "amount": 1000
    }]
        )
        result.setData()
        result.setPosition()
        result.createOrder()
        result.newOrders['amount'] = 1200
        result.updateStockAmount()
        self.assertEqual(result.order_data.qty, 2)
        self.assertEqual(result.asset["amount"], 1200)

    # maxTimeout failsafes
    # def test_limitBuyTimeoutCancel(self):
    #     result = AutomatedTrader(
    #         paperTrading,
    #         req=limitTests[1],
    #         newOptions={"enabled": True, "limit": True, "buyTimeout": "Cancel"}
    #     )

    # def test_limitBuyTimeoutMarket(self):
    #     result = AutomatedTrader(
    #         paperTrading,
    #         req=limitTests[1],
    #         newOptions={"enabled": True, "limit": True, "buyTimeout": "Market"}
    #     )

    # def test_limitSellTimeoutMarket(self):
    #     result = AutomatedTrader(
    #         paperTrading,
    #         req=limitTests[1],
    #         newOptions={"enabled": True, "limit": True, "sellTimeout": "Market"}
    #     )


if __name__ == "__main__":
    # unittest.main()
    pytest.main()
    # pytest test_alpaca.py::TestAlpaca::test_buyAmt
