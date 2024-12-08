import pandas as pd
import numpy as np

class StrategyManager:
    def calculate_ema(self, prices, period):
        return prices.ewm(span=period, adjust=False).mean()

    def evaluate_signal(self, prices):
        short_ema = self.calculate_ema(prices, period=12)
        long_ema = self.calculate_ema(prices, period=26)

        if short_ema.iloc[-1] > long_ema.iloc[-1]:
            return "BUY"
        elif short_ema.iloc[-1] < long_ema.iloc[-1]:
            return "SELL"
        return "HOLD"
