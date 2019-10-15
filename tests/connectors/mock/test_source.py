"""Test for the mock SourceConnector.
"""

from papilotte.connectors.mock.source import SourceConnector


def test_constructor():
    options = {'foo': 'bar'}
    source = SourceConnector(options)
    assert source.options['foo'] == 'bar'


def test_get(sourceconnector):
    "Find a specific source by id"
    source = sourceconnector.get('Source 006')
    assert source['@id'] == 'Source 006'

def test_get_not_found(sourceconnector):
    "No such Source"
    assert sourceconnector.get('xxxx') is None

def test_search_without_filters(sourceconnector):
    "Get a list of sources."
    result = sourceconnector.search(30, 1)
    assert len(result) == 25  # we only have 25 different source objects
    assert result[0]['@id'] == 'Source 001'

def test_search_with_paging(sourceconnector):
    "Test if paging works correctly: we have 25 different sources."
    result = sourceconnector.search(10, 1)
    assert len(result) == 10
    assert result[0]['@id'] == 'Source 001'
    assert result[-1]['@id'] == 'Source 010'

    result = sourceconnector.search(10, 2)
    assert len(result) == 10
    assert result[0]['@id'] == 'Source 011'
    assert result[-1]['@id'] == 'Source 020'

    result = sourceconnector.search(10, 3)
    assert len(result) == 5
    assert result[0]['@id'] == 'Source 021'
    assert result[-1]['@id'] == 'Source 025'

def test_search_with_filter(sourceconnector):
    "Filter by label"
    assert len(sourceconnector.search(30, 1, s='Source 006')) == 1
    assert len(sourceconnector.search(30, 1, s='Label Source 006')) == 1
    assert len(sourceconnector.search(30, 1, s='Label Source 001')) == 1
    assert len(sourceconnector.search(30, 1, s='http://example.com/5')) == 23 

def test_count(sourceconnector):
    "Test counting of (filtered) sources."
    assert sourceconnector.count() == 25
    assert sourceconnector.count(s="Source 006") == 1
    assert sourceconnector.count(s='Label Source 001') == 1


# TODO: tests for save when implemented
# TODO: tests for update when implemented
# TODO: tests for delete when implemented
