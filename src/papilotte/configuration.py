import importlib
import os
import re

import toml
from pkg_resources import resource_filename

import voluptuous as vt
from papilotte.exceptions import ConfigurationError

default_spec_file = resource_filename(__name__, "openapi/ipif.yml")

# The configuration validation schema (without connect config)
schema = vt.Schema(
    {
        "server": {
            vt.Required("port", default=5000): vt.All(vt.Coerce(int), vt.Range(min=1)),
            vt.Required("host", default="localhost"): vt.All(str, vt.Length(min=1)),
            vt.Required("debug", default=False): vt.Boolean(),
            vt.Required("connector", default="papilotte.connectors.pony"): vt.All(
                str, vt.Length(min=2)
            ),
            vt.Required("strictValidation", default="True"): vt.Boolean(),
            vt.Required("responseValidation", default="False"): vt.Boolean(),
        },
        "logging": {
            vt.Required("logLevel", default="info"): vt.Any(
                "debug", "info", "warn", "error"
            ),
            vt.Required("logTo", default="console"): vt.Any(
                "console", "file", "syslog"
            ),
            # only in 'file'
            vt.Required("logFile", default=""): str,
            vt.Required("maxLogFileSize", default="1M"): str,
            vt.Required("keepLogFiles", default=3): vt.Coerce(int),
            # only syslog
            vt.Required("logHost", default="localhost"): vt.All(str, vt.Length(min=2)),
            vt.Required("logPort", default=514): vt.All(
                vt.Coerce(int), vt.Range(min=1)
            ),
        },
        "api": {
            vt.Required("complianceLevel", default=1): vt.All(
                vt.Coerce(int), vt.Range(min=0, max=2)
            ),
            vt.Required("specFile", default=default_spec_file): vt.All(vt.IsFile()),
            vt.Required("basePath", default="/api"): vt.All(str, vt.Length(min=1)),
            vt.Required("maxSize", default=200): vt.All(
                vt.Coerce(int), vt.Range(min=5)
            ),
            vt.Required("formats", default=["application/json"]): vt.All(
                list, vt.Length(min=1)
            ),  # FIMXE: validation?
        },
        # FIMXE: should this be required withould default values?
        "metadata": {
            vt.Required("description", default="No description available"): str,
            vt.Required(
                "provider", default="No data provider information available"
            ): str,
            vt.Required("contact", default="No contact information available"): str,
        },
    }
)

def compute_bytes(value):
    """Return value like `3M` unto bytes.
    """
    factors = {
        'k': 1024,
        'kb': 1024,
        'm': 1024 * 1024,
        'mb': 1024 * 1024,
        'g': 1024 * 1024 * 1024,
        'gb': 1024 * 1024 * 1024
    }
    try:
        return int(value)
    except ValueError:
        m = re.match(r'(\d+\.?\d*)\s*(\w+)', value)
        if m:
            num_part = float(m.group(1))
            try:
                factor = factors[m.group(2).lower()]
                return int(num_part * factor)
            except KeyError:
                raise ConfigurationError("'{}' is not an allowed value for 'maxLogFileSize'".format(value))
        else:
            raise ConfigurationError("'{}' is not an allowed value for 'maxLogFileSize'".format(value))



def validate(cfg_dict, context):
    """Validate and set default values if necessary for cfg_dict.

    Returns the dict with added default values.
    """
    # Remove connector config temporarily during validation
    connector_cfg = cfg_dict.pop("connector", {})
    try:
        cfg = schema(cfg_dict)
    except vt.error.Error as err:
        msg = "{} ({})".format(str(err), context)
        raise ConfigurationError(msg)
    try:  # try to load the connector_module
        connector_module = importlib.import_module(cfg["server"]["connector"])
    except ModuleNotFoundError:
        raise ConfigurationError(
            "Cannot load connector module '{}' ({}).".format(
                cfg["server"]["connector"], context
            )
        )
    connector_cfg = connector_module.validate(connector_cfg)
    # make module available in configuration
    connector_cfg["connector_module"] = connector_module
    cfg["connector"] = connector_cfg
    # validate `logTo` depended settings
    if cfg["logging"]["logTo"] == "file":
        if not cfg["logging"]["logFile"]:
            raise ConfigurationError("'logFile' must be configured")
    return cfg


def get_default_configuration():
    """Return a dict containing the default configuration.

    This is mostly extracted from the validation schema.
    """
    cfg = {"server": {}, "logging": {}, "api": {}, "metadata": {}}
    cfg = schema(cfg)  # set the default values
    # TODO: set defaults for default connector
    cfg["connector"] = {}
    return cfg


def read_configfile(filename):
    cfg = toml.load(filename)
    return validate(cfg, "configuration file: '{}".format(filename))


def underline_to_camelcase(name):
    "Convert snake_name to snakeName."
    buf = []
    uc_next = False
    for c in name:
        if c == "_":
            uc_next = True
        else:
            if uc_next:
                buf.append(c.upper())
                uc_next = False
            else:
                buf.append(c)
    return "".join(buf)


def update_from_environment(configuration, env_dict=None):
    """Update an existing configuration dict from env_dict.

    env_dict is only used for testing.
    """
    if not env_dict:
        env_dict = os.environ
    for name, value in env_dict.items():
        if name.startswith("PAPILOTTE_"):
            _, section, sname = name.lower().split("_", 2)
            sname = underline_to_camelcase(sname)
            if section in ("server", "api", "metadata", "logging"):
                if sname in configuration[section]:
                    configuration[section][sname] = value
                else:
                    raise ConfigurationError(
                        "Unknown envrionment variable: '{}'".format(name)
                    )
            elif section == "connector":
                configuration["connector"][sname] = value
            else:
                raise ConfigurationError(
                    "Unknown envrionment variable: '{}'".format(name)
                )
    return validate(configuration, "environment")


def update_from_cli(configuration, cli_config):
    "Extract configuration values from command line arguments."
    # map cli_config properties to configuration properties
    mappings = {
        "spec_file": ("api", "specFile"),
        "port": ("server", "port"),
        "host": ("server", "host"),
        "debug": ("server", "debug"),
        "compliance_level": ("api", "complianceLevel"),
        "connector": ("server", "connector"),
        "base_path": ("api", "basePath"),
        "strict_validation": ("server", "strictValidation"),
        "response_validation": ("server", "responseValidation"),
    }
    for key, conf_keys in mappings.items():
        if key in cli_config:
            configuration[conf_keys[0]][conf_keys[1]] = cli_config[key]
    # if we set debug via cli we might want the full log output, too
    if configuration['server']['debug']:
        configuration['logging']['logLevel'] = 'debug'
    return validate(configuration, "command line arguments")


def get_configuration(configfile=None, cli_cfg={}):
    """Return the configuration as dictionary.

    The configuration is constructed in this order:

        1. Values from the default configuration
        2. Values from configuration file (configfile), if specified
        3. Values from .env (if such a file exists)
        4. Values from environment variables (Starting with PAPILOTTE_)
        5. Values from command line arguments

    If a values is set in a later stage, this value will be used.
    So for example, server.port spezified via environment variable 
    will overrule the value set in the configuration file.
    """
    if configfile:
        cfg = read_configfile(configfile)
    else:
        cfg = get_default_configuration()
    cfg = update_from_environment(cfg, os.environ)
    cfg = update_from_cli(cfg, cli_cfg)
    cfg['logging']['maxLogFileSize'] = compute_bytes(cfg['logging']['maxLogFileSize'])
    return cfg
