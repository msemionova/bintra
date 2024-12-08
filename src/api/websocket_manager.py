import asyncio
import websockets
import logging

class WebSocketManager:
    def __init__(self, stream: str):
        self.url = f"wss://testnet.binance.vision/ws/{stream}"

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
