# Bintra Bot

A modular cryptocurrency trading bot built with Python

## Features

- Real-time cryptocurrency trading
- Modular strategy system for easy implementation of custom trading strategies
- Built-in scalping strategy implementation
- Real-time market data processing
- Automated trade execution and management
- Risk management through configurable parameters

## Requirements

- Python 3.7+
- API credentials
- Required Python packages (see Installation section)

## Installation

1. Clone the repository:
```bash
git clone <git@github.com:msemionova/bintra.git>
```

2. Install required packages:
```bash
pip3 install binance-client pandas numpy
```

3. Configure your API credentials in `config.py`:
```python
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'
```

## Usage

1. Configure trading pairs and parameters in `config.py`:
```python
TRADING_PAIRS = ['TRXUSDT']  # Add your desired trading pairs
```

2. Run the trading bot:
```bash
python3 src/main.py
```

## Warning

Trading cryptocurrencies involves significant risk of loss. Use this software at your own risk.
