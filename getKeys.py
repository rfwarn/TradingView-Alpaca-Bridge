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
    # Try to get secure keys if they exist.
    try:
        keys = get_secret()
    except Exception as e:
        print(e)
    for key, value in keys.items():
        os.environ[key] = value
    
    # Get the API keys from the environment variables. These are for Paper keys. Below are keys for real trading in Alpaca
    if account == "paperTrading":
        # Paper trading
        paperTrading = {
            "api_key": os.environ.get("Alpaca_API_KEY"),
            "secret_key": os.environ.get("Alpaca_SECRET_KEY"),
            "paper": True,
        }
        account = paperTrading
    elif account == "realTrading":
        # Real money trading
        realTrading = {
            "api_key": os.environ.get("Alpaca_API_KEY-real"),
            "secret_key": os.environ.get("Alpaca_SECRET_KEY-real"),
            "paper": False,
        }
        account = realTrading
    else:
        raise NameError(
            "Verify account type ('realTrading'/'paperTrading') is correct in settings(using:)"
        )
    return account