import httpx
import hmac
import hashlib
import time
from utils.config_loader import load_config

class RESTAPIManager:
    config = load_config()
    BASE_URL = config["api_url"]

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key

    def sign_payload(self, params):
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(self.secret_key.encode(), query.encode(), hashlib.sha256).hexdigest()
        return f"{query}&signature={signature}"

    async def place_order(self, symbol: str, side: str, type_: str, quantity: float):
        endpoint = "/v3/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": type_,
            "quantity": quantity,
            "timestamp": int(time.time() * 1000)
        }
        signed_params = self.sign_payload(params)
        headers = {"X-MBX-APIKEY": self.api_key}

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.BASE_URL}{endpoint}?{signed_params}", headers=headers)
            return response.json()
