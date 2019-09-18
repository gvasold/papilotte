"""Pytest fixtures for json tests.
"""


import pytest

from papilotte.connectors import mock


@pytest.fixture
def mock_factoid():
    "Return a full mock Factoid"
    generator = mock.mockdata.generate_factoid()
    data = next(generator)
    return data


@pytest.fixture
def minimal_factoid():
    "Return a mock factoid containing only the required properties"
    factoid = {
        "@id": "f1",
        "person": {"@id": "p1"},
        "source": {"@id": "s1"},
        "statement": {"@id": "st1"},
        "createdBy": "Foo Bar",
        "createdWhen": "2019-01-17",
    }
    return factoid 
