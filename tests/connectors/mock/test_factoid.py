"""Tests for the mock Factoid Connector.
"""
from papilotte.connectors.mock.factoid import FactoidConnector

def test_constructor():
    options = {'foo': 'bar'}
    factoid = FactoidConnector(options)
    assert factoid.options['foo'] == 'bar'

def test_get(factoidconnector):
    "Find a specific factoid by id"
    source = factoidconnector.get('Factoid 006')
    assert source['@id'] == 'Factoid 006'

def test_get_not_found(factoidconnector):
    "No such Source"
    assert factoidconnector.get('xxxx') is None

def test_search_without_filters(factoidconnector):
    "Get a list of sources."
    result = factoidconnector.search(30, 1)
    assert len(result) == 30  # we only have 25 different source objects
    assert result[0]['@id'] == 'Factoid 001'

def test_search_with_paging(factoidconnector):
    "Test if paging works correctly: we have 100 different factoids."
    result = factoidconnector.search(10, 1)
    assert len(result) == 10
    assert result[0]['@id'] == 'Factoid 001'
    assert result[-1]['@id'] == 'Factoid 010'

    result = factoidconnector.search(10, 2)
    assert len(result) == 10
    assert result[0]['@id'] == 'Factoid 011'
    assert result[-1]['@id'] == 'Factoid 020'

def test_search_with_filter(factoidconnector):
    "Filter by label"
    assert len(factoidconnector.search(30, 1, factoidId='Factoid 006')) == 1
    assert len(factoidconnector.search(30, 1, s='Label Source 006')) == 4
    assert len(factoidconnector.search(30, 1, st='F5S1')) == 1
    assert len(factoidconnector.search(30, 1, p='http://example.com/5')) == 30

def test_count(factoidconnector):
    "Test counting of (filtered) sources."
    assert factoidconnector.count() == 100
    assert factoidconnector.count(s="Source 001") == 4
    assert factoidconnector.count(s='Label Source 01') == 40


# TODO: tests for save when implemented
# TODO: tests for update when implemented
# TODO: tests for delete when implemented
