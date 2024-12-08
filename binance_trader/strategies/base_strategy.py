from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from ..api.client import BinanceClient

class BaseStrategy(ABC):
    def __init__(self, client: BinanceClient, symbol: str):
        self.client = client
        self.symbol = symbol
        self.data = pd.DataFrame()

    @abstractmethod
    def calculate_signals(self) -> dict:
        """Calculate trading signals based on strategy logic"""
        pass

    @abstractmethod
    def should_enter_trade(self) -> bool:
        """Determine if we should enter a trade"""
        pass

    @abstractmethod
    def should_exit_trade(self) -> bool:
        """Determine if we should exit a trade"""
        pass

    def update_data(self, kline_data: dict):
        """Update strategy data with new kline information"""
        new_data = pd.DataFrame([{
            'timestamp': kline_data['k']['t'],
            'open': float(kline_data['k']['o']),
            'high': float(kline_data['k']['h']),
            'low': float(kline_data['k']['l']),
            'close': float(kline_data['k']['c']),
            'volume': float(kline_data['k']['v'])
        }])
        self.data = pd.concat([self.data, new_data]).tail(100)  # Keep last 100 candles

    def calculate_rsi(self, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs)).iloc[-1]

    def calculate_ema(self, period: int) -> float:
        """Calculate Exponential Moving Average"""
        return self.data['close'].ewm(span=period, adjust=False).mean().iloc[-1]

    def calculate_macd(self) -> tuple:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = self.data['close'].ewm(span=12, adjust=False).mean()
        exp2 = self.data['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd.iloc[-1], signal.iloc[-1]