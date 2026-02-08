"""
TN-NT Housekeeping app config
"""

# Django
from django.apps import AppConfig

# TN-NT Auth Housekeeping
from tnnt_housekeeping import __version__


class TnntHousekeepingConfig(AppConfig):
    """
    TN-NT Housekeeping app config
    """

    name = "tnnt_housekeeping"
    label = "tnnt_housekeeping"
    verbose_name = f"Terra Nanotech Alliance Auth Houskeeping v{__version__}"
