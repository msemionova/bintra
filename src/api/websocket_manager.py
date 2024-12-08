import asyncio
import websockets
import logging
from utils.config_loader import load_config

class WebSocketManager:
    config = load_config()
    WS_URL = config["ws_url"]

    def __init__(self, stream: str):
        self.url = f"{self.WS_URL}/{stream}"

    async def connect(self):
        try:
            logging.info("Connecting to WebSocket...")
            async with websockets.connect(self.url) as ws:
                while True:
                    message = await ws.recv()
                    logging.info(f"Received: {message}")
        except websockets.ConnectionClosed:
            logging.warning("WebSocket connection closed. Reconnecting...")
            await self.connect()
