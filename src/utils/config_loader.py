import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    return {
        "api_key": os.getenv("TESTNET_API_KEY"),
        "secret_key": os.getenv("TESTNET_SECRET_KEY")
    }
