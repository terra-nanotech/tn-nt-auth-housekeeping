"""
Unit tests for the Cache handler in tnnt_housekeeping.handler.cache.
"""

# Standard Library
from unittest.mock import patch

# Django
from django.utils.timezone import now

# TN-NT Auth Housekeeping
from tnnt_housekeeping.handler.cache import Cache
from tnnt_housekeeping.tests import BaseTestCase


class TestHandlerCache(BaseTestCase):
    """
    Unit tests for the Cache handler in tnnt_housekeeping.handler.cache.
    """

    def setUp(self):
        self._cache_patcher = patch("tnnt_housekeeping.handler.cache.cache")
        self.mock_cache = self._cache_patcher.start()
        # default safe return value for get to avoid reading real cache
        self.mock_cache.get.return_value = False

    def tearDown(self):
        self._cache_patcher.stop()

    def test_raises_type_error_when_subkey_is_not_string(self):
        """
        Test that initializing Cache with a non-string subkey raises a TypeError.

        :return:
        :rtype:
        """

        with self.assertRaises(TypeError):
            Cache(subkey=123)

    def test_raises_value_error_when_subkey_is_empty_string(self):
        """
        Test that initializing Cache with an empty string subkey raises a ValueError.

        :return:
        :rtype:
        """

        with self.assertRaises(ValueError):
            Cache(subkey="")

    @patch("tnnt_housekeeping.handler.cache.cache.set")
    def test_sets_hourly_cache_with_correct_key_and_timeout(self, mock_cache_set):
        """
        Test that set_hourly sets the cache with the correct key and a timeout of 3600 seconds.

        :param mock_cache_set:
        :type mock_cache_set:
        :return:
        :rtype:
        """

        cache_handler = Cache(subkey="test_key")
        cache_handler.set_hourly(value="test_value")

        mock_cache_set.assert_called_once_with(
            key="tnnt-housekeeping:test_key", value="test_value", timeout=3600
        )

    @patch("tnnt_housekeeping.handler.cache.cache.set")
    def test_sets_daily_cache_with_correct_key_and_calculated_timeout(
        self, mock_cache_set
    ):
        """
        Test that set_daily sets the cache with the correct key and a timeout calculated until 11:30 AM the next day.

        :param mock_cache_set:
        :type mock_cache_set:
        :return:
        :rtype:
        """

        with patch(
            "tnnt_housekeeping.handler.cache.Cache._get_max_cache_time",
            return_value=86400,
        ):
            cache_handler = Cache(subkey="test_key")
            cache_handler.set_daily(value="test_value")

            mock_cache_set.assert_called_once_with(
                key="tnnt-housekeeping:test_key", value="test_value", timeout=86400
            )

    @patch("tnnt_housekeeping.handler.cache.cache.get")
    def test_retrieves_existing_cache_value(self, mock_cache_get):
        """
        Test that get retrieves the existing cache value when the cache key exists.

        :param mock_cache_get:
        :type mock_cache_get:
        :return:
        :rtype:
        """

        mock_cache_get.return_value = "existing_value"
        cache_handler = Cache(subkey="existing_key")
        result = cache_handler.get()

        self.assertEqual(result, "existing_value")
        mock_cache_get.assert_called_once_with(
            key="tnnt-housekeeping:existing_key", default=False
        )

    @patch("tnnt_housekeeping.handler.cache.cache.get")
    def test_returns_default_when_cache_key_does_not_exist(self, mock_cache_get):
        """
        Test that get returns the default value (False) when the cache key does not exist.

        :param mock_cache_get:
        :type mock_cache_get:
        :return:
        :rtype:
        """

        mock_cache_get.return_value = False
        cache_handler = Cache(subkey="nonexistent_key")
        result = cache_handler.get()

        self.assertFalse(result)
        mock_cache_get.assert_called_once_with(
            key="tnnt-housekeeping:nonexistent_key", default=False
        )

    @patch("tnnt_housekeeping.handler.cache.now")
    def test_returns_seconds_until_next_day_target_time(self, mock_now):
        """
        Test that _get_max_cache_time returns the correct number of seconds until 11:30 AM the next day when the current time is before 11:30 AM.

        :param mock_now:
        :type mock_now:
        :return:
        :rtype:
        """

        mock_now.return_value = now().replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        result = Cache._get_max_cache_time()

        self.assertEqual(result, 5400)  # 1.5 hours in seconds

    @patch("tnnt_housekeeping.handler.cache.now")
    def test_returns_seconds_until_target_time_next_day_when_past_target(
        self, mock_now
    ):
        """
        Test that _get_max_cache_time returns the correct number of seconds until 11:30 AM the next day when the current time is after 11:30 AM.

        :param mock_now:
        :type mock_now:
        :return:
        :rtype:
        """

        mock_now.return_value = now().replace(
            hour=12, minute=0, second=0, microsecond=0
        )
        result = Cache._get_max_cache_time()

        self.assertGreater(result, 0)

    @patch("tnnt_housekeeping.handler.cache.now")
    def test_handles_midnight_correctly(self, mock_now):
        """
        Test that _get_max_cache_time returns the correct number of seconds until 11:30 AM the next day when the current time is at midnight.

        :param mock_now:
        :type mock_now:
        :return:
        :rtype:
        """

        mock_now.return_value = now().replace(hour=0, minute=0, second=0, microsecond=0)
        result = Cache._get_max_cache_time()

        self.assertGreater(result, 0)
