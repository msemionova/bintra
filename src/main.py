import asyncio
from utils.logger import setup_logger
from utils.config_loader import load_config
from api.websocket_manager import WebSocketManager
from api.rest_api_manager import RESTAPIManager
from strategies.strategy_manager import StrategyManager
from risk.risk_manager import RiskManager

logger = setup_logger(log_file="logs/bintra.log")

async def main():
    # Load configuration
    config = load_config()

    # Initialize components
    ws_manager = WebSocketManager(f"{config['trading_pair']}@ticker")
    rest_api = RESTAPIManager(config["api_key"], config["secret_key"])
    strategy = StrategyManager(buy_threshold=29500, sell_threshold=30500)  # Example thresholds
    risk = RiskManager(stop_loss=0.02, take_profit=0.05)

    # Connect WebSocket
    await ws_manager.connect()

    # Process market data and execute strategies
    async for message in ws_manager.listen():
        price = float(message["c"])  # Current price
        strategy.update_market_data(price)
        action = strategy.evaluate_strategy()

        if action == "BUY":
            logger.info(f"Signal detected: {action} at {price}")
            rest_api.place_order("BUY", quantity=0.001)
        elif action == "SELL":
            logger.info(f"Signal detected: {action} at {price}")
            rest_api.place_order("SELL", quantity=0.001)

if __name__ == "__main__":
    asyncio.run(main())
