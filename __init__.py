'''
Initialization Module to force lp_settings and lp_logging to load first to ensure globals are populated correctly.
'''
#import logging as _logging
from legopython import (
    lp_api,
    lp_awssession,
    lp_dbsecrets,
    lp_dynamodb,
    lp_general,
    lp_logging,
    lp_interface,
    lp_postgresql,
    lp_s3,
    lp_secretsmanager,
    lp_settings
)
from legopython.__metadata__ import __description__, __license__, __title__, __version__

__all__ = [
    "lp_api",
    "lp_awssession",
    "lp_dbsecrets",
    "lp_dynamodb",
    "lp_general",
    "lp_logging",
    "lp_interface",
    "lp_postgresql",
    "lp_s3",
    "lp_secretsmanager",
    "lp_settings",
    "__description__",
    "__license__",
    "__title__",
    "__version__",
]
#_logging.getLogger("legopython").addHandler(_logging.NullHandler())
