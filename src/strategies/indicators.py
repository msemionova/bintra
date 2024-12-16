import numpy as np
import talib
from utils.logger import setup_logger

logger = setup_logger(log_file="logs/main.log")

# Example function to calculate RSI using TA-Lib
def calculate_rsi(prices, period=14):
    # Ensure we have enough data for RSI calculation
    if len(prices) < period:
        return None  # Not enough data to calculate RSI

    # Convert the list to a numpy array (TA-Lib expects numpy arrays)
    prices_array = np.array(prices)

    if len(prices) > period:
        # Calculate RSI using TA-Lib (adjust the period as needed)
        rsi = talib.RSI(prices_array, timeperiod=period)
        logger.info(f"Talib RSI: {rsi}")

        return rsi[-1]  # Return the most recent RSI value
