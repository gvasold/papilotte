"""Tests for papilotte.connectors.pony.statement
"""
import copy
import datetime

import pytest
from pony import orm

from papilotte.connectors.pony import statement

@pytest.fixture
def mockstatement1():
    "Return a single Statement as mock dict."
    return {
        "@id": "Foo99",
        "createdBy": "Foo Bar",
        "createdWhen": datetime.datetime(2020, 1, 1, 12, 0, 0).isoformat(),
        "name": "Name 1",
        "date": {"label": "On christmas eve 1755", "sortDate": "1755-12-24"},
        "role": {"label": "Role 1", "uri": "https://example.com/roles/1"},
        "statementContent": "Statement Content 1",
        "statementType": {
            "label": "Statement Type 1",
            "uri": "https://example.com/stmttypes/1",
        },
        "memberOf": {"label": "Member of 1", "uri": "https://example.com/members/1"},
        "uris": [
            "https://example.com/statements/1",
            "https://example.com/statements/2",
        ],
        "relatesToPersons": [
            {"label": "RelPerson 1", "uri": "https://example.com/relpersons/1"},
            {"label": "RelPerson 2", "uri": "https://example.com/relpersons/2"},
        ],
        "places": [
            {"label": "Place 1", "uri": "http://eample.com/places/1"},
            {"label": "Place 2", "uri": "http://eample.com/places/2"},
        ],
    }
def test_update_new(mockcfg, mockstatement1):
    "Create new source via PUT"
    connector = statement.StatementConnector(mockcfg)
    rdata = connector.update("Foo99", mockstatement1)
    for key in mockstatement1:
        assert rdata[key] == mockstatement1[key], "Uxexpected value for key {}".format(
            key
        )


def test_update_update(mockcfg, mockstatement1):
    "Test updating an existing person"
    # create entry
    connector = statement.StatementConnector(mockcfg)
    connector.update("Foo99", mockstatement1)

    mockstatement1["name"] = "Name 1a"
    mockstatement1["date"] = {
        "label": "On christmas eve 1855",
        "sortDate": "1855-12-24",
    }
    mockstatement1["role"] = {"label": "Role 1a", "uri": "https://example.com/roles/1a"}
    mockstatement1["statementContent"] = "Statement Content 1a"
    mockstatement1["statementType"] = {
        "label": "Statement Type 1a",
        "uri": "https://example.com/stmttypes/1a",
    }
    mockstatement1["memberOf"] = {
        "label": "Member of 1a",
        "uri": "https://example.com/members/1a",
    }
    mockstatement1["relatesToPersons"] = [
        {"label": "RelPerson 1a", "uri": "https://example.com/relpersons/1a"},
        {"label": "RelPerson 2a", "uri": "https://example.com/relpersons/2a"},
    ]
    mockstatement1["places"] = [
        {"label": "Place 1a", "uri": "http://eample.com/places/1a"},
        {"label": "Place 2a", "uri": "http://eample.com/places/2a"},
    ]
    mockstatement1["uris"] = [
        "https://example.com/statements/1a",
        "https://example.com/statements/2a",
    ]

    # update entry
    rdata = connector.update("Foo99", copy.deepcopy(mockstatement1))

    for key in mockstatement1:
        assert rdata[key] == mockstatement1[key], "Uxexpected value for key {}".format(
            key
        )


def test_create(mockcfg, mockstatement1):
    "Test the save() method."
    connector = statement.StatementConnector(mockcfg)
    rdata = connector.create(mockstatement1)

    for key in mockstatement1:
        assert rdata[key] == mockstatement1[key], "Uxexpected value for key {}".format(
            key
        )


def test_delete(mockcfg, mockstatement1):
    "Test the delete method."
    connector = statement.StatementConnector(mockcfg)
    # TODO: find a better way (without create)
    connector.create(mockstatement1)
    rdata = connector.get(mockstatement1["@id"])
    assert rdata
    connector.delete(mockstatement1["@id"])
    rdata = connector.get(mockstatement1["@id"])
    assert rdata is None


def test_delete_non_existing_object(mockcfg):
    "Calling delete() on a non exisiting object should cause an exception."
    connector = statement.StatementConnector(mockcfg)
    with pytest.raises(orm.ObjectNotFound):
        connector.delete("foobarfoo")

