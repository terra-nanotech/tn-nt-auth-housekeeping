"""
Cache handler for AA ESI Status.
"""

# Standard Library
from datetime import timedelta
from typing import Any

# Django
from django.core.cache import cache
from django.utils.timezone import now

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# TN-NT Auth Housekeeping
# AA ESI Status
from tnnt_housekeeping import __title__
from tnnt_housekeeping.providers import AppLogger

logger = AppLogger(my_logger=get_extension_logger(__name__), prefix=__title__)


class Cache:
    """
    Handling the redis cache for TN-NT Housekeeping.

    - Cache keys are generated based on a base key and a subkey.
    - Cache values are set with a timeout that expires at 11:30 AM the next day.
    """

    redis_key_base = "tnnt-housekeeping"

    def __init__(self, subkey: str) -> None:
        """
        Initialize the Cache with a subkey.

        :param subkey:
        :type subkey:
        """

        if not isinstance(subkey, str):
            raise TypeError("Argument 'subkey' must be a string")

        if not subkey.strip():
            raise ValueError("Argument 'subkey' must be a non-empty string")

        self.subkey = subkey

    def _get_cache_key(self) -> str:
        """
        Generate a cache key based on the base key and subkey.

        :return:
        :rtype:
        """

        cache_key = f"{self.redis_key_base}:{self.subkey}"

        logger.debug(f"Generating cache key for: {cache_key}")

        return cache_key

    @staticmethod
    def _get_max_cache_time() -> int:
        """
        Get the maximum cache time until 11:30 AM the next day.

        :return:
        :rtype:
        """

        expire_time = now()
        target = expire_time.replace(hour=11, minute=30, second=0, microsecond=0)

        if expire_time >= target:
            target += timedelta(days=1)

        return int((target - expire_time).total_seconds())

    def set_hourly(self, value: Any) -> None:
        """
        Set a specific cache value for a cache key.

        :param value:
        :type value:
        :return:
        :rtype:
        """

        cache_key = self._get_cache_key()

        logger.debug(f"Setting cache for: {cache_key}")

        cache.set(key=cache_key, value=value, timeout=3600)

    def set_daily(self, value: Any) -> None:
        """
        Set a specific cache value for a cache key.

        :param value:
        :type value:
        :return:
        :rtype:
        """

        cache_key = self._get_cache_key()

        logger.debug(f"Setting cache for: {cache_key}")

        cache.set(
            key=cache_key,
            value=value,
            timeout=self._get_max_cache_time(),
        )

    def get(self) -> Any:
        """
        Get a specific cache value for a cache key.

        :param url:
        :type url:
        :return:
        :rtype:
        """

        cache_key = self._get_cache_key()

        logger.debug(f"Getting cache for: {cache_key}")

        return cache.get(key=cache_key, default=False)
