from .base_strategy import BaseStrategy
import numpy as np

class ScalpingStrategy(BaseStrategy):
    def __init__(self, client, symbol, rsi_period=14, rsi_overbought=70, rsi_oversold=30):
        super().__init__(client, symbol)
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def calculate_signals(self) -> dict:
        if len(self.data) < 30:  # Need enough data for calculations
            return {'valid': False}

        rsi = self.calculate_rsi(self.rsi_period)
        ema_20 = self.calculate_ema(20)
        macd, signal = self.calculate_macd()
        
        current_price = self.data['close'].iloc[-1]
        
        return {
            'valid': True,
            'rsi': rsi,
            'ema_20': ema_20,
            'macd': macd,
            'signal': signal,
            'current_price': current_price,
            'is_bullish': self._is_bullish_setup(),
            'is_bearish': self._is_bearish_setup()
        }

    def should_enter_trade(self) -> bool:
        signals = self.calculate_signals()
        if not signals['valid']:
            return False

        # Bullish entry conditions
        if signals['is_bullish'] and signals['rsi'] < self.rsi_oversold:
            return True

        # Bearish entry conditions
        if signals['is_bearish'] and signals['rsi'] > self.rsi_overbought:
            return True

        return False

    def should_exit_trade(self) -> bool:
        signals = self.calculate_signals()
        if not signals['valid']:
            return True  # Exit if we can't calculate signals

        # Exit conditions based on RSI reversal
        if signals['is_bullish'] and signals['rsi'] > self.rsi_overbought:
            return True
        if signals['is_bearish'] and signals['rsi'] < self.rsi_oversold:
            return True

        return False

    def _is_bullish_setup(self) -> bool:
        if len(self.data) < 3:
            return False
        
        last_closes = self.data['close'].tail(3)
        return (last_closes.iloc[-1] > last_closes.iloc[-2] > last_closes.iloc[-3])

    def _is_bearish_setup(self) -> bool:
        if len(self.data) < 3:
            return False
        
        last_closes = self.data['close'].tail(3)
        return (last_closes.iloc[-1] < last_closes.iloc[-2] < last_closes.iloc[-3])