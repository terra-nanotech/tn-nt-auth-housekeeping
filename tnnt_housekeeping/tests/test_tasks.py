"""
Unit tests for the housekeeping tasks.
"""

# Standard Library
from unittest.mock import MagicMock, patch

# TN-NT Auth Housekeeping
from tnnt_housekeeping.tasks import DailyTasks, daily_housekeeping, housekeeping
from tnnt_housekeeping.tests import BaseTestCase

MODULE = "tnnt_housekeeping.tasks"


class TestDailyHousekeepingTasks(BaseTestCase):
    """
    Test cases for the housekeeping tasks.
    """

    ##
    # CORPORATION CLEANUP TESTS
    ##

    def test_corporation_cleanup_logs_and_deletes_closed_corporations(self):
        """
        Test that the corporation_cleanup method logs the number of closed corporations found and deletes them.

        :return:
        :rtype:
        """

        with (
            patch(MODULE + ".EveCorporationInfo.objects.filter") as mock_filter,
            patch(MODULE + ".logger") as mock_logger,
        ):
            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 3
            mock_filter.return_value = mock_queryset

            DailyTasks.remove_closed_corporations()

            mock_logger.info.assert_any_call(
                "Starting daily corporation cleanup tasks."
            )
            mock_logger.info.assert_any_call("Found 3 closed corporations to delete.")
            mock_queryset.delete.assert_called_once()

    def test_corporation_cleanup_handles_deletion_error(self):
        """
        Test that the corporation_cleanup method logs an error if there is an exception during deletion.

        :return:
        :rtype:
        """

        with (
            patch(MODULE + ".EveCorporationInfo.objects.filter") as mock_filter,
            patch(MODULE + ".logger") as mock_logger,
        ):
            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 2
            mock_queryset.delete.side_effect = Exception("Deletion error")
            mock_filter.return_value = mock_queryset

            DailyTasks.remove_closed_corporations()

            mock_logger.error.assert_called_once_with(
                "Error deleting closed corporations: Deletion error"
            )

    @patch(MODULE + ".EveCorporationInfo.objects.filter")
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

        DailyTasks.remove_closed_corporations()
        mock_filter.assert_called_once_with(ceo_id=1)

    ##
    # CHARACTER CLEANUP TESTS
    ##

    def test_character_cleanup_logs_and_deletes_doomheim_characters(self):
        """
        Test that the character_cleanup method logs the number of characters found in Doomheim and deletes them.

        :return:
        :rtype:
        """

        with (
            patch(MODULE + ".EveCharacter.objects.filter") as mock_filter,
            patch(MODULE + ".logger") as mock_logger,
        ):
            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 5
            mock_filter.return_value = mock_queryset

            DailyTasks.remove_biomassed_characters()

            mock_logger.info.assert_any_call("Starting daily character cleanup tasks.")
            mock_logger.info.assert_any_call("Found 5 characters to delete.")
            mock_queryset.delete.assert_called_once()

    def test_character_cleanup_handles_deletion_error(self):
        """
        Test that the character_cleanup method logs an error if there is an exception during deletion of characters in Doomheim.

        :return:
        :rtype:
        """

        with (
            patch(MODULE + ".EveCharacter.objects.filter") as mock_filter,
            patch(MODULE + ".logger") as mock_logger,
        ):
            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 3
            mock_queryset.delete.side_effect = Exception("Deletion error")
            mock_filter.return_value = mock_queryset

            DailyTasks.remove_biomassed_characters()

            mock_logger.error.assert_called_once_with(
                "Error deleting characters in Doomheim: Deletion error"
            )

    @patch(MODULE + ".EveCharacter.objects.filter")
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

        DailyTasks.remove_biomassed_characters()

        mock_filter.assert_called_once_with(corporation_id=1000001)

    ##
    # DAILY HOUSEKEEPING TASKS
    ##

    @patch(MODULE + ".Cache.get")
    @patch(MODULE + ".DailyTasks.remove_closed_corporations")
    @patch(MODULE + ".DailyTasks.remove_biomassed_characters")
    @patch(MODULE + ".Cache.set_daily")
    def test_runs_daily_tasks_when_cache_is_empty(
        self,
        mock_set_daily,
        mock_remove_biomassed_characters,
        mock_remove_closed_corporations,
        mock_cache_get,
    ):
        """
        Test that the daily_housekeeping function runs daily tasks when the cache is empty.

        :param mock_set_daily:
        :type mock_set_daily:
        :param mock_remove_biomassed_characters:
        :type mock_remove_biomassed_characters:
        :param mock_remove_closed_corporations:
        :type mock_remove_closed_corporations:
        :param mock_cache_get:
        :type mock_cache_get:
        :return:
        :rtype:
        """

        mock_cache_get.return_value = False

        daily_housekeeping()

        mock_cache_get.assert_called_once_with()
        mock_remove_closed_corporations.assert_called_once()
        mock_remove_biomassed_characters.assert_called_once()
        mock_set_daily.assert_called_once()

    @patch(MODULE + ".Cache.get")
    @patch(MODULE + ".DailyTasks.remove_closed_corporations")
    @patch(MODULE + ".DailyTasks.remove_biomassed_characters")
    @patch(MODULE + ".Cache.set_daily")
    def test_skips_daily_tasks_when_cache_is_set(
        self,
        mock_set_daily,
        mock_remove_biomassed_characters,
        mock_remove_closed_corporations,
        mock_cache_get,
    ):
        """
        Test that the daily_housekeeping function skips daily tasks when the cache is set.

        :param mock_set_daily:
        :type mock_set_daily:
        :param mock_remove_biomassed_characters:
        :type mock_remove_biomassed_characters:
        :param mock_remove_closed_corporations:
        :type mock_remove_closed_corporations:
        :param mock_cache_get:
        :type mock_cache_get:
        :return:
        :rtype:
        """

        mock_cache_get.return_value = True

        daily_housekeeping()

        mock_cache_get.assert_called_once_with()
        mock_remove_closed_corporations.assert_not_called()
        mock_remove_biomassed_characters.assert_not_called()
        mock_set_daily.assert_not_called()

    @patch(MODULE + ".daily_housekeeping.delay")
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
