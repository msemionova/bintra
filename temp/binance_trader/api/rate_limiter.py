import asyncio
import time
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for Binance API requests"""
    
    def __init__(self, max_requests: int, time_window: float):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[float, int] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    async def acquire(self):
        """
        Acquire a rate limit slot. Blocks if rate limit is exceeded.
        """
        while True:
            now = time.time()
            # Remove old timestamps
            cutoff = now - self.time_window
            self.requests = {ts: count for ts, count in self.requests.items() if ts > cutoff}
            
            # Calculate current request count
            current_requests = sum(self.requests.values())
            
            if current_requests < self.max_requests:
                # Add new request
                self.requests[now] = self.requests.get(now, 0) + 1
                return
            
            # Wait before checking again
            await asyncio.sleep(0.1)

    async def cleanup(self):
        """
        Periodically cleanup old timestamps
        """
        while True:
            try:
                now = time.time()
                cutoff = now - self.time_window
                self.requests = {ts: count for ts, count in self.requests.items() if ts > cutoff}
                await asyncio.sleep(self.time_window / 2)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")
                await asyncio.sleep(1)

    def start(self):
        """Start the cleanup task"""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self.cleanup())

    async def stop(self):
        """Stop the cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None