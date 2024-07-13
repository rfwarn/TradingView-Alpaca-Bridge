from Data.get_stock_info import StockUpdater, getListOrString, main

stockUpdater = StockUpdater(write=False)
SL = []


def test_get_stock_info():
    # Test to get the stock info and add it to the list as an object with blank account
    # information ('') if not already present.
    # global SL
    newArgs = getListOrString("goog")
    SL = stockUpdater.stockSplitter(newArgs)
    assert SL[0]["account"] == ""


def test_add_stock_single():
    # global SL
    main(["-a", "msft"])
    newArgs = getListOrString("msft")
    SL = stockUpdater.stockSplitter(newArgs)
    assert SL[0]["account"] == ""
    assert SL[1]["symbol"] == "MSFT"


def test_add_stock_multtext():
    # global SL
    newArgs = getListOrString("msft, fcel")
    SL = stockUpdater.stockSplitter(newArgs)
    assert SL[0]["account"] == ""
    assert SL[0]["symbol"] == "FCEL"
    assert SL[2]["symbol"] == "MSFT"


def test_add_stock_multlist():
    # global SL
    newArgs = getListOrString("['msft', 'fcel']")
    SL = stockUpdater.stockSplitter(newArgs)
    assert SL[0]["account"] == ""
    assert SL[0]["symbol"] == "FCEL"
    assert SL[2]["symbol"] == "MSFT"


def test_add_stock_badName():
    global SL
    try:
        newArgs = stockUpdater.getListOrString("as3fd")
        SL = stockUpdater.stockSplitter(newArgs)
    except AttributeError:
        pass
    else:
        assert False


def test_remove_stock():
    newArgs = getListOrString("msft")
    stockUpdater.stockRemover(newArgs)
    for stock in stockUpdater.stocklist:
        assert stock["symbol"] != "MSFT"


def test_set_paper_stock_preference():
    newArgs = getListOrString("fcel, goog")
    stockUpdater.setAccountPreference(newArgs, "paper")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["account"] == "paper"


def test_set_real_stock_preference():
    newArgs = getListOrString("fcel")
    stockUpdater.setAccountPreference(newArgs, "real")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["account"] == "real"


def test_clear_stock_preference():
    newArgs = getListOrString("fcel")
    stockUpdater.setAccountPreference(newArgs, "")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["account"] == ""


def test_clear_stock_preference_badName():
    newArgs = getListOrString("tsla")
    stockUpdater.setAccountPreference(newArgs, "")


def test_setStockAmount():
    stockUpdater.setStockAmount("500", "fcel")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["amount"] == 500


def test_setStockAmount2():
    stockUpdater.setStockAmount("800", ["goog", "fcel"])
    assert stockUpdater.stocklist[1]["symbol"] == "GOOG"
    assert stockUpdater.stocklist[1]["amount"] == 800
    assert stockUpdater.stocklist[0]["amount"] == 800


def test_setStockAmount3():
    # test for item not in stocks list.
    stockUpdater.setStockAmount("800", "msft")


def test_setOverrideMax1():
    # test for set override.
    assert not stockUpdater.stocklist[0]["override"]
    stockUpdater.setOverrideMax("True", "fcel")
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["override"]


def test_setOverrideMax2():
    # test for invalid set override.
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
    # stocklist = '["NVDA", "JPM"]'
    stocklist = '"NVDA", "JPM"'
    # stock = "FCEL"
    stockUpdater.stocklist = []
    temp = main(["-a", stocklist], write=False)
    stockUpdater.stockSplitter(stock)
    stockUpdater.setStockAmount("2000", stock)
    main(["-ma", "1", stock])
    main(["-ma", "1", stocklist])
    stockUpdater.multiplyAmount("1.2", stock)
    assert stockUpdater.stocklist[0]["symbol"] == stock
    assert stockUpdater.stocklist[0]["amount"] == 2400


def test_stock_offset():
    # test to make sure stock amount is adjusted correctly
    # stock = "NVDA"
    stock = "FCEL"
    stocklist = '["NVDA", "JPM"]'
    stockUpdater.stocklist = []
    stockUpdater.stockSplitter(stock)
    main(["-oa", "3", stock])
    # main(["-oa", "3", stocklist])
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
