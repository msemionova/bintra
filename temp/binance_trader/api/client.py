from binance.client import Client
from binance.enums import *
import asyncio
import logging
from binance_trader.config import Config
from .websocket_manager import WebSocketManager
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class BinanceClient:
    def __init__(self):
        self.client = Client(
            Config.API_KEY,
            Config.API_SECRET,
            testnet=Config.USE_TESTNET
        )
        self.bm = None
        self.ws_connections = {}
        self._setup_socket_manager()

    def _setup_socket_manager(self):
        """Initialize WebSocket manager"""
        self.ws_manager = WebSocketManager()
        self.rate_limiter = RateLimiter(max_requests=1200, time_window=60)
        self.rate_limiter.start()

    async def start_kline_socket(self, symbol: str, callback, interval: str = '1m'):
        """Start a WebSocket connection for kline/candlestick data"""
        try:
            stream_name = f"{symbol.lower()}@kline_{interval}"
            await self.ws_manager.connect_socket(stream_name, callback)
            logger.info(f"Started kline socket for {symbol} - {interval}")
        except Exception as e:
            logger.error(f"Error starting kline socket: {e}")
            raise

    async def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        """Place an order on Binance"""
        try:
            await self.rate_limiter.acquire()
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity
            }
            if price and order_type != ORDER_TYPE_MARKET:
                params['price'] = price

            order = self.client.create_order(**params)
            logger.info(f"Order placed: {order}")
            return order
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise

    async def get_account_balance(self):
        """Get account balance for all assets"""
        try:
            await self.rate_limiter.acquire()
            return self.client.get_account()
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            raise

    async def close_all_connections(self):
        """Close all WebSocket connections"""
        try:
            await self.ws_manager.close()
            logger.info("Closed all WebSocket connections")
        except Exception as e:
            logger.error(f"Error closing WebSocket connections: {e}")
            raise