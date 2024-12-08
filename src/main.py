import asyncio
from utils.logger import setup_logger
from utils.config_loader import load_config
from api.websocket_manager import WebSocketManager
from api.rest_api_manager import RESTAPIManager
from strategies.strategy_manager import StrategyManager
from risk.risk_manager import RiskManager

logger = setup_logger()

async def main():
    config = load_config()

    ws_manager = WebSocketManager(f"{config["trading_pair"]}@ticker")
    rest_api = RESTAPIManager(config["api_key"], config["secret_key"])
    strategy = StrategyManager()
    risk = RiskManager(stop_loss=0.02, take_profit=0.05)

    await ws_manager.connect()

if __name__ == "__main__":
    asyncio.run(main())
