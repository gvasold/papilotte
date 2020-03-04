"""Test parsing an validation of config file via read_configfile.
"""
import papilotte.configuration
import pytest
import tempfile
import toml

from papilotte.connectors import pony as mockconnector
from papilotte.exceptions import ConfigurationError

def test_read_configfile(configfile, configuration):
    "Test reading a complete config file whithout errors."
    cfg = papilotte.configuration.read_configfile(configfile)
    # this one is added during validation
    configuration['connector']['connector_module'] = mockconnector
    for section in configuration:
        for key in configuration[section]:
            assert cfg[section][key] == configuration[section][key], "Missmatch for [{}][{}]".format(section, key)

def test_invalid_port(configuration, tmp_path):
    "An invalid port value must raise ConfigurationError."
    configuration['server']['port'] = 'foo'
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('port')

def test_empty_port(configuration, tmp_path):
    "A missing port must lead to default port."
    del configuration['server']['port'] 
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))

    cfg = papilotte.configuration.read_configfile(cfile)
    assert cfg['server']['port'] == 5000

    # also value None must lead to default port
    configuration['server']['port'] = None 
    cfile.write_text(toml.dumps(configuration))
    cfg = papilotte.configuration.read_configfile(cfile)
    assert cfg['server']['port'] == 5000

def test_invalid_host(configuration, tmp_path):
    configuration['server']['host'] = ''
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('length')
    assert err.match('host')

def test_invalid_debug(configuration, tmp_path):
    configuration['server']['debug'] = 'foo'
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('expected boolean')
    assert err.match('debug')

def test_invalid_loglevel(configuration, tmp_path):
    configuration['logging']['logLevel'] = 'foo'
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('not a valid value')
    assert err.match('logLevel')

def test_missing_logfile(configuration, tmp_path):
    "If logTo is file, logFile must be set."
    configuration['logging']['logTo'] = 'file'
    configuration['logging']['logFile'] = ''
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match("'logFile' must be configured")



def test_invalid_api_compliance_level(configuration, tmp_path):
    configuration['api']['complianceLevel'] = 99
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('value must be at most 2 ')
    assert err.match('complianceLevel')

def test_invalid_api_base_path(configuration, tmp_path):
    configuration['api']['basePath'] = ''
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('length of value must be at least 1')
    assert err.match('basePath')

def test_invalid_api_spec_file(configuration, tmp_path):
    configuration['api']['specFile'] = '/foo/bar.yml'
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('not a file')
    assert err.match('specFile')

def test_invalid_api_max_size(configuration, tmp_path):
    configuration['api']['maxSize'] = 0
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('value must be at least ')
    assert err.match('maxSize')

    configuration['api']['maxSize'] = "foo"
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('expected int')
    assert err.match('maxSize')


def test_invalid_api_formats(configuration, tmp_path):
    configuration['api']['formats'] = []
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('value must be at least ')
    assert err.match('formats')

    configuration['api']['formats'] = 'foo'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('expected list')
    assert err.match('formats')


def test_invalid_config_name(configuration, tmp_path):
    configuration['server']['foo'] = 'bar'
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    with pytest.raises(ConfigurationError) as err:
        papilotte.configuration.read_configfile(cfile)
    assert err.match('extra keys not allowed')


def test_connector_config_is_not_validated(configuration, tmp_path):
    "Make sure that connector-part of config is not validated-"
    configuration['connector']['foo'] = 'bar'
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    cfg = papilotte.configuration.read_configfile(cfile)
    assert cfg['connector']['foo'] == 'bar'


def test_max_log_file_size(configuration, tmp_path):
    configuration['logging']['maxLogFileSize'] = "3M"
    cfile = tmp_path / 'papilotte.toml'
    cfile.write_text(toml.dumps(configuration))
    cfg = papilotte.configuration.get_configuration(cfile)
    assert cfg['logging']['maxLogFileSize'] == 3 * 1024 * 1024

