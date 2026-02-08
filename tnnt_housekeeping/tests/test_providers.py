"""
Unit tests for the providers in tnnt_housekeeping.providers.
"""

# Standard Library
import logging
from unittest.mock import Mock

# TN-NT Auth Housekeeping
from tnnt_housekeeping.providers import AppLogger
from tnnt_housekeeping.tests import BaseTestCase


class TestAppLogger(BaseTestCase):
    """
    Unit tests for the AppLogger class in tnnt_housekeeping.providers.
    """

    def test_adds_prefix_to_log_message(self):
        """
        Test that the AppLogger correctly adds the prefix to log messages.

        :return:
        :rtype:
        """

        mock_logger = Mock(spec=logging.Logger)

        logger = AppLogger(mock_logger, "PREFIX")
        logger.info("Test message")

        mock_logger.log.assert_called_once_with(logging.INFO, "[PREFIX] Test message")

    def test_handles_empty_prefix(self):
        """
        Test that the AppLogger correctly handles an empty prefix.

        :return:
        :rtype:
        """

        mock_logger = Mock(spec=logging.Logger)

        logger = AppLogger(mock_logger, "")
        logger.info("Test message")

        mock_logger.log.assert_called_once_with(logging.INFO, "[] Test message")

    def test_handles_empty_message(self):
        """
        Test that the AppLogger correctly handles an empty log message.

        :return:
        :rtype:
        """
        mock_logger = Mock(spec=logging.Logger)

        logger = AppLogger(mock_logger, "PREFIX")
        logger.info("")

        mock_logger.log.assert_called_once_with(logging.INFO, "[PREFIX] ")

    def test_handles_kwargs_in_log_message(self):
        """
        Test that the AppLogger correctly handles additional keyword arguments in log messages.

        :return:
        :rtype:
        """

        mock_logger = Mock(spec=logging.Logger)

        logger = AppLogger(mock_logger, "PREFIX")
        logger.info("Test message", extra={"key": "value"})

        mock_logger.log.assert_called_once_with(
            logging.INFO, "[PREFIX] Test message", extra={"key": "value"}
        )
