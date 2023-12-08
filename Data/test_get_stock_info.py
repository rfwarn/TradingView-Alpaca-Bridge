from get_stock_info import StockUpdater, getListOrString

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
    assert stockUpdater.stocklist[0]["symbol"] == "FCEL"
    assert stockUpdater.stocklist[0]["account"] == ""


if __name__ == "__main__":
    test_get_stock_info()
    test_add_stock_single()
    test_add_stock_multtext()
    test_add_stock_multlist()
    test_add_stock_badName()
    test_remove_stock()
    test_set_paper_stock_preference()
    test_set_real_stock_preference()
    test_clear_stock_preference()
    test_clear_stock_preference_badName()
