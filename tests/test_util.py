"""Test the options module
"""

import json
import logging
import os
import tempfile
import pytest

import yaml
from papilotte.util import get_options, transform_cli_options, validate_json
from papilotte.validator import JSONValidationError


def test_transform_cli_options_debug():
    "Test handling of 'debug' in transform_cli_options."
    cli_options = {"debug": True, "config_file": "foo"}
    result = transform_cli_options(**cli_options)
    assert result["log_level"] == "debug"

    cli_options["debug"] = False
    result = transform_cli_options(**cli_options)
    # only set if debug is True
    assert "log_level" not in result


def test_transform_cli_options_ignore():
    "Test if values from ignore_options are ignored in transform_cli_options."
    cli_options = {"debug": True, "config_file": "foo", "port": "9999"}
    result = transform_cli_options(**cli_options)
    assert "config_file" not in result
    assert "port" in result


def test_transform_cli_options_none_value():
    """Test if None values from ignore_options are ignored
    in transform_cli_options."""
    cli_options = {"debug": True, "port": None}
    result = transform_cli_options(**cli_options)
    assert "port" not in result


def test_get_options_default_values_only():
    "Test if reading from default_config works (no other config involved)."
    result = get_options()
    assert result["port"] == 5000
    assert result["host"] == "localhost"
    assert result["compliance_level"] == 1
    assert "openapi/ipif.yml" in result["spec_file"]
    assert result["base_path"] is None
    assert result["max_size"] == 200

    assert result["connector"] == "papilotte.connectors.mock"
    assert result["description"] == "Short description of the data the service provides"
    assert (
        result["provider"]
        == "Name of the individual or institution running the service"
    )
    assert result["contact"] == "contact@example.com"
    assert result["formats"] == ["application/json"]
    assert result["json_file"] == "/var/lib/papilotte/data.json"
    assert result["log_level"] == logging.INFO


def test_get_options_default_and_custom_config():
    "Test if default options and custom options are merged correctly."
    cfg_data = {
        "port": 9999,
        "host": "example.com",
        "log_level": "error",
        "debug": "true",
        "compliance_level": 0,
        "spec_file": "foo",
        "base_path": "otherapi",
        "max_size": 1000,
        "connector": "myconnector",
        "description": "foo",
        "provider": "bar",
        "contact": "user@example.com",
        "formats": ["application/json", "application/xml"],
        "json_file": "some_json_file",
    }
    dump = yaml.safe_dump(cfg_data)
    with tempfile.NamedTemporaryFile(suffix=".yml") as file_:
        file_.write(dump.encode())
        file_.seek(0)
        result = get_options(config_file=file_.name)
    assert result["port"] == 9999
    assert result["host"] == "example.com"
    assert result["debug"]
    assert result["compliance_level"] == 0
    assert result["spec_file"] == "foo"
    assert result["base_path"] == "otherapi"
    assert result["max_size"] == 1000

    assert result["connector"] == "myconnector"
    assert result["description"] == "foo"
    assert result["provider"] == "bar"
    assert result["contact"] == "user@example.com"
    assert result["formats"] == ["application/json", "application/xml"]
    assert result["json_file"] == "some_json_file"
    assert result["log_level"] == logging.ERROR


def test_get_options_default_and_custom_and_cli():
    "Test if merging of options from default config + custom conf + cli conf works."
    cfg_data = {
        "port": 9999,
        "host": "example.com",
        "log_level": "error",
        "debug": "true",
        "compliance_level": 0,
        "spec_file": "foo",
        "base_path": "otherapi",
        "max_size": 1000,
        "connector": "myconnector",
        "description": "foo",
        "provider": "bar",
        "contact": "user@example.com",
        "formats": ["application/json", "application/xml"],
        "json_file": "some_json_file",
    }
    dump = yaml.safe_dump(cfg_data)
    with tempfile.NamedTemporaryFile(suffix=".yml") as file_:
        file_.write(dump.encode())
        file_.seek(0)
        result = get_options(
            config_file=file_.name,
            spec_file="xxx",
            port="8888",
            debug="False",
            compliance_level="2",
            connector="foobar",
            base_path="zzz",
        )
    assert result["port"] == 8888
    assert result["host"] == "example.com"
    # assert not result['debug']
    assert result["compliance_level"] == 2
    assert result["spec_file"] == "xxx"
    assert result["base_path"] == "zzz"
    assert result["max_size"] == 1000

    assert result["connector"] == "foobar"
    assert result["description"] == "foo"
    assert result["provider"] == "bar"
    assert result["contact"] == "user@example.com"
    assert result["formats"] == ["application/json", "application/xml"]
    assert result["json_file"] == "some_json_file"
    # assert result['log_level'] == logging.ERROR


def test_get_options_default_and_custom_and_cli_missing_value():
    "Test if merging of options from default config + custom conf + cli conf works."
    cfg_data = {
        "port": 9999,
        "host": "example.com",
        "log_level": "error",
        "debug": "true",
        "compliance_level": 0,
        "spec_file": "foo",
        "base_path": "otherapi",
        "max_size": 1000,
        "connector": "myconnector",
        "description": "foo",
        "provider": "bar",
        "formats": ["application/json", "application/xml"],
        "json_file": "some_json_file",
    }
    dump = yaml.safe_dump(cfg_data)
    with tempfile.NamedTemporaryFile(suffix=".yml") as file_:
        file_.write(dump.encode())
        file_.seek(0)
        result = get_options(
            config_file=file_.name,
            spec_file="xxx",
            port="8888",
            debug="False",
            compliance_level="2",
            connector="foobar",
            base_path="zzz",
        )
    assert result["port"] == 8888
    assert result["host"] == "example.com"
    # assert not result['debug']
    assert result["compliance_level"] == 2
    assert result["spec_file"] == "xxx"
    assert result["base_path"] == "zzz"
    assert result["max_size"] == 1000

    assert result["connector"] == "foobar"
    assert result["description"] == "foo"
    assert result["provider"] == "bar"
    assert result["contact"] == "contact@example.com"
    assert result["formats"] == ["application/json", "application/xml"]
    assert result["json_file"] == "some_json_file"


def test_validate_json(minimal_factoid):
    "Run validate_json with a valid factoid."

    data_file = tempfile.mkstemp(suffix='.json')[1]
    data = []
    data.append(minimal_factoid)
    options = {
        'connector': 'papilotte.connectors.json',
        'json_file': data_file
    }
    try:
        with open(data_file, 'w') as jsonfile:
            json.dump(data, jsonfile)
        validate_json(options)
    except Exception as err:
        raise err
    finally:
        os.unlink(data_file)

def test_validate_json_with_invalid_data(minimal_factoid):
    "Run validate_json with a invalid factoid."

    data_file = tempfile.mkstemp(suffix='.json')[1]
    #del minimal_factoid['source']
    del minimal_factoid['@id']
    data = []
    data.append(minimal_factoid)
    options = {
        'connector': 'papilotte.connectors.json',
        'json_file': data_file
    }
    with open(data_file, 'w') as jsonfile:
        json.dump(data, jsonfile)
    with pytest.raises(JSONValidationError):
        validate_json(options)
    os.unlink(data_file)