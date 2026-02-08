"""
Unit tests for the housekeeping tasks.
"""

# Standard Library
from unittest.mock import patch

# TN-NT Auth Housekeeping
from tnnt_housekeeping.tasks import DailyTasks, daily_housekeeping, housekeeping
from tnnt_housekeeping.tests import BaseTestCase


class TestDailyHousekeepingTasks(BaseTestCase):
    """
    Test cases for the housekeeping tasks.
    """

    @patch("tnnt_housekeeping.tasks.EveCorporationInfo.objects.filter")
    def test_corporation_cleanup_deletes_closed_corporations(self, mock_filter):
        """
        Test that the corporation_cleanup method deletes closed corporations with CEO ID 1.

        :param mock_filter:
        :type mock_filter:
        :return:
        :rtype:
        """

        mock_queryset = mock_filter.return_value
        mock_queryset.count.return_value = 3

        DailyTasks.corporation_cleanup()

        mock_filter.assert_called_once_with(ceo_id=1)
        mock_queryset.delete.assert_called_once()

    @patch("tnnt_housekeeping.tasks.EveCorporationInfo.objects.filter")
    def test_corporation_cleanup_no_closed_corporations_to_delete(self, mock_filter):
        """
        Test that the corporation_cleanup method does not attempt to delete when there are no closed corporations.

        :param mock_filter:
        :type mock_filter:
        :return:
        :rtype:
        """

        mock_queryset = mock_filter.return_value
        mock_queryset.count.return_value = 0

        DailyTasks.corporation_cleanup()
        mock_filter.assert_called_once_with(ceo_id=1)

    @patch("tnnt_housekeeping.tasks.EveCharacter.objects.filter")
    def test_character_cleanup_deletes_characters_in_doomheim(self, mock_filter):
        """
        Test that the character_cleanup method deletes characters in corporation ID 1000001 (Doomheim).

        :param mock_filter:
        :type mock_filter:
        :return:
        :rtype:
        """

        mock_queryset = mock_filter.return_value
        mock_queryset.count.return_value = 5

        DailyTasks.character_cleanup()

        mock_filter.assert_called_once_with(corporation_id=1000001)
        mock_queryset.delete.assert_called_once()

    @patch("tnnt_housekeeping.tasks.EveCharacter.objects.filter")
    def test_character_cleanup_no_characters_to_delete(self, mock_filter):
        """
        Test that the character_cleanup method does not attempt to delete when there are no characters in corporation ID 1000001 (Doomheim).

        :param mock_filter:
        :type mock_filter:
        :return:
        :rtype:
        """

        mock_queryset = mock_filter.return_value
        mock_queryset.count.return_value = 0

        DailyTasks.character_cleanup()

        mock_filter.assert_called_once_with(corporation_id=1000001)

    @patch("tnnt_housekeeping.tasks.Cache.get")
    @patch("tnnt_housekeeping.tasks.DailyTasks.corporation_cleanup")
    @patch("tnnt_housekeeping.tasks.DailyTasks.character_cleanup")
    @patch("tnnt_housekeeping.tasks.Cache.set_daily")
    def test_runs_daily_tasks_when_cache_is_empty(
        self,
        mock_set_daily,
        mock_character_cleanup,
        mock_corporation_cleanup,
        mock_cache_get,
    ):
        """
        Test that the daily_housekeeping function runs daily tasks when the cache is empty.

        :param mock_set_daily:
        :type mock_set_daily:
        :param mock_character_cleanup:
        :type mock_character_cleanup:
        :param mock_corporation_cleanup:
        :type mock_corporation_cleanup:
        :param mock_cache_get:
        :type mock_cache_get:
        :return:
        :rtype:
        """

        mock_cache_get.return_value = False

        daily_housekeeping()

        mock_cache_get.assert_called_once_with()
        mock_corporation_cleanup.assert_called_once()
        mock_character_cleanup.assert_called_once()
        mock_set_daily.assert_called_once()

    @patch("tnnt_housekeeping.tasks.Cache.get")
    @patch("tnnt_housekeeping.tasks.DailyTasks.corporation_cleanup")
    @patch("tnnt_housekeeping.tasks.DailyTasks.character_cleanup")
    @patch("tnnt_housekeeping.tasks.Cache.set_daily")
    def test_skips_daily_tasks_when_cache_is_set(
        self,
        mock_set_daily,
        mock_character_cleanup,
        mock_corporation_cleanup,
        mock_cache_get,
    ):
        """
        Test that the daily_housekeeping function skips daily tasks when the cache is set.

        :param mock_set_daily:
        :type mock_set_daily:
        :param mock_character_cleanup:
        :type mock_character_cleanup:
        :param mock_corporation_cleanup:
        :type mock_corporation_cleanup:
        :param mock_cache_get:
        :type mock_cache_get:
        :return:
        :rtype:
        """

        mock_cache_get.return_value = True

        daily_housekeeping()

        mock_cache_get.assert_called_once_with()
        mock_corporation_cleanup.assert_not_called()
        mock_character_cleanup.assert_not_called()
        mock_set_daily.assert_not_called()

    @patch("tnnt_housekeeping.tasks.daily_housekeeping.delay")
    def test_triggers_daily_housekeeping_task(self, mock_daily_housekeeping):
        """
        Test that the housekeeping function triggers the daily_housekeeping task.

        :param mock_daily_housekeeping:
        :type mock_daily_housekeeping:
        :return:
        :rtype:
        """

        housekeeping()
        mock_daily_housekeeping.assert_called_once()
