import os

class Config:
    # API Configuration
    API_KEY = os.getenv('TESTNET_API_KEY')
    API_SECRET = os.getenv('TESTNET_API_SECRET')

    # Trading Parameters
    USE_TESTNET = os.getenv('USE_TESTNET', 'True').lower() == 'true'
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '100'))  # USDT

    # Risk Management
    STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', '1.0'))
    TAKE_PROFIT_PERCENTAGE = float(os.getenv('TAKE_PROFIT_PERCENTAGE', '2.0'))
    MAX_TRADES_PER_DAY = int(os.getenv('MAX_TRADES_PER_DAY', '10'))

    # WebSocket Settings
    WS_RECONNECT_ATTEMPTS = int(os.getenv('WS_RECONNECT_ATTEMPTS', '3'))
    WS_RECONNECT_DELAY = int(os.getenv('WS_RECONNECT_DELAY', '5'))  # seconds

    # Trading Pairs
    TRADING_PAIRS = os.getenv('TRADING_PAIRS')