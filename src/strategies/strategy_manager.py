import pandas as pd
import numpy as np
from utils.logger import setup_logger
from strategies.indicators import calculate_rsi

logger = setup_logger(log_file="logs/main.log")

# StrategyManager to manage prices and RSI evaluation
class StrategyManager:
    def __init__(self, buy_threshold=25, sell_threshold=75, buffer_size=100):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.price_buffer = []
        self.buffer_size = buffer_size

    def update_market_data(self, price):
        """
        Updates price buffer and calculates RSI.
        """
        self.price_buffer = update_price_buffer(self.price_buffer, price, self.buffer_size)
        return self.price_buffer

    def evaluate_strategy(self):
        """
        Uses buffered prices to calculate RSI and detect trends.
        """
        if len(self.price_buffer) < 14:
            logger.info("Waiting for sufficient market data...")
            return None

        rsi = calculate_rsi(self.price_buffer)
        logger.info(f"RSI: {rsi}")

        if rsi is None:
            logger.info("RSI is None, skipping strategy evaluation.")
            return None

        if rsi < self.buy_threshold:
            logger.info("BUY signal detected. 1")
            return "BUY"
        elif rsi > self.sell_threshold:
            logger.info("SELL signal detected. 1")
            return "SELL"
        else:
            logger.info("No significant signal. Holding position.")
            return None

# Function to update price buffer
def update_price_buffer(buffer, new_price, max_size=100):
    buffer.append(new_price)
    if len(buffer) > max_size:
        buffer.pop(0)
    return buffer
