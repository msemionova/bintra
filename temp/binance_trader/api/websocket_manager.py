import websockets
import json
import logging
import asyncio
from typing import Dict, Optional, Callable, Any
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections to Binance streams"""
    
    WEBSOCKET_BASE_URL = "wss://stream.binance.com:9443/ws/"
    
    def __init__(self):
        self._connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self._callbacks: Dict[str, Callable] = {}
        self._running = False
        self._tasks = set()

    async def connect_socket(self, stream_name: str, callback: Callable[[dict], Any]) -> None:
        """
        Connect to a Binance WebSocket stream
        
        Args:
            stream_name: Name of the stream to connect to (e.g. "btcusdt@kline_1m")
            callback: Callback function to handle incoming messages
        """
        if stream_name in self._connections:
            logger.warning(f"Stream {stream_name} already connected")
            return

        self._callbacks[stream_name] = callback
        uri = urljoin(self.WEBSOCKET_BASE_URL, stream_name)
        
        try:
            ws = await websockets.connect(uri)
            self._connections[stream_name] = ws
            task = asyncio.create_task(self._handle_socket(stream_name, ws))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
            logger.info(f"Connected to stream: {stream_name}")
        except Exception as e:
            logger.error(f"Failed to connect to {stream_name}: {e}")
            raise

    async def _handle_socket(self, stream_name: str, websocket: websockets.WebSocketClientProtocol) -> None:
        """Handle incoming messages from a WebSocket connection"""
        try:
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    await self._process_message(stream_name, data)
                except websockets.ConnectionClosed:
                    logger.warning(f"Connection closed for stream {stream_name}")
                    await self._reconnect(stream_name)
                    break
                except Exception as e:
                    logger.error(f"Error in socket {stream_name}: {e}")
                    await asyncio.sleep(1)  # Prevent tight loop in case of repeated errors
        finally:
            await self._cleanup_connection(stream_name)

    async def _process_message(self, stream_name: str, data: dict) -> None:
        """Process incoming message and call appropriate callback"""
        try:
            callback = self._callbacks.get(stream_name)
            if callback:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
        except Exception as e:
            logger.error(f"Error processing message for {stream_name}: {e}")

    async def _reconnect(self, stream_name: str) -> None:
        """Attempt to reconnect to a stream after connection loss"""
        await self._cleanup_connection(stream_name)
        
        retry_count = 0
        max_retries = 5
        
        while retry_count < max_retries:
            try:
                callback = self._callbacks.get(stream_name)
                if callback:
                    await self.connect_socket(stream_name, callback)
                    logger.info(f"Successfully reconnected to {stream_name}")
                    return
            except Exception as e:
                retry_count += 1
                wait_time = min(1 * 2 ** retry_count, 30)  # Exponential backoff with 30s cap
                logger.warning(f"Reconnection attempt {retry_count} failed for {stream_name}: {e}")
                await asyncio.sleep(wait_time)
        
        logger.error(f"Failed to reconnect to {stream_name} after {max_retries} attempts")

    async def _cleanup_connection(self, stream_name: str) -> None:
        """Clean up connection resources"""
        if stream_name in self._connections:
            try:
                await self._connections[stream_name].close()
            except Exception as e:
                logger.error(f"Error closing connection for {stream_name}: {e}")
            finally:
                del self._connections[stream_name]

    async def close(self) -> None:
        """Close all WebSocket connections"""
        for stream_name in list(self._connections.keys()):
            await self._cleanup_connection(stream_name)
        
        # Cancel all running tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for all tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)