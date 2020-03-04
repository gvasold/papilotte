import sys
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler
import connexion
from papilotte.resolver import PapiResolver
import papilotte
import os
import toml

from papilotte import configuration

# logger = logging.getLogger(__name__)

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


def configure_logging(debug, **log_cfg):
    "Configure the app wide logger."
    logger = logging.getLogger("papilotte")
    logger.setLevel(LOG_LEVELS[log_cfg["logLevel"]])
    if debug or log_cfg["logTo"] == "console":
        logger.addHandler(logging.StreamHandler())
    if log_cfg["logTo"] == "file":
        logger.addHandler(RotatingFileHandler(
                log_cfg["logFile"],
                maxBytes=int(log_cfg["maxLogFileSize"]),
                backupCount=log_cfg["keepLogFiles"]
        ))
    elif log_cfg["logTo"] == "syslog":
        logger.addHandler(SysLogHandler(
                address=(log_cfg["logHost"], log_cfg["logPort"])
            ))


def create_app(config_file=None, cli_options={}):
    """Create the app object."""
    config = configuration.get_configuration(config_file, cli_options)
    configure_logging(config["server"]["debug"], **config["logging"])

    app = connexion.FlaskApp(
        __name__,
        port=config["server"]["port"],
        host=config["server"]["host"],
        debug=config["server"]["debug"],
    )
    # configure connexion
    app.add_api(
        config["api"]["specFile"],
        base_path=config["api"]["basePath"],
        resolver=PapiResolver("papilotte.api"),
        strict_validation=config["server"]["strictValidation"],
        validate_responses=config["server"]["responseValidation"]
    )
    connector_module = config['connector'].pop('connector_module')
    connector_configuration = config.pop('connector')

    # Set some extra config values needed by api and connector
    app.app.config['PAPI_CONNECTOR_MODULE'] = connector_module
    app.app.config['PAPI_MAX_SIZE'] = config['api']['maxSize']
    app.app.config['PAPI_COMPLIANCE_LEVEL'] = config['api']['complianceLevel']
    app.app.config['PAPI_METADATA'] = config['metadata']
    app.app.config['PAPI_FORMATS'] = config['api']['formats']
    connector_configuration = connector_module.initialize(connector_configuration)
    app.app.config['PAPI_CONNECTOR_CONFIGURATION'] = connector_configuration
    return app
