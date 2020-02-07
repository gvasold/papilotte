import json
import logging
import os
import sys
from collections import ChainMap

from jsonschema.exceptions import ValidationError
from pkg_resources import resource_filename

import yaml
from papilotte import validator
from papilotte.connectors.json.reader import read_json_file

from papilotte.errors import ConfigurationError


options = {}

LOG_LEVELS = {
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


def transform_cli_options(**cli_params):
    """Convert options from cli_params to config like options.
    # TODO: check which params are cli params??
    # TODO: keep log level and 'debug' option apart
    # only used with the built-in server (Flask)
    """
    options = {}
    ignore_options = ("config_file", "debug")
    if cli_params.get("debug", False):
        options["log_level"] = "debug"
    for param, value in cli_params.items():
        if value is not None and param not in ignore_options:
            options[param] = value
    return options


def get_options(**cli_params):
    """Return a dict of options joint from all configurations.

    TODO: add reading from environment variables
    :param config_file: Path to the configuration file
    :type config_file: str
    :param **cli_options: A dict of options set via command line.
    :type cli_options: dict
    :return: A dict of options
    :rtype: dict
    """
    cli_options = transform_cli_options(**cli_params)
    default_cfg_file = resource_filename(__name__, "config/default_config.yml")
    default_spec_file = resource_filename(__name__, "openapi/ipif.yml")
    with open(default_cfg_file) as file_:
        default_config = yaml.safe_load(file_)
        default_config["spec_file"] = default_spec_file

    custom_config = {}
    if cli_params.get("config_file") is not None:
        with open(cli_params["config_file"]) as file_:
            custom_config = yaml.safe_load(file_)

    options = dict(ChainMap(cli_options, custom_config, default_config))
    # cast to expected data types
    options["log_level"] = LOG_LEVELS[options["log_level"]]
    for key, value in options.items():
        if value is not None:
            if key in ("default_size", "max_size", "compliance_level", "port"):
                options[key] = int(value)
    return options


def validate_json(options):
    """Check in json file contains valid data if the json connector is used.
    :param options: The server configuration.
    :type options: dict
    :raises: JSONValidationError if json file cannot be validated aginst the 
             IPIF OpenAPI spec.
    :return: None
    """
    if options["connector"] == "papilotte.connectors.json":
        spec_file = options.get("spec_file")
        json_file = options.get("json_file")
        strict_validation = options.get("strict_validation")
        factoids = read_json_file(json_file)
        try:
            for factoid in factoids:
                validator.validate(factoid, strict_validation, spec_file)
        except ValidationError as err:
            msg = (
                "'{}' contains invalid factoids:\n{}"
                "\nUse the 'validate_factoids.py' script to validate your data."
            ).format(json_file, validator.make_readable_validation_msg(err))
            raise validator.JSONValidationError(msg)


def validate_log_options(options, log_handlers):
    """Validate logging specific options.

    :param options: a dictionary of configuration options
    :type options: dict
    :param log_handlers': a list of log handler types
    :type log_handlers: list of strings
    :raises: error.ConfigurationError
    """
    ALLOWED_HANDLERS = ('console', 'file', 'syslog')
    # minimal validation for supported log_handlers
    for hdl in log_handlers:
        if hdl not in ALLOWED_HANDLERS:
            raise ConfigurationError("'{}' is not an allowed value for log_handlers!".format(hdl))

    # file log handler needs a log_file value
    if 'file' in log_handlers:
        if not 'log_file' in options or options['log_file'] is None:
            raise ConfigurationError("'When using the log_handler 'file', you must specify a value for 'log_file'!")
        else:
            log_dir = os.path.abspath(os.path.dirname(options['log_file']))
            if not os.path.isdir(log_dir):
                raise ConfigurationError("Log directory '{}' does not exist.".format(log_dir))


def get_logging_configuration(options):
    """ TODO: check for missing options
    # SMTPHandler (error only)??
    """
    # convert log handlers to list
    if "log_handlers" in options and options["log_handlers"]:
        log_handlers = [hdl.strip() for hdl in options['log_handlers'].split()]
    else:
        log_handlers = ['console']
    validate_log_options(options, log_handlers)
    cfg = {
        "version": 1,
        "handlers": {}
    }
    for hdl in log_handlers:
        if hdl == "console":
            cfg["handlers"]["console"] = {
                "class": "logging.StreamHandler",
                "level": options['log_level'],
                "stream": sys.stdout
            }
        elif hdl == "syslog":
            cfg["handlers"]["syslog"] = {
                "class": "logging.handlers.SysLogHandler",
                "level": options['log_level'],
            }
        elif hdl == "file":
            cfg["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                # "formatter": None,
                "filename": options['log_file'],  
                "maxBytes": 100000,
                "backupCount": 3,
                "level": options['log_level'],
            }
    return cfg
