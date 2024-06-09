# generates a daily report for buying and selling with alpaca paper stocks
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
import os
import requests
import datetime
import pandas as pd
from getKeys import getKeys


def genReport(account: str = "paperTrading", days: int = 180):
    """Generates a Alpaca buy/sell report for last x (default 30) days. At the moment,
    it can only retrieve a max of 500 transactions (alpaca API limitation) per request.
    Specify 'paperTrading' or 'realTrading' ('paperTrading' default) for account.
    """
    client = getKeys(account)
    client = TradingClient(**client)
    dt = datetime.datetime.today() - datetime.timedelta(days=days)
    ordr = GetOrdersRequest(status="closed", after=dt, limit=500)
    history = client.get_orders(ordr)
    newdict = {}
    for i in history:
        tempdict = i.__dict__
        for k, v in tempdict.items():
            if newdict.get(k):
                newdict[k].append(v)
            else:
                newdict[k] = [v]
    df = pd.DataFrame(newdict)
    return df


def writeFile(df, account: str = "paperTrading"):
    name = "AlpacaPaper.csv" if account == "paperTrading" else "AlpacaReal.csv"
    df.to_csv(name)


def getDocuments():
    # Not used at the moment
    account_id = os.environ.get("Alpaca_ID")
    url = (
        f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{account_id}/documents"
    )
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    print(response.text)


if __name__ == "__main__":
    # Generates reports for both 'paperTrading' and 'realTrading'. Second arguemnt is number of days to return (default is 30). Limit max is 500 returns at the moment by Alpaca.
    account = "paperTrading"
    report = genReport(account)
    writeFile(report, account)
    account = "realTrading"
    report = genReport(account)
    writeFile(report, account)
    # getDocuments()
