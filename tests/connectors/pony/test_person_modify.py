"""Test create(), update() and delete() for papilotte.connectors.pony.person.
"""
import copy
import datetime

import pytest

from pony import orm

from papilotte.connectors.pony import person


@pytest.fixture
def mockperson1():
    "Return a single Person as mock dict."
    return {
        "@id": "Foo99",
        "createdBy": "Foo Bar",
        "createdWhen": datetime.datetime(2020, 1, 1, 12, 0, 0).isoformat(),
        "uris": ["https://example.com/persons/1", "https://example.com/persons/2"],
    }


def test_update_new(mockcfg, mockperson1):
    "Create new person via PUT"
    connector = person.PersonConnector(mockcfg)
    rdata = connector.update("Foo99", mockperson1)
    assert rdata["@id"] == "Foo99"
    assert rdata["createdBy"] == "Foo Bar"
    assert rdata["createdWhen"] == mockperson1["createdWhen"]
    assert rdata["modifiedWhen"] == ""
    assert rdata["modifiedBy"] == ""
    assert rdata["uris"] == [
        "https://example.com/persons/1",
        "https://example.com/persons/2",
    ]


def test_update_update(mockcfg, mockperson1):
    "Test updating an existing person"
    # create entry
    connector = person.PersonConnector(mockcfg)
    connector.update("Foo99", mockperson1)
    mockperson1["createdBy"] = "Bar Foo"
    mockperson1["modifiedBy"] = "Foo Bar"
    mockperson1["modifiedWhen"] = datetime.datetime(2021, 1, 2, 12, 0, 0).isoformat()
    mockperson1["uris"] = ["https://example.com/persons/1a", "https://example.com/persons/2a"]

    # update entry
    rdata = connector.update("Foo99", copy.deepcopy(mockperson1))
    assert rdata["@id"] == "Foo99"
    assert rdata["createdBy"] == mockperson1["createdBy"]
    assert rdata["createdWhen"] == mockperson1["createdWhen"]
    assert rdata["modifiedBy"] == mockperson1["modifiedBy"]
    assert rdata["modifiedWhen"] == mockperson1["modifiedWhen"]
    assert rdata["uris"] == mockperson1["uris"]


def test_create(mockcfg, mockperson1):
    "Test the save() method."
    connector = person.PersonConnector(mockcfg)
    rdata = connector.create(mockperson1)
    assert rdata["@id"]
    assert rdata["createdBy"] == mockperson1["createdBy"]
    assert rdata["createdWhen"] == mockperson1["createdWhen"]
    assert rdata["uris"] == mockperson1["uris"]


def test_delete(mockcfg, mockperson1):
    "Test the delete method."
    connector = person.PersonConnector(mockcfg)
    # TODO: find a better way (without create)
    connector.create(mockperson1)
    rdata = connector.get(mockperson1["@id"])
    assert rdata
    connector.delete(mockperson1["@id"])
    rdata = connector.get(mockperson1["@id"])
    assert rdata is None


def test_delete_non_existing_object(mockcfg):
    "Calling delete() on a non exisiting object should cause an exception."
    connector = person.PersonConnector(mockcfg)
    with pytest.raises(orm.ObjectNotFound):
        connector.delete("foobarfoo")

