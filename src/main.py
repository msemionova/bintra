import asyncio
from utils.logger import setup_logger
from utils.config_loader import load_config
from api.websocket_manager import WebSocketManager
from api.rest_api_manager import RESTAPIManager
from strategies.strategy_manager import StrategyManager
from risk.risk_manager import RiskManager
from binance.client import Client  # Import Binance client

logger = setup_logger(log_file="logs/main.log")

async def check_active_orders(binance_client, SYMBOL):
    """Check if there are any active orders for the symbol"""
    orders = binance_client.get_open_orders(symbol=SYMBOL)
    return len(orders) > 0  # Return True if there are active orders

async def main():
    # Load configuration
    config = load_config()

    API_KEY = config["api_key"]
    API_SECRET = config["secret_key"]
    TRADING_PAIR = config["trading_pair"]
    SYMBOL = config["trading_pair"].upper()
    ORDER_SIZE = 20  # Number of units for buy/sell
    TIMEFRAME = '1m'  # Candle time frame

    # Order constants
    SIDE_BUY = 'BUY'
    SIDE_SELL = 'SELL'
    ORDER_TYPE_MARKET = 'MARKET'
    ORDER_TYPE_LIMIT = 'LIMIT'

    # Initialize components
    ws_manager = WebSocketManager(f"{TRADING_PAIR}@ticker")
    rest_api = RESTAPIManager(API_KEY, API_SECRET)

    # Initialize Binance client
    binance_client = Client(API_KEY, API_SECRET, testnet=True)

    strategy = StrategyManager(buy_threshold=25, sell_threshold=75)  # Example thresholds
    risk = RiskManager(stop_loss=0.02, take_profit=0.05)

    # Connect WebSocket asynchronously
    websocket_task = asyncio.create_task(ws_manager.connect())

    try:
        # Simulate doing other things asynchronously
        logger.info("WebSocket manager running in the background")

        ################## Получаем баланс USDT
        usdt_balance = binance_client.get_asset_balance(asset='USDT')
        logger.info(f"Balance USDT: {usdt_balance}")

        # # ################## Получаем баланс TRX
        trx_balance = binance_client.get_asset_balance(asset='TRX')
        logger.info(f"Balance TRX: {trx_balance}")

        orders = binance_client.get_all_orders(symbol="TRXUSDT")
        # Фильтруем только открытые ордера (статус "NEW" или "PARTIALLY_FILLED")
        open_orders = [order for order in orders if order['status'] in ['NEW', 'PARTIALLY_FILLED']]

        # Выводим открытые ордера
        if open_orders:
            print(f"Open orders: {open_orders}")
        else:
            print("No open orders.")

        # Process market data and execute strategies
        while True:
            # Example of continuously fetching messages
            message = await ws_manager.listen()
            if message:
                logger.info(f"Received message...")
                price = float(message["c"])  # Current price
                updated_data = strategy.update_market_data(price)
                action = strategy.evaluate_strategy()

                logger.info(f"Price: {price}")
                logger.info(f"Updated market data: {updated_data[-14:]}")
                logger.info(f"Action: {action}")

                # Check for active orders before placing a new one
                if await check_active_orders(binance_client, SYMBOL):
                    logger.info("An active order exists, waiting before placing a new one.")
                else:
                    if action == "BUY":
                        logger.info(f"Signal detected: {action} at {price}")
                        # Place actual buy order using Binance client
                        binance_client.order_market_buy(symbol=SYMBOL, quantity=ORDER_SIZE)
                    elif action == "SELL":
                        logger.info(f"Signal detected: {action} at {price}")
                        # Place actual sell order using Binance client
                        binance_client.order_market_sell(symbol=SYMBOL, quantity=ORDER_SIZE)

            await asyncio.sleep(2)  # Adjust the sleep time based on your needs
    except asyncio.CancelledError:
        logger.info("Shutdown initiated, cancelling tasks...")
        websocket_task.cancel()
        await websocket_task
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Main program shutting down.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected, exiting...")