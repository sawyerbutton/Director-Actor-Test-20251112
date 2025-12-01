"""
Cache cleanup utilities.

Provides scheduled cleanup for expired cache entries.
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Optional

from .cache import CacheManager

logger = logging.getLogger(__name__)


class CacheCleanupScheduler:
    """
    Schedules periodic cleanup of expired cache entries.

    Usage:
        scheduler = CacheCleanupScheduler()
        await scheduler.start()  # Runs cleanup daily at midnight

        # Or run cleanup immediately
        removed = scheduler.run_cleanup_now()
    """

    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
        cleanup_hour: int = 0,
        cleanup_minute: int = 0,
    ):
        """
        Initialize cleanup scheduler.

        Args:
            cache_manager: CacheManager instance (creates new if not provided)
            cleanup_hour: Hour to run daily cleanup (0-23)
            cleanup_minute: Minute to run daily cleanup (0-59)
        """
        self._cache = cache_manager or CacheManager()
        self._cleanup_time = time(hour=cleanup_hour, minute=cleanup_minute)
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the cleanup scheduler."""
        if self._running:
            logger.warning("Cleanup scheduler already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_scheduler())
        logger.info(
            f"Cache cleanup scheduler started, will run daily at {self._cleanup_time}"
        )

    async def stop(self):
        """Stop the cleanup scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Cache cleanup scheduler stopped")

    def run_cleanup_now(self) -> int:
        """
        Run cleanup immediately.

        Returns:
            Number of expired entries removed
        """
        logger.info("Running cache cleanup...")
        removed = self._cache.cleanup_expired()
        logger.info(f"Cache cleanup complete: {removed} expired entries removed")
        return removed

    async def _run_scheduler(self):
        """Main scheduler loop."""
        while self._running:
            try:
                # Calculate seconds until next cleanup time
                now = datetime.now()
                next_run = datetime.combine(now.date(), self._cleanup_time)

                # If cleanup time already passed today, schedule for tomorrow
                if next_run <= now:
                    next_run = next_run.replace(day=now.day + 1)

                wait_seconds = (next_run - now).total_seconds()
                logger.debug(f"Next cache cleanup in {wait_seconds:.0f} seconds")

                # Wait until cleanup time
                await asyncio.sleep(wait_seconds)

                # Run cleanup
                if self._running:
                    self.run_cleanup_now()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup scheduler: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(60)


def run_cleanup(db_path: str = None) -> int:
    """
    Convenience function to run cleanup immediately.

    Args:
        db_path: Optional database path

    Returns:
        Number of expired entries removed
    """
    with CacheManager(db_path) as cache:
        return cache.cleanup_expired()
