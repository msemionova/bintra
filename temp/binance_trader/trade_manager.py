import logging
from typing import Dict, Optional
from .api.client import BinanceClient
from .strategies.base_strategy import BaseStrategy
from .config import Config
from binance.enums import *

logger = logging.getLogger(__name__)

class TradeManager:
    def __init__(self, client: BinanceClient):
        self.client = client
        self.active_trades: Dict[str, dict] = {}
        self.strategies: Dict[str, BaseStrategy] = {}

    def add_strategy(self, symbol: str, strategy: BaseStrategy):
        """Add a trading strategy for a symbol"""
        self.strategies[symbol] = strategy
        logger.info(f"Added strategy for {symbol}")

    async def start_trading(self):
        """Start trading for all registered strategies"""
        try:
            for symbol in self.strategies.keys():
                await self.client.start_kline_socket(
                    symbol,
                    self._handle_kline_data,
                    interval='1m'
                )
            logger.info("Started trading system")
        except Exception as e:
            logger.error(f"Error starting trading system: {e}")
            await self.stop_trading()
            raise

    async def stop_trading(self):
        """Stop trading and cleanup resources"""
        try:
            await self.client.close_all_connections()
            logger.info("Stopped trading system")
        except Exception as e:
            logger.error(f"Error stopping trading system: {e}")
            raise

    async def _handle_kline_data(self, msg):
        """Handle incoming kline/candlestick data"""
        try:
            if 'data' not in msg:
                logger.warning(f"Received invalid message format: {msg}")
                return
                
            kline_data = msg['data']['k']
            symbol = kline_data['s']
            
            if symbol not in self.strategies:
                return
                
            # Extract relevant kline data
            candle = {
                'open_time': kline_data['t'],
                'close_time': kline_data['T'],
                'symbol': symbol,
                'interval': kline_data['i'],
                'open': float(kline_data['o']),
                'high': float(kline_data['h']),
                'low': float(kline_data['l']),
                'close': float(kline_data['c']),
                'volume': float(kline_data['v']),
                'is_closed': kline_data['x']
            }
            
            # Only process completed candles
            if not candle['is_closed']:
                return
                
            strategy = self.strategies[symbol]
            await strategy.process_candle(candle)

            # Check for trade signals
            if symbol not in self.active_trades:
                if strategy.should_enter_trade():
                    self._enter_trade(symbol)
            else:
                if strategy.should_exit_trade():
                    self._exit_trade(symbol)

        except Exception as e:
            logger.error(f"Error handling kline data: {e}")

    def _enter_trade(self, symbol: str):
        """Enter a new trade"""
        try:
            # Calculate position size based on account balance and risk parameters
            account = self.client.get_account_balance()
            usdt_balance = float(next(
                (asset['free'] for asset in account['balances'] 
                if asset['asset'] == 'USDT'),
                0
            ))
            
            position_size = min(
                Config.MAX_POSITION_SIZE,
                usdt_balance * 0.1  # Use 10% of available balance
            )

            # Place market buy order
            order = self.client.place_order(
                symbol=symbol,
                side=SIDE_BUY,
                order_type=ORDER_TYPE_MARKET,
                quantity=position_size
            )

            # Record the trade
            self.active_trades[symbol] = {
                'entry_price': float(order['price']),
                'quantity': float(order['executedQty']),
                'order_id': order['orderId']
            }

            logger.info(f"Entered trade for {symbol} at {order['price']}")

        except Exception as e:
            logger.error(f"Error entering trade: {e}")

    def _exit_trade(self, symbol: str):
        """Exit an existing trade"""
        try:
            trade = self.active_trades.get(symbol)
            if not trade:
                return

            # Place market sell order
            order = self.client.place_order(
                symbol=symbol,
                side=SIDE_SELL,
                order_type=ORDER_TYPE_MARKET,
                quantity=trade['quantity']
            )

            # Calculate profit/loss
            entry_price = trade['entry_price']
            exit_price = float(order['price'])
            pl_percent = ((exit_price - entry_price) / entry_price) * 100

            logger.info(
                f"Exited trade for {symbol} at {exit_price}. "
                f"P/L: {pl_percent:.2f}%"
            )

            # Clear the trade record
            del self.active_trades[symbol]

        except Exception as e:
            logger.error(f"Error exiting trade: {e}")