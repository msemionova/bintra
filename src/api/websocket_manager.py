import asyncio
import websockets
from utils.logger import setup_logger
from utils.config_loader import load_config

logger = setup_logger(log_file="logs/bintra_websocket.log")
class WebSocketManager:
    config = load_config()
    WS_URL = config["ws_url"]

    def __init__(self, stream: str):
        self.url = f"{self.WS_URL}/{stream}"

    async def connect(self):
        try:
            logger.info("Connecting to WebSocket...")
            async with websockets.connect(self.url) as ws:
                while True:
                    message = await ws.recv()
                    logger.info(f"Received: {message}")
        except websockets.ConnectionClosed:
            logger.warning("WebSocket connection closed. Reconnecting...")
            await self.connect()
