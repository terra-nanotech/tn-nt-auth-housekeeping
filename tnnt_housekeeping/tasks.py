"""
Housekeeping tasks for TN-NT Auth Housekeeping.
"""

# Third Party
from celery import shared_task
from celery_once import QueueOnce

# Django
from django.utils import timezone

# Alliance Auth
from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)
from allianceauth.services.hooks import get_extension_logger

# TN-NT Auth Housekeeping
from tnnt_housekeeping.handler.cache import Cache
from tnnt_housekeeping.providers import AppLogger

logger = AppLogger(my_logger=get_extension_logger(name=__name__))

CACHE_KEY_HOURLY_HOUSEKEEPING = "hourly-housekeeping-last-run"
CACHE_KEY_DAILY_HOUSEKEEPING = "daily-housekeeping-last-run"


@shared_task(base=QueueOnce, once={"graceful": True, "timeout": 300})
def housekeeping() -> None:
    """
    Main housekeeping task that runs every minute and performs both hourly and daily housekeeping tasks.

    :return:
    :rtype:
    """

    logger.info("Starting main housekeeping task.")

    # hourly_housekeeping.delay()
    daily_housekeeping.delay()


# @shared_task(base=QueueOnce, once={"graceful": True, "timeout": 300})
# def hourly_housekeeping():
#     """
#     This function performs hourly housekeeping tasks.
#
#     :return:
#     :rtype:
#     """
#
#     cache_subkey = CACHE_KEY_HOURLY_HOUSEKEEPING
#     cached = Cache(subkey=cache_subkey).get()
#
#     if cached:
#         logger.debug(
#             "Hourly housekeeping tasks have already been run recently. Skipping."
#         )
#
#         return
#
#     logger.info("Starting hourly housekeeping tasks.")
#
#     # Trigger all hourly hooks for TN-NT Housekeeping
#
#     # Update the cache to indicate that hourly housekeeping tasks have been run
#     Cache(subkey=cache_subkey).set_hourly(value=timezone.now())


@shared_task(base=QueueOnce, once={"graceful": True, "timeout": 300})
def daily_housekeeping() -> None:
    """
    This function performs daily housekeeping tasks.

    :return:
    :rtype:
    """

    cache_subkey = CACHE_KEY_DAILY_HOUSEKEEPING
    cached = Cache(subkey=cache_subkey).get()

    if cached:
        logger.debug(
            "Daily housekeeping tasks have already been run recently. Skipping."
        )

        return

    logger.info("Starting daily housekeeping tasks.")

    # Trigger all daily hooks for TN-NT Housekeeping
    DailyTasks().cleanup_eveonline_data()  # Cleanup EveOnline data

    # Update the cache to indicate that daily housekeeping tasks have been run
    Cache(subkey=cache_subkey).set_daily(value=timezone.now())


class DailyTasks:
    """
    Class to handle daily housekeeping tasks.
    """

    @staticmethod
    def _remove_closed_corporations() -> None:
        """
        Remove closed corporations from the database.
        Closed corporations are identified by having a CEO ID of 1.

        :return:
        :rtype:
        """

        logger.info("Starting daily corporation cleanup tasks.")

        # Find corporations with CEO ID 1 (indicating closed corporations)
        closed_corps = EveCorporationInfo.objects.filter(ceo_id=1)
        count = closed_corps.count()

        logger.info(f"Found {count} closed corporations to delete.")

        try:
            closed_corps.delete()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Error deleting closed corporations: {e}")

    @staticmethod
    def _remove_biomassed_characters() -> None:
        """
        Remove characters that are in the Doomheim corporation (corporation ID 1000001).
        These characters are considered "biomassed" and should be removed from the database.

        :return:
        :rtype:
        """

        logger.info("Starting daily character cleanup tasks.")

        # Find all characters in corporation ID 1000001 (Doomheim)
        delete_characters = EveCharacter.objects.filter(corporation_id=1000001)
        count = delete_characters.count()

        logger.info(f"Found {count} characters to delete.")

        try:
            delete_characters.delete()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Error deleting characters in Doomheim: {e}")

    @staticmethod
    def _remove_non_account_characters() -> None:
        """
        Remove characters that are not associated with any user account.

        :return:
        :rtype:
        """

        logger.info("Starting daily non-account character cleanup tasks.")

        # Find all characters that are not associated with any user account
        delete_characters = EveCharacter.objects.filter(
            character_ownership__isnull=True
        )
        count = delete_characters.count()

        logger.info(f"Found {count} non-account characters to delete.")

        try:
            delete_characters.delete()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Error deleting non-account characters: {e}")

    @staticmethod
    def _remove_empty_corporations() -> None:
        """
        Remove corporations that have no associated characters.

        :return:
        :rtype:
        """

        logger.info("Starting daily empty corporation cleanup tasks.")

        # Find all corporations that have no associated characters
        character_corporation_ids = EveCharacter.objects.values_list(
            "corporation_id", flat=True
        ).distinct()
        delete_corporations = EveCorporationInfo.objects.exclude(
            corporation_id__in=character_corporation_ids
        )
        count = delete_corporations.count()

        logger.info(f"Found {count} empty corporations to delete.")

        try:
            delete_corporations.delete()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Error deleting empty corporations: {e}")

    @staticmethod
    def _remove_empty_alliances() -> None:
        """
        Remove alliances that have no associated corporations.

        :return:
        :rtype:
        """

        logger.info("Starting daily empty alliance cleanup tasks.")

        # Find all alliances that have no associated corporations
        character_alliance_ids = (
            EveCharacter.objects.values_list("alliance_id", flat=True)
            .exclude(alliance_id__isnull=True)
            .distinct()
        )
        delete_alliances = EveAllianceInfo.objects.exclude(
            alliance_id__in=character_alliance_ids
        )
        count = delete_alliances.count()

        logger.info(f"Found {count} empty alliances to delete.")

        try:
            delete_alliances.delete()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Error deleting empty alliances: {e}")

    def _cleanup_empty_eveonline_data(self) -> None:
        """
        Cleanup EveOnline data by removing non-account characters, empty corporations, and empty alliances.

        :return:
        :rtype:
        """

        self._remove_non_account_characters()
        self._remove_empty_corporations()
        self._remove_empty_alliances()

    def cleanup_eveonline_data(self) -> None:
        """
        Cleanup EveOnline data by removing closed corporations and biomassed characters.

        :return:
        :rtype:
        """

        self._remove_closed_corporations()
        self._remove_biomassed_characters()
        self._cleanup_empty_eveonline_data()
