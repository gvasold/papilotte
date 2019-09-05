"""Pytest fictures for mocj tests.
"""


import pytest

from papilotte.connectors import mock


@pytest.fixture
def sourceconnector():
    "Return a mock SourceConnector mock object."
    return mock.source.SourceConnector({})  # no options


@pytest.fixture
def personconnector():
    "Return a mock PersonConnector mock object."
    return mock.person.PersonConnector({})  # no options


@pytest.fixture
def statementconnector():
    "Return a mock StatementConnecor object"
    return mock.statement.StatementConnector({})  # no options


@pytest.fixture
def factoidconnector():
    "Return a mock FactoidConnector object"
    return mock.factoid.FactoidConnector({})


@pytest.fixture
def mockdata():
    "Return 100 mock Factoids"
    data = []
    generator = mock.mockdata.generate_factoid()
    for _ in range(100):
        data.append(next(generator))
    return data


@pytest.fixture
def qfilter():
    "Return a mock.filter object"
    return mock.filter.Filter()
