import asyncio
import websockets
from utils.logger import setup_logger
from utils.config_loader import load_config
import json

logger = setup_logger(log_file="logs/main.log")
class WebSocketManager:
    config = load_config()
    WS_URL = config["ws_url"]

    def __init__(self, stream: str):
        self.url = f"{self.WS_URL}/{stream}"
        self.last_message = None  # Initialize last_message

    async def connect(self):
        try:
            logger.info("Connecting to WebSocket...")
            async with websockets.connect(self.url) as ws:
                while True:
                    message = await ws.recv()
                    logger.info(f"Received: {message}")
                    # Parse the JSON string into a Python dictionary
                    parsed_message = json.loads(message)
                    logger.info(f"Received message: {parsed_message}")
                    await self.handle_message(parsed_message)

        except websockets.ConnectionClosed:
            logger.warning("WebSocket connection closed. Reconnecting...")
            await self.connect()

    async def listen(self):
        # Simply return the last message received
        return self.last_message

    async def handle_message(self, message):
        # Store the parsed message in the last_message attribute
        self.last_message = message
        # Optionally, process the message further here if needed