from Data.get_stock_info import StockUpdater, getListOrString, main

# from get_stock_info import StockUpdater, getListOrString, main

stockUpdater = StockUpdater(write=False, loadSL=False)
SL = []


def test_get_stock_info():
    # Test to get the stock info and add it to the list as an object with blank account
    # information ('') if not already present.
    # global SL
    newArgs = getListOrString("goog")
    SL = stockUpdater.stockSplitter(newArgs)
    assert SL[0]["account"] == ""


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
    temp = main(["-a", stock], write=False, loadSL=False)
    temp.conv_list2dict()
    assert temp.stocklist_dict[stock.upper()]["symbol"] == "MSFT"

    stockUpdater.stocklist = []
    newArgs = getListOrString("msft")
    SL = stockUpdater.stockSplitter(newArgs)
    assert SL[0]["account"] == ""
    assert SL[0]["symbol"] == "MSFT"


def test_add_stock_multtext():
    stockUpdater.stocklist = []
    newArgs = getListOrString("msft, fcel")
    SL = stockUpdater.stockSplitter(newArgs)
    assert SL[0]["account"] == ""
    assert SL[0]["symbol"] == "FCEL"
    assert SL[1]["symbol"] == "MSFT"


def test_add_stock_multlist():
    stockUpdater.stocklist = []
    newArgs = getListOrString("['msft', 'fcel']")
    SL = stockUpdater.stockSplitter(newArgs)
    assert SL[0]["account"] == ""
    assert SL[0]["symbol"] == "FCEL"
    assert SL[1]["symbol"] == "MSFT"


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
    newArgs = getListOrString("msft")
    stockUpdater.stockSplitter(newArgs)
    stockUpdater.stockRemover(newArgs)
    for stock in stockUpdater.stocklist:
        assert stock["symbol"] != "MSFT"


def test_set_paper_stock_preference():
    stockUpdater.stocklist = []
    newArgs = getListOrString("fcel, goog")
    stockUpdater.stockSplitter(newArgs)
    stockUpdater.setAccountPreference(newArgs, "paper")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["account"] == "paper"


def test_set_real_stock_preference():
    stockUpdater.stocklist = []
    newArgs = getListOrString("fcel")
    stockUpdater.stockSplitter(newArgs)
    stockUpdater.setAccountPreference(newArgs, "real")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["account"] == "real"


def test_clear_stock_preference():
    stockUpdater.stocklist = []
    newArgs = getListOrString("fcel")
    stockUpdater.stockSplitter(newArgs)
    stockUpdater.setAccountPreference(newArgs, "")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["account"] == ""


def test_clear_stock_preference_badName():
    stockUpdater.stocklist = []
    newArgs = getListOrString("tsla")
    problems = stockUpdater.setAccountPreference(newArgs, "")
    assert problems == "Stock not found for: TSLA | "


def test_setStockAmount():
    stockUpdater.stocklist = []
    newArgs = getListOrString("fcel")
    stockUpdater.stockSplitter(newArgs)
    stockUpdater.setStockAmount("500", "fcel")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["amount"] == 500


def test_setStockAmount2():
    stockUpdater.stocklist = []
    newArgs = getListOrString("fcel, goog")
    stockUpdater.stockSplitter(newArgs)
    stockUpdater.setStockAmount("800", ["goog", "fcel"])
    assert stockUpdater.stocklist[1]["symbol"] == "GOOG"
    assert stockUpdater.stocklist[1]["amount"] == 800
    assert stockUpdater.stocklist[0]["amount"] == 800


def test_setStockAmount3():
    # test for item not in stocks list.
    stockUpdater.stocklist = []
    newArgs = getListOrString("fcel")
    stockUpdater.stockSplitter(newArgs)
    stockUpdater.setStockAmount("800", "msft")


def test_setOverrideMax1():
    # test for set override.
    stockUpdater.stocklist = []
    newArgs = getListOrString("fcel")
    stockUpdater.stockSplitter(newArgs)
    assert not stockUpdater.stocklist[0]["override"]
    stockUpdater.setOverrideMax("True", "fcel")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["override"]


def test_setOverrideMax2():
    # test for invalid set override.
    stockUpdater.stocklist = []
    newArgs = getListOrString("fcel")
    stockUpdater.stockSplitter(newArgs)
    try:
        stockUpdater.setOverrideMax("asdf", "fcel")
    except Exception:
        pass


def test_stock_sysargs():
    # verify no errors when passing an argument in
    main(["-m"])


def test_stock_multiply():
    # test to make sure stock amount is adjusted correctly
    stock = "NVDA"
    stocklist = '"NVDA", "JPM"'
    main(["-a", stocklist], write=False, loadSL=False)
    main(["-sm", "345", stocklist], write=False, loadSL=False)
    main(["-ma", "1.1", stock], write=False, loadSL=False)
    temp = main(["-ma", "1.2", stocklist], write=False, loadSL=False)
    temp.conv_list2dict()
    assert temp.stocklist_dict["JPM"]["amount"] == 414
    assert int(temp.stocklist_dict["NVDA"]["amount"]) == 455

    stockUpdater.stocklist = []
    stockUpdater.stockSplitter(stock)
    stockUpdater.setStockAmount("2000", stock)
    stockUpdater.multiplyAmount("1.2", stock)
    assert stockUpdater.stocklist[0]["symbol"] == stock
    assert stockUpdater.stocklist[0]["amount"] == 2400


def test_stock_offset():
    # test to make sure stock amount is adjusted correctly
    # stock = "NVDA"
    stock = "FCEL"
    stockUpdater.stocklist = []
    stockUpdater.stockSplitter(stock)
    main(["-a", stock], write=False, loadSL=False)
    main(["-sm", "222", stock], write=False, loadSL=False)
    temp = main(["-oa", "3", stock], write=False, loadSL=False)
    temp.conv_list2dict()
    assert temp.stocklist_dict[stock]["amount"] == 225
    # stocklist = '["NVDA", "JPM"]'
    # main(["-oa", "3", stocklist])

    stockUpdater.stocklist = []
    newArgs = getListOrString(stock)
    stockUpdater.stockSplitter(newArgs)
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
