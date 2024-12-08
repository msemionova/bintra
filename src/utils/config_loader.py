import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    return {
        "api_key": os.getenv("TESTNET_API_KEY"),
        "secret_key": os.getenv("TESTNET_SECRET_KEY"),
        "trading_pair": os.getenv("TRADING_PAIR"),
        "api_url": os.getenv("API_TESTNET_BASE"),
        "ws_url": os.getenv("WS_TESTNET"),
    }
