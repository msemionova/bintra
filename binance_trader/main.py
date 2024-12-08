import asyncio
import logging
from api.client import BinanceClient
from strategies.scalping_strategy import ScalpingStrategy
from trade_manager import TradeManager
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Initialize the Binance client
        client = BinanceClient()
        
        # Initialize trade manager
        trade_manager = TradeManager(client)
        
        # Register strategies for each trading pair
        for symbol in Config.TRADING_PAIRS:
            strategy = ScalpingStrategy(client, symbol)
            trade_manager.add_strategy(symbol, strategy)
        
        # Start trading
        await trade_manager.start_trading()
        
        # Keep the main loop running
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        # Cleanup
        client.close_all_connections()

if __name__ == "__main__":
    asyncio.run(main())