"""Pytest fixtures for json tests.
"""

import os
import json
import pytest
import papilotte.configuration
#from papilotte.connectors import mock
import toml

#from papilotte.connectors import mock as mockconnector

from papilotte import mockdata



# ------------- Fixture for IPIF date (dictionaries)  ----------------

@pytest.fixture
def data1():
    "Return the first mockdata factoid as dict."
    data ={'factoids': []}
    for i, factoid in enumerate(mockdata.make_factoids(1)):
        if i == 1:
            break
        data['factoids'].append(factoid)
    return data


@pytest.fixture
def data200():
    "Return 200 mockdata factoids as dict"
    data ={'factoids': []}
    for i, factoid in enumerate(mockdata.make_factoids(1)):
        if i == 200:
            break
        data['factoids'].append(factoid)
    return data

