import pandas as pd
import numpy as np
from utils.logger import setup_logger
from strategies.indicators import calculate_rsi

logger = setup_logger(log_file="logs/main.log")

class StrategyManager:
    def __init__(self, buy_threshold=30, sell_threshold=70):
        """
        Initialize the strategy manager with thresholds for RSI and a list for closing prices.
        """
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.close_prices = []

    def update_market_data(self, price: float):
        """
        Updates the list of closing prices for RSI calculation.

        Args:
            price (float): The latest closing price.
        """
        self.close_prices.append(price)
        if len(self.close_prices) > 100:  # Limit the stored prices to the last 100
            self.close_prices.pop(0)

        logger.info(f"Updated close prices: {self.close_prices[-5:]}")  # Log last 5 prices

    def evaluate_strategy(self) -> str | None:
        """
        Analyzes the market data and generates trading signals based on RSI.

        Returns:
            str | None: "BUY", "SELL", or None if no action is required.
        """
        if len(self.close_prices) < 14:  # Ensure enough data for RSI calculation
            logger.info("Not enough data for RSI calculation.")
            return None

        # Calculate RSI
        rsi = calculate_rsi(self.close_prices)
        logger.info(f"Calculated RSI: {rsi}")

        # Determine signal based on thresholds
        if rsi < self.buy_threshold:
            logger.info("RSI below buy threshold. Signal: BUY")
            return "BUY"
        elif rsi > self.sell_threshold:
            logger.info("RSI above sell threshold. Signal: SELL")
            return "SELL"
        else:
            logger.info("RSI within thresholds. No action.")
            return None

    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculates the Exponential Moving Average (EMA) for given prices and period.

        Args:
            prices (pd.Series): Series of closing prices.
            period (int): EMA calculation period.

        Returns:
            pd.Series: The calculated EMA values.
        """
        return prices.ewm(span=period, adjust=False).mean()

    def evaluate_signal(self, prices: pd.Series) -> str:
        """
        Evaluates trading signals based on EMA crossovers.

        Args:
            prices (pd.Series): Series of closing prices.

        Returns:
            str: "BUY", "SELL", or "HOLD" based on the EMA crossover.
        """
        short_ema = self.calculate_ema(prices, period=12)
        long_ema = self.calculate_ema(prices, period=26)

        if short_ema.iloc[-1] > long_ema.iloc[-1]:
            return "BUY"
        elif short_ema.iloc[-1] < long_ema.iloc[-1]:
            return "SELL"
        return "HOLD"
