"""Tests for the mock StatementConnector.
"""
from papilotte.connectors.mock.statement import StatementConnector


def test_constructor():
    options = {'foo': 'bar'}
    stmt = StatementConnector(options)
    assert stmt.options['foo'] == 'bar'


def test_get(statementconnector):
    "Find a specific statement by id"
    stmt = statementconnector.get("F21S1")
    assert stmt["@id"] == "F21S1"


def test_get_not_found(statementconnector):
    "No such Statement"
    assert statementconnector.get("xxxx") is None


def test_search_without_filters(statementconnector):
    "Get a list of statements."
    result = statementconnector.search(30, 1)
    assert len(result) == 30
    assert result[0]["@id"] == "F1S1"


def test_search_with_paging(statementconnector):
    "Test if paging works correctly."
    result = statementconnector.search(10, 1)
    assert len(result) == 10
    assert result[0]["@id"] == "F1S1"
    assert result[-1]["@id"] == "F10S1"

    result = statementconnector.search(10, 2)
    assert len(result) == 10
    assert result[0]["@id"] == "F11S1"
    assert result[-1]["@id"] == "F20S1"


def test_search_with_filter(statementconnector):
    "Test filtering by label"
    assert len(statementconnector.search(30, 1, statementId="F5S1")) == 1
    assert len(statementconnector.search(30, 1, st="Place 43_1")) == 2
    assert len(statementconnector.search(30, 1, st="Related person 2_1")) == 3
    assert (
        len(statementconnector.search(30, 1, st="http://example.com/member_of/7/1"))
        == 4
    )


def test_count(statementconnector):
    "Test counting of (filtered) sources."
    assert statementconnector.count() == 100
    assert statementconnector.count(st="F6S1") == 1
    assert statementconnector.count(st="Related person 2_1") == 3
