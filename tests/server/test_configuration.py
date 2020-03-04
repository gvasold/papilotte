# from papilotte.validator import get_schema, validate
# from jsonschema.exceptions import ValidationError
import logging
import papilotte.configuration
from papilotte.exceptions import ConfigurationError
import pytest
import toml
import os


@pytest.fixture
def cli_config():
    "Return a valid mock cli configuration."
    return {
        'spec_file': papilotte.configuration.default_spec_file,
        'port':  9876,
        'host': 'foo.example.com',
        'debug': True,
        'compliance_level': 2,
        'connector': 'papilotte.connectors.pony',
        'base_path': '/foobar'
    }


def test_get_default_configuration():
    "get_default_configuration should extract defaults from schema default values."
    cfg = papilotte.configuration.get_default_configuration()
    assert "server" in cfg
    assert "api" in cfg
    assert "metadata" in cfg
    assert "connector" in cfg

    assert cfg["server"]["port"] == 5000
    assert cfg["server"]["host"] == "localhost"
    assert cfg["server"]["debug"] == False
    assert cfg["server"]["connector"] == "papilotte.connectors.pony"


    assert cfg["logging"]["logLevel"] == "info"
    assert cfg["logging"]["logFile"] == ""
    assert cfg["logging"]["maxLogFileSize"] == "1M"
    assert cfg["logging"]["keepLogFiles"] == 3


    assert cfg["api"]["complianceLevel"] == 1
    assert cfg["api"]["specFile"] == papilotte.configuration.default_spec_file
    assert cfg["api"]["basePath"] == "/api"
    assert cfg["api"]["maxSize"] == 200
    assert cfg["api"]["formats"] == ["application/json"]

    assert cfg["metadata"]["description"] == "No description available"
    assert cfg["metadata"]["provider"] == "No data provider information available"
    assert cfg["metadata"]["contact"] == "No contact information available"

    # TODO: test default connector configuration

def test_update_from_environment(configuration):
    env_dict = {
        'PAPILOTTE_SERVER_PORT': 8888,
        'PAPILOTTE_API_MAX_SIZE': 25,
        'PAPILOTTE_METADATA_CONTACT': 'foo bar',
        'PAPILOTTE_SERVER_STRICT_VALIDATION': False,
        'PAPILOTTE_SERVER_RESPONSE_VALIDATION': True
    }
    cfg = papilotte.configuration.update_from_environment(configuration, env_dict)
    assert cfg['server']['port'] == 8888
    assert cfg['api']['maxSize'] == 25
    assert cfg['metadata']['contact'] == 'foo bar'
    assert cfg['server']['strictValidation'] == False
    assert cfg['server']['responseValidation'] == True


def test_update_from_env_invalid_first_name(configuration):
    "Unknown env names must raise error."
    env_dict = {
        'PAPILOTTE_FOO_PORT': 8888,
    }
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.update_from_environment(configuration, env_dict)
    assert err.match('Unknown envrionment variable')

def test_update_from_env_invalid_second_name(configuration):
    "Unknown env names must raise error."
    env_dict = {
        'PAPILOTTE_API_PORT': 8888,
    }
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.update_from_environment(configuration, env_dict)
    assert err.match('Unknown envrionment variable')


def test_update_from_env_invalid_value(configuration):
    "Check if validation works for values taken form environment."
    env_dict = {
        'PAPILOTTE_SERVER_PORT': 'abc',
    }
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.update_from_environment(configuration, env_dict)
    assert err.match('expected int')


def test_update_from_cli(configuration, cli_config):
    cfg = papilotte.configuration.update_from_cli(configuration, cli_config)
    assert cfg['server']['port'] == 9876
    assert cfg['server']['host'] == 'foo.example.com'
    assert cfg['server']['connector'] == 'papilotte.connectors.pony'
    assert cfg['server']['debug'] is True
    assert cfg['api']['specFile'] == papilotte.configuration.default_spec_file
    assert cfg['api']['complianceLevel'] == 2
    assert cfg['api']['basePath'] == '/foobar'    

def test_get_configuration(configuration, configfile, cli_config):
    "Test if using default, configfile, env and cli leads to expected configuration."
    os.environ['PAPILOTTE_SERVER_HOST'] = 'hoo.foo.com'
    os.environ['PAPILOTTE_SERVER_PORT'] = '7171'
    del cli_config['host']
    cfg = papilotte.configuration.get_configuration(configfile, cli_config)
    assert cfg['logging']['logLevel'] == 'debug' # from config file
    assert cfg['server']['host'] == 'hoo.foo.com' # from env
    assert cfg['server']['port'] == 9876 # from cli
    

def test_underline_to_camelcase():
    assert papilotte.configuration.underline_to_camelcase('foo_bar_foo') == 'fooBarFoo'


def test_compute_bytes():
    """Test conversion to bytes.
    """
    assert papilotte.configuration.compute_bytes('123') == 123
    assert papilotte.configuration.compute_bytes('1k') == 1024
    assert papilotte.configuration.compute_bytes('1.5kb') == 1024 + 512
    assert papilotte.configuration.compute_bytes('1 m') == 1024 * 1024
    assert papilotte.configuration.compute_bytes('1 MB') == 1024 * 1024
    assert papilotte.configuration.compute_bytes('1 g') == 1024 * 1024 * 1024
    assert papilotte.configuration.compute_bytes('1 GB') == 1024 * 1024 * 1024

    with pytest.raises(ConfigurationError):
        papilotte.configuration.compute_bytes('1y')
