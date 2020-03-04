"""Pytest fixtures for json tests.
"""

import os
import json
import pytest
import papilotte.configuration
#from papilotte.connectors import mock
import toml

#from papilotte.connectors import mock as mockconnector

#from papilotte import mockdata


@pytest.fixture
def configuration():
    "Return a complete custom configuration dict for configuration testing."

    return {
        'server': {
            'port': 7777,
            'host': 'example.com',
            'debug': True,
            'strictValidation': False,
            'responseValidation': True,
            'connector': 'papilotte.connectors.pony'
        },
        'logging': {
            'logLevel': 'debug',
            'logTo': "syslog",
            "logFile": "foo.bar",
            "maxLogFileSize": "10077",
            "keepLogFiles": 5,
            "logHost": "foo.foo.foo",
            "logPort": 1744
        },
        'api': {
            'complianceLevel': 0,
            'specFile': papilotte.configuration.default_spec_file,
            'basePath': '/api/v2',
            'maxSize': 500,
            'formats': ['application/json', 'application/xml']
        },
        'metadata': {
            'description': 'foo',
            'provider': 'bar',
            'contact': 'foo@bar.com'
        },
        # TODO: set some values
        'connector': {
        }
    }

@pytest.fixture
def configfile(tmp_path, configuration):
    """Return path to a toml formated config file.

    This file contains values from the configuration fixture.
    """
    base_path = tmp_path / "cfg"
    base_path.mkdir()
    cfg_file = base_path / "config.toml"
    cfg_file.write_text(toml.dumps(configuration))
    return cfg_file    


# @pytest.fixture
# def data1():
#     "Return the first mockdata factoid as dict."
#     data ={'factoids': []}
#     for i, factoid in enumerate(mockdata.make_factoids(1)):
#         if i == 1:
#             break
#         data['factoids'].append(factoid)
#     return data


# @pytest.fixture
# def data200():
#     "Return 200 mockdata factoids as dict"
#     data ={'factoids': []}
#     for i, factoid in enumerate(mockdata.make_factoids(1)):
#         if i == 200:
#             break
#         data['factoids'].append(factoid)
#     return data

# @pytest.fixture
# def cfg_template():
#     "Return a complete custom configuration dict."

#     return {
#         'server': {
#             'port': 7777,
#             'host': 'example.com',
#             'debug': True,
#             'strictValidation': False,
#             'responseValidation': True,
#             'connector': 'papilotte.connectors.pony'
#         },
#         'logging': {
#             'logLevel': 'debug',
#             'logTo': "syslog",
#             "logFile": "foo.bar",
#             "maxLogFileSize": "10077",
#             "keepLogFiles": 5,
#             "logHost": "foo.foo.foo",
#             "logPort": 1744
#         },
#         'api': {
#             'complianceLevel': 0,
#             'specFile': papilotte.configuration.default_spec_file,
#             'basePath': '/api/v2',
#             'maxSize': 500,
#             'formats': ['application/json', 'application/xml']
#         },
#         'metadata': {
#             'description': 'foo',
#             'provider': 'bar',
#             'contact': 'foo@bar.com'
#         },
#         # TODO: set some values
#         'connector': {
#         }
#     }
