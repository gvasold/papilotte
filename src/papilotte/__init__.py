import sys
import logging
import connexion
from connexion.resolver import RestyResolver
from . import util
import papilotte

__version__ = "0.1.4.dev1"

logger = logging.getLogger("papilotte")


if sys.version_info.major < 3 or (
    sys.version_info.major == 3 and sys.version_info.minor < 5):
    print("Papilotte requires Python version 3.5 or higher.")
    sys.exit(1)


def create_app(**cli_options):
    """Create the app object."""
    papilotte.options = util.get_options(**cli_options)
    # Only used for json connector
    util.validate_json(papilotte.options)
    app = connexion.FlaskApp(
        __name__,
        port=papilotte.options["port"],
        host=papilotte.options["host"],
        debug=papilotte.options["log_level"] == logging.DEBUG,
    )
    app.add_api(
        papilotte.options["spec_file"],
        base_path=papilotte.options["base_path"],
        resolver=RestyResolver("papilotte.api"),
        strict_validation=True,
        validate_responses=True,
    )
    return app
