"""A papilotte connector to relational databases using the pony ORM
"""

from flask import current_app as app
from pony import orm

from papilotte.exceptions import ConfigurationError

from . import database
from .factoid import FactoidConnector
from .person import PersonConnector
from .source import SourceConnector
from .statement import StatementConnector


def validate(configuration):
    """Validate the connector specific configuration.

    Set default values where appropriate.

    :raises: papilotte.config.Configuration Error
    :return: a valid configuration as dict
    """
    provider = configuration.get("provider", "sqlite")
    configuration["provider"] = provider
    if provider == "sqlite":
        filename = configuration.get("filename")
        if not filename:
            filename = ":memory:"
        configuration["filename"] = filename
    elif provider in ("postgresql", "mysql"):
        configuration["host"] = configuration.get("host", "")
        configuration["user"] = configuration.get("user", "")
        configuration["password"] = configuration.get("password", "")
        configuration["database"] = configuration.get("database", "")
        if configuration.get("port"):
            configuration["port"] = configuration["port"]
        else:
            if provider == "postgresql":
                configuration["port"] = "5432"
            else:
                configuration["port"] = "3306"

    elif provider == "oracle":
        # todo
        raise ConfigurationError(
            "Connecting to oracle databases is not implemented yet"
        )
    else:
        raise ConfigurationError(
            "Invalid value for 'connector.provider': '{}".format(provider)
        )
    return configuration


def initialize(connector_cfg):
    """Prepare database and put it into configuration.
    """
    new_config = {}
    if connector_cfg["provider"] == "sqlite":
        db = database.make_db(provider="sqlite", filename=connector_cfg["filename"])
    elif connector_cfg["provider"] in ("postgresql", "mysql"):
        db = database.make_db(
            provider=connector_cfg["provider"],
            host=connector_cfg["host"],
            port=connector_cfg["port"],
            user=connector_cfg["user"],
            password=connector_cfg["password"],
            database=connector_cfg["database"],
        )
    new_config["db"] = db
    return new_config

