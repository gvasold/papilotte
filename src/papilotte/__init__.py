import sys
import logging
import connexion
#from connexion.resolver import RestyResolver
from papilotte.resolver import PapiResolver
from . import util
import papilotte
from logging.config import dictConfig

__version__ = "0.1.4.dev1"

logger = logging.getLogger("papilotte")


if sys.version_info.major < 3 or (
    sys.version_info.major == 3 and sys.version_info.minor < 5):
    print("Papilotte requires Python version 3.5 or higher.")
    sys.exit(1)

def get_logging_configuration(options):
    # TODO: check for missing options
    # SMTPHandler (error only)??
    cfg = {
        "version": 1,
        "handlers": {
            "console": {
                "class": logging.StreamHandler,
                "level": logging.INFO,
                "stream": sys.stdout
            },
            "file": {
                "class": logging.handlers.RotatingFileHandler,
                #"formatter": None,
                "filename": None, # FIXME
                "maxBytes": 100000,
                "backupCount": 3
            },
            "syslog": {
                "class": logging.handlers.SysLogHandler
            }
        },
        "root": {
            "handlers": ['syslog']
        }
    }

    return cfg


def create_app(**cli_options):
    """Create the app object."""
    papilotte.options = util.get_options(**cli_options)
    #dictConfig(get_logging_configuration(papilotte.options))
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
        resolver=PapiResolver("papilotte.api"),
        strict_validation=True,
        validate_responses=True,
    )
    return app
