"""Tests for mock PersonConnector.
"""
from papilotte.connectors.mock.person import PersonConnector


def test_constructor():
    options = {'foo': 'bar'}
    person = PersonConnector(options)
    assert person.options['foo'] == 'bar'


def test_get_not_found(personconnector):
    "No such Person"
    assert personconnector.get('xxxx') is None


def test_search_without_filters(personconnector):
    "Get a paginated list of persons."
    result = personconnector.search(30, 1)
    assert len(result) == 15  # we only have 15 different person objects
    assert result[0]['@id'] == 'Person 001'

def test_search_with_paging(personconnector):
    "Test if paging works correctly: we have 15 different persons."
    result = personconnector.search(6, 1)
    assert len(result) == 6
    assert result[0]['@id'] == 'Person 001'
    assert result[-1]['@id'] == 'Person 006'

    result = personconnector.search(6, 2)
    assert len(result) == 6
    assert result[0]['@id'] == 'Person 007'
    assert result[-1]['@id'] == 'Person 012'

    result = personconnector.search(6, 3)
    assert len(result) == 3
    assert result[0]['@id'] == 'Person 013'
    assert result[-1]['@id'] == 'Person 015'

def test_search_with_filter(personconnector):
    "Filter by uri"
    assert len(personconnector.search(30, 1, personId='Person 012')) == 1
    assert len(personconnector.search(30, 1, p='Person 00')) == 9
    assert len(personconnector.search(30, 1, p='http://example.com/5')) == 13

def test_count(personconnector):
    "Test counting of (filtered) persons."
    assert personconnector.count() == 15
    assert personconnector.count(p="Person 006") == 1


# TODO: tests for save when implemented
# TODO: tests for update when implemented
# TODO: tests for delete when implemented
