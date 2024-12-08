import numpy as np

def calculate_rsi(prices, period=14):
    """
    Calculates the Relative Strength Index (RSI).
    """
    if len(prices) < period:
        return 50  # Neutral RSI if insufficient data

    deltas = np.diff(prices)
    gains = np.maximum(deltas, 0)
    losses = -np.minimum(deltas, 0)

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        return 100  # RSI is 100 if no losses

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
