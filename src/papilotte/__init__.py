import logging
import sys

__version__ = "0.3.0.dev27"

logger = logging.getLogger("papilotte")


if sys.version_info.major < 3 or (
    sys.version_info.major == 3 and sys.version_info.minor < 6):
    print("Papilotte requires Python version 3.6 or higher.")
    sys.exit(1)
