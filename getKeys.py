from dotenv import load_dotenv
import os
try:
    from Keys.getSecureKeys import get_secret
except ModuleNotFoundError:
    pass

def getKeys(account):
    """Retrives the keys for either the "paperTrading" or "realTrading" account.
    Pass in either "paperTrading" or "realTrading" and it will return the keys and paper setting.
    Ex. {
        "api_key": "ASDJKL",
        "secret_key": "jkn23kj234nkj2",
        "paper": True,
    }"""
    load_dotenv(override=True)
    
    def getSecureKeys():
        # Try to get secure keys if they exist.
        try:
            keys = get_secret()
        except Exception as e:
            print(e)
            return
        # for key, value in keys.items():
        #     os.environ[key] = value
        return keys
    
    # Get the API keys from the environment variables. These are for Paper keys. Below are keys for real trading in Alpaca
    keys = {}
    if account == "paperTrading":
        # Paper trading
        if not os.environ.get("Alpaca_API_KEY"):
            keys = getSecureKeys()
        else:
            keys['Alpaca_API_KEY'] = os.environ.get("Alpaca_API_KEY")
            keys['Alpaca_SECRET_KEY'] = os.environ.get("Alpaca_SECRET_KEY")
        paperTrading = {
            "api_key": keys['Alpaca_API_KEY'],
            "secret_key": keys['Alpaca_SECRET_KEY'],
            "paper": True,
        }
        account = paperTrading
    elif account == "realTrading":
        # Real money trading
        if not os.environ.get("Alpaca_API_KEY-real"):
            keys = getSecureKeys()
        else:
            keys['Alpaca_API_KEY-real'] = os.environ.get("Alpaca_API_KEY-real")
            keys['Alpaca_SECRET_KEY-real'] = os.environ.get("Alpaca_SECRET_KEY-real")
        realTrading = {
            "api_key": keys["Alpaca_API_KEY-real"],
            "secret_key": keys["Alpaca_SECRET_KEY-real"],
            "paper": False,
        }
        account = realTrading
    else:
        raise NameError(
            "Verify account type ('realTrading'/'paperTrading') is correct in settings(using:)"
        )
    return account

if __name__ == '__main__':
    getKeys("paperTrading")