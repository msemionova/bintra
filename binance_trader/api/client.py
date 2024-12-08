from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
import asyncio
import logging
from ..config import Config

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
        self.bm = BinanceSocketManager(self.client)

    async def start_kline_socket(self, symbol, callback, interval='1m'):
        """Start a WebSocket connection for kline/candlestick data"""
        try:
            conn_key = f"{symbol}_{interval}"
            self.ws_connections[conn_key] = self.bm.start_kline_socket(
                symbol,
                callback,
                interval=interval
            )
            logger.info(f"Started kline socket for {symbol} - {interval}")
        except Exception as e:
            logger.error(f"Error starting kline socket: {e}")
            raise

    def place_order(self, symbol, side, order_type, quantity, price=None):
        """Place an order on Binance"""
        try:
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

    def get_account_balance(self):
        """Get account balance for all assets"""
        try:
            return self.client.get_account()
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            raise

    def close_all_connections(self):
        """Close all WebSocket connections"""
        try:
            self.bm.close()
            self.ws_connections.clear()
            logger.info("Closed all WebSocket connections")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")