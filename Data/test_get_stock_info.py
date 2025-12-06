from Data.get_stock_info import StockUpdater, getListOrString, main
from Data import sql
import os
import tempfile
from unittest.mock import patch, MagicMock

# from get_stock_info import StockUpdater, getListOrString, main

# Use a temporary test database
test_db_path = None

def setup_module():
    """Setup test database before running tests."""
    global test_db_path
    # Create a temporary database file
    fd, test_db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    # Override the database path
    sql.db_path = test_db_path
    sql.init_DB()

def teardown_module():
    """Cleanup test database after tests."""
    global test_db_path
    sql.close_DB()
    if test_db_path and os.path.exists(test_db_path):
        os.remove(test_db_path)

def clear_database():
    """Clear all data from the test database."""
    conn = sql.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM stocks")
    conn.commit()

def get_mock_stock_data(symbol):
    """Create mock stock data without calling API."""
    return {
        "symbol": symbol.upper(),
        "name": f"{symbol.upper()} Test Company",
        "fractionable": True,
        "shortable": True,
        "easy_to_borrow": True,
        "status": "active",
        "tradable": True
    }

stockUpdater = StockUpdater(write=True, loadSL=False)
SL = []


def test_get_stock_info():
    # Test to get the stock info and add it to the list as an object with blank account
    # information ('') if not already present.
    clear_database()
    stockUpdater.stocklist = []
    # Use mock data instead of API call
    mock_data = get_mock_stock_data("goog")
    stockUpdater.updateStockInfo(mock_data)
    stockUpdater.getStockList()  # Reload from DB
    assert stockUpdater.stocklist[0]["account"] == ""
    assert stockUpdater.stocklist[0]["symbol"] == "GOOG"


def test_get_list_or_string():
    # Test to make sure that getListOrString() returns a list of strings or a single
    # string, depending on the input.
    newArgs = getListOrString("goog")
    assert type(newArgs) is str
    newArgs = getListOrString(["goog"])
    assert type(newArgs) is str
    newArgs = getListOrString('["goog"]')
    assert type(newArgs) is list
    assert newArgs[0] == "GOOG"
    newArgs = getListOrString("goog, aapl")
    assert type(newArgs) is list
    assert newArgs[0] == "GOOG"
    newArgs = getListOrString("'goog', 'aapl'")
    assert type(newArgs) is list
    assert newArgs[0] == "GOOG"
    newArgs = getListOrString(["goog", "aapl"])
    assert type(newArgs) is list
    assert newArgs[0] == "GOOG"
    newArgs = getListOrString('["goog", "aapl"]')
    assert type(newArgs) is list
    assert newArgs[0] == "GOOG"
    assert len(newArgs) == 2
    assert type(newArgs) is list
    assert newArgs[0] == "GOOG"
    assert len(newArgs) == 2
    long = "[AAPL,'fcel','NVDA','Msft','jpm']"
    newArgs = getListOrString(long)
    assert newArgs[0] == "AAPL"
    assert newArgs[-1] == "JPM"
    assert len(newArgs) == 5


def test_add_stock_single():
    stock = "msft"
    stockUpdater.stocklist = []
    # Use mock data instead of API call
    mock_data = get_mock_stock_data(stock)
    stockUpdater.updateStockInfo(mock_data)
    stockUpdater.conv_list2dict()
    assert stockUpdater.stocklist_dict[stock.upper()]["symbol"] == "MSFT"
    assert stockUpdater.stocklist[0]["account"] == ""
    assert stockUpdater.stocklist[0]["symbol"] == "MSFT"


def test_add_stock_multtext():
    stockUpdater.stocklist = []
    # Add multiple stocks with mock data
    for stock in ["msft", "fcel"]:
        mock_data = get_mock_stock_data(stock)
        stockUpdater.updateStockInfo(mock_data)
    stockUpdater.sort()
    assert stockUpdater.stocklist[0]["account"] == ""
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[1]["symbol"] == "MSFT"


def test_add_stock_multlist():
    stockUpdater.stocklist = []
    # Add multiple stocks with mock data
    for stock in ["msft", "fcel"]:
        mock_data = get_mock_stock_data(stock)
        stockUpdater.updateStockInfo(mock_data)
    stockUpdater.sort()
    assert stockUpdater.stocklist[0]["account"] == ""
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[1]["symbol"] == "MSFT"


def test_add_stock_badName():
    try:
        newArgs = stockUpdater.getListOrString("as3fd")
        stockUpdater.stockSplitter(newArgs)
    except AttributeError:
        pass
    else:
        assert False


def test_remove_stock():
    stockUpdater.stocklist = []
    mock_data = get_mock_stock_data("msft")
    stockUpdater.updateStockInfo(mock_data)
    stockUpdater.stockRemover("msft")
    for stock in stockUpdater.stocklist:
        assert stock["symbol"] != "MSFT"


def test_set_paper_stock_preference():
    stockUpdater.stocklist = []
    for stock in ["fcel", "goog"]:
        mock_data = get_mock_stock_data(stock)
        stockUpdater.updateStockInfo(mock_data)
    stockUpdater.setAccountPreference(["fcel", "goog"], "paper")
    stockUpdater.sort()
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["account"] == "paper"


def test_set_real_stock_preference():
    stockUpdater.stocklist = []
    mock_data = get_mock_stock_data("fcel")
    stockUpdater.updateStockInfo(mock_data)
    stockUpdater.setAccountPreference("fcel", "real")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["account"] == "real"


def test_clear_stock_preference():
    stockUpdater.stocklist = []
    mock_data = get_mock_stock_data("fcel")
    stockUpdater.updateStockInfo(mock_data)
    stockUpdater.setAccountPreference("fcel", "")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["account"] == ""


def test_clear_stock_preference_badName():
    stockUpdater.stocklist = []
    newArgs = getListOrString("tsla")
    problems = stockUpdater.setAccountPreference(newArgs, "")
    assert problems == "Stock not found for: TSLA | "


def test_setStockAmount():
    stockUpdater.stocklist = []
    mock_data = get_mock_stock_data("fcel")
    stockUpdater.updateStockInfo(mock_data)
    stockUpdater.setStockAmount("500", "fcel")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["amount"] == 500


def test_setStockAmount2():
    stockUpdater.stocklist = []
    for stock in ["fcel", "goog"]:
        mock_data = get_mock_stock_data(stock)
        stockUpdater.updateStockInfo(mock_data)
    stockUpdater.setStockAmount("800", ["goog", "fcel"])
    stockUpdater.sort()
    assert stockUpdater.stocklist[1]["symbol"] == "GOOG"
    assert stockUpdater.stocklist[1]["amount"] == 800
    assert stockUpdater.stocklist[0]["amount"] == 800


def test_setStockAmount3():
    # test for item not in stocks list.
    stockUpdater.stocklist = []
    mock_data = get_mock_stock_data("fcel")
    stockUpdater.updateStockInfo(mock_data)
    stockUpdater.setStockAmount("800", "msft")


def test_setOverrideMax1():
    # test for set override.
    clear_database()
    stockUpdater.stocklist = []
    mock_data = get_mock_stock_data("fcel")
    stockUpdater.updateStockInfo(mock_data)
    stockUpdater.getStockList()  # Reload from DB
    assert not stockUpdater.stocklist[0]["override"]
    stockUpdater.setOverrideMax("True", "fcel")
    stockUpdater.getStockList()  # Reload from DB
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["override"]


def test_setOverrideMax2():
    # test for invalid set override.
    stockUpdater.stocklist = []
    mock_data = get_mock_stock_data("fcel")
    stockUpdater.updateStockInfo(mock_data)
    try:
        stockUpdater.setOverrideMax("asdf", "fcel")
    except Exception:
        pass


def test_stock_sysargs():
    # verify no errors when passing an argument in
    # This test prints stock info, it shouldn't crash
    try:
        main(["-m"])
    except SystemExit:
        pass  # main() might call sys.exit()


def test_stock_multiply():
    # test to make sure stock amount is adjusted correctly
    stock = "NVDA"
    clear_database()
    stockUpdater.stocklist = []
    mock_data = get_mock_stock_data(stock)
    stockUpdater.updateStockInfo(mock_data)
    stockUpdater.setStockAmount("2000", stock)

    # Mock both getKeys and TradingClient to avoid API calls
    from alpaca.common.exceptions import APIError
    import json

    with patch('Data.get_stock_info.getKeys') as mock_getKeys, \
         patch('Data.get_stock_info.TradingClient') as mock_TradingClient:

        # Mock getKeys to return fake credentials
        mock_getKeys.return_value = {
            "api_key": "test_key",
            "secret_key": "test_secret"
        }

        # Mock TradingClient to raise APIError when position not found
        # Create a proper APIError with code 40410000
        error_json = json.dumps({"code": 40410000, "message": "position does not exist"})
        api_error = APIError(error_json)

        mock_client_instance = MagicMock()
        mock_client_instance.get_open_position.side_effect = api_error
        mock_TradingClient.return_value = mock_client_instance

        stockUpdater.multiplyAmount("1.2", stock)

    assert stockUpdater.stocklist[0]["symbol"] == stock
    assert stockUpdater.stocklist[0]["amount"] == 2400


def test_stock_offset():
    # test to make sure stock amount is adjusted correctly
    stock = "FCEL"
    stockUpdater.stocklist = []
    mock_data = get_mock_stock_data(stock)
    stockUpdater.updateStockInfo(mock_data)
    stockUpdater.setStockAmount("2000", stock)
    stockUpdater.offsetAmount("300", stock)
    assert stockUpdater.stocklist[0]["amount"] == 2300
    stockUpdater.offsetAmount("-300", stock)
    assert stockUpdater.stocklist[0]["amount"] == 2000


# if __name__ == "__main__":
#     test_get_stock_info()
#     test_add_stock_single()
#     test_add_stock_multtext()
#     test_add_stock_multlist()
#     test_add_stock_badName()
#     test_remove_stock()
#     test_set_paper_stock_preference()
#     test_set_real_stock_preference()
#     test_clear_stock_preference()
#     test_clear_stock_preference_badName()
#     test_setStockAmount()
#     test_setStockAmount2()
#     test_setStockAmount3()
