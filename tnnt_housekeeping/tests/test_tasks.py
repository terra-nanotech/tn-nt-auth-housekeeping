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

            DailyTasks._remove_closed_corporations()

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

            DailyTasks._remove_closed_corporations()

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

        DailyTasks._remove_closed_corporations()
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

            DailyTasks._remove_biomassed_characters()

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

            DailyTasks._remove_biomassed_characters()

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

        DailyTasks._remove_biomassed_characters()

        mock_filter.assert_called_once_with(corporation_id=1000001)

    def test_non_account_character_cleanup_logs_and_deletes_unlinked_characters(self):
        """
        Test that remove_non_account_characters logs the number of unlinked characters found and deletes them.

        :return:
        """

        with (
            patch(MODULE + ".EveCharacter.objects.filter") as mock_filter,
            patch(MODULE + ".logger") as mock_logger,
        ):
            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 4
            mock_filter.return_value = mock_queryset

            DailyTasks._remove_non_account_characters()

            mock_logger.info.assert_any_call(
                "Starting daily non-account character cleanup tasks."
            )
            mock_logger.info.assert_any_call(
                "Found 4 non-account characters to delete."
            )
            mock_queryset.delete.assert_called_once()

    def test_non_account_character_cleanup_no_unlinked_characters(self):
        """
        Test that remove_non_account_characters does not attempt to delete when there are no unlinked characters.

        :return:
        """

        with patch(MODULE + ".EveCharacter.objects.filter") as mock_filter:
            mock_queryset = mock_filter.return_value
            mock_queryset.count.return_value = 0

            DailyTasks._remove_non_account_characters()

            mock_filter.assert_called_once_with(character_ownership__isnull=True)

    def test_non_account_character_cleanup_handles_deletion_error(self):
        """
        Test that remove_non_account_characters logs an error if there is an exception during deletion of unlinked characters.

        :return:
        """

        with (
            patch(MODULE + ".EveCharacter.objects.filter") as mock_filter,
            patch(MODULE + ".logger") as mock_logger,
        ):
            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 2
            mock_queryset.delete.side_effect = Exception("Deletion failed")
            mock_filter.return_value = mock_queryset

            DailyTasks._remove_non_account_characters()

            mock_logger.error.assert_called_once_with(
                "Error deleting non-account characters: Deletion failed"
            )

    def test_empty_corporation_cleanup_logs_and_deletes_empty_corporations(self):
        """
        Test that remove_empty_corporations logs the number of empty corporations found and deletes them.

        :return:
        """

        with (
            patch(MODULE + ".EveCharacter.objects.values_list") as mock_values_list,
            patch(MODULE + ".EveCorporationInfo.objects.exclude") as mock_exclude,
            patch(MODULE + ".logger") as mock_logger,
        ):
            # values_list().distinct() should provide the IDs used in the exclude call
            mock_values_list.return_value.distinct.return_value = [10, 20]

            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 2
            mock_exclude.return_value = mock_queryset

            DailyTasks._remove_empty_corporations()

            mock_logger.info.assert_any_call(
                "Starting daily empty corporation cleanup tasks."
            )
            mock_logger.info.assert_any_call("Found 2 empty corporations to delete.")
            mock_queryset.delete.assert_called_once()

    def test_empty_corporation_cleanup_no_empty_corporations(self):
        """
        Test that remove_empty_corporations does not attempt to delete when there are no empty corporations.

        :return:
        """

        with (
            patch(MODULE + ".EveCharacter.objects.values_list") as mock_values_list,
            patch(MODULE + ".EveCorporationInfo.objects.exclude") as mock_exclude,
        ):
            mock_values_list.return_value.distinct.return_value = []
            mock_queryset = mock_exclude.return_value
            mock_queryset.count.return_value = 0

            DailyTasks._remove_empty_corporations()

            mock_values_list.assert_called_once_with("corporation_id", flat=True)
            mock_values_list.return_value.distinct.assert_called_once()
            mock_exclude.assert_called_once_with(
                corporation_id__in=mock_values_list.return_value.distinct.return_value
            )

    def test_empty_corporation_cleanup_handles_deletion_error(self):
        """
        Test that remove_empty_corporations logs an error if there is an exception during deletion of empty corporations.

        :return:
        """

        with (
            patch(MODULE + ".EveCharacter.objects.values_list") as mock_values_list,
            patch(MODULE + ".EveCorporationInfo.objects.exclude") as mock_exclude,
            patch(MODULE + ".logger") as mock_logger,
        ):
            mock_values_list.return_value.distinct.return_value = [1]
            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 1
            mock_queryset.delete.side_effect = Exception("Deletion error")
            mock_exclude.return_value = mock_queryset

            DailyTasks._remove_empty_corporations()

            mock_logger.error.assert_called_once_with(
                "Error deleting empty corporations: Deletion error"
            )

    def test_empty_alliance_cleanup_logs_and_deletes_empty_alliances(self):
        """
        Test that remove_empty_alliances logs the number of empty alliances found and deletes them.

        :return:
        """

        with (
            patch(MODULE + ".EveCharacter.objects.values_list") as mock_values_list,
            patch(MODULE + ".EveAllianceInfo.objects.exclude") as mock_exclude,
            patch(MODULE + ".logger") as mock_logger,
        ):
            # values_list().exclude().distinct() should provide the IDs used in the exclude call
            mock_values_list.return_value.exclude.return_value.distinct.return_value = [
                100,
                200,
            ]

            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 2
            mock_exclude.return_value = mock_queryset

            DailyTasks._remove_empty_alliances()

            mock_logger.info.assert_any_call(
                "Starting daily empty alliance cleanup tasks."
            )
            mock_logger.info.assert_any_call("Found 2 empty alliances to delete.")
            mock_queryset.delete.assert_called_once()

    def test_empty_alliance_cleanup_no_empty_alliances(self):
        """
        Test that remove_empty_alliances does not attempt to delete when there are no empty alliances.

        :return:
        """

        with (
            patch(MODULE + ".EveCharacter.objects.values_list") as mock_values_list,
            patch(MODULE + ".EveAllianceInfo.objects.exclude") as mock_exclude,
        ):
            mock_values_list.return_value.exclude.return_value.distinct.return_value = (
                []
            )
            mock_queryset = mock_exclude.return_value
            mock_queryset.count.return_value = 0

            DailyTasks._remove_empty_alliances()

            mock_values_list.assert_called_once_with("alliance_id", flat=True)
            mock_values_list.return_value.exclude.assert_called_once_with(
                alliance_id__isnull=True
            )
            mock_values_list.return_value.exclude.return_value.distinct.assert_called_once()
            mock_exclude.assert_called_once_with(
                alliance_id__in=mock_values_list.return_value.exclude.return_value.distinct.return_value
            )

    def test_empty_alliance_cleanup_handles_deletion_error(self):
        """
        Test that remove_empty_alliances logs an error if there is an exception during deletion of empty alliances.

        :return:
        """

        with (
            patch(MODULE + ".EveCharacter.objects.values_list") as mock_values_list,
            patch(MODULE + ".EveAllianceInfo.objects.exclude") as mock_exclude,
            patch(MODULE + ".logger") as mock_logger,
        ):
            mock_values_list.return_value.exclude.return_value.distinct.return_value = [
                42
            ]
            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 1
            mock_queryset.delete.side_effect = Exception("Deletion error")
            mock_exclude.return_value = mock_queryset

            DailyTasks._remove_empty_alliances()

            mock_logger.error.assert_called_once_with(
                "Error deleting empty alliances: Deletion error"
            )

    ##
    # DAILY HOUSEKEEPING TASKS
    ##

    @patch(MODULE + ".Cache.get")
    @patch(MODULE + ".DailyTasks._remove_closed_corporations")
    @patch(MODULE + ".DailyTasks._remove_biomassed_characters")
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
    @patch(MODULE + ".DailyTasks._remove_closed_corporations")
    @patch(MODULE + ".DailyTasks._remove_biomassed_characters")
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
