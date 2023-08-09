# generates a daily report for buying and selling with alpaca paper stocks
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
import os
import requests
import datetime
import pandas as pd


def genReport(account: str='paper', days: int=7):
    """ Generates a general report for x days in the past. At the moment, it can only retrieve a max of 500 transactions. """
    if account == 'paper':
        # Get the API keys from the environment variables. These are for Paper keys. Below are keys for real trading in Alpaca
        # ALPACA_API_ENDPOINT = 'https://paper-api.alpaca.markets'
        API_KEY = os.environ.get("Alpaca_API_KEY")
        SECRET_KEY = os.environ.get("Alpaca_SECRET_KEY")
        paper = True
    elif account == 'real':
        # Real money settings***
        API_KEY = os.environ.get('Alpaca_API_KEY-real')
        SECRET_KEY = os.environ.get("Alpaca_SECRET-real")
        paper = False
    else:
        raise Exception('Input keyword needs to be "paper" or "real". Default is paper.')
    client = TradingClient(API_KEY, SECRET_KEY, paper=paper)
    # account = client.get_account()
    # assets = client.get_all_positions()
    # dt = datetime.datetime(year=2023, month=8, day=2, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    dt = datetime.datetime.today() - datetime.timedelta(days=days)
    ordr = GetOrdersRequest(status='closed', after=dt, limit=500)
    history = client.get_orders(ordr)
    newdict = {}
    for i in history:
        tempdict = i.__dict__
        for k, v in tempdict.items():
            if newdict.get(k):
                newdict[k].append(v)
            else:
                newdict[k] = [v]
            # print(k, v)
        
    df = pd.DataFrame(newdict)
    
    name = 'AlpacaTest.csv' if account == 'paper' else 'AlpacaReal.csv'
    df.to_csv(name)
    # df.to_excel('Alpacatest.xlsx')
    # print('test')
    return df


def getDocuments():
    # Not used at the moment
    account_id = os.environ.get("Alpaca_ID")
    url = f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{account_id}/documents"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    print(response.text)


if __name__ == "__main__":
    # set to 'paper' or 'real' (default is paper). Second arguemnt is number of days to return (default is 7). Limit max is 500 returns at the moment.
    genReport()
    # getDocuments()
