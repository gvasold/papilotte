import logging
from collections import ChainMap
from pkg_resources import resource_filename
import yaml

options = {}

LOG_LEVELS = {
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}


def transform_cli_options(**cli_params):
    """Convert options from cli_params to config like options.
    # TODO: check which params are cli params??
    # only used with the built-in server (Flask)
    """
    options = {}
    ignore_options = ('config_file', 'debug')
    if cli_params.get('debug', False):
        options['log_level'] = 'debug'
    for param, value in cli_params.items():
        if value is not None and param not in ignore_options:
            options[param] = value
    return options


def get_options(**cli_params):
    """Return a dict of options joint from all configurations.

    FIXME: add reading from environment variables
    :param config_file: Path to the configuration file
    :type config_file: str
    :param **cli_options: A dict of options set via command line.
    :type cli_options: dict
    :return: A dict of options
    :rtype: dict
    """
    cli_options = transform_cli_options(**cli_params)
    default_cfg_file = resource_filename(__name__,
                                         'config/default_config.yml')
    default_spec_file = resource_filename(__name__, 'openapi/ipif.yml')
    with open(default_cfg_file) as file_:
        default_config = yaml.safe_load(file_)
        default_config['spec_file'] = default_spec_file

    custom_config = {}
    if cli_params.get('config_file') is not None:
        with open(cli_params['config_file']) as file_:
            custom_config = yaml.safe_load(file_)

    options = dict(ChainMap(cli_options, custom_config, default_config))
    # cast to expected data types
    options['log_level'] = LOG_LEVELS[options['log_level']]
    for key, value in options.items():
        if value is not None:
            if key in ('default_size', 'max_size', 'compliance_level',
                       'port'):
                options[key] = int(value)
    return options
