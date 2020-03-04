"""Tests for papilotte.connectors.pony.factoid
"""
import copy
import datetime

import pytest

from pony import orm

from papilotte.connectors.pony import factoid


@pytest.fixture
def mockfactoid1():
    "Return a single Factoid as mock dict."
    return {
        "@id": "Foo99",
        "createdBy": "Foo Bar",
        "createdWhen": datetime.datetime(2020, 1, 1, 12, 0, 0).isoformat(),
        "source": {'@id': 'Source 1'},
        "person": {'@id': 'Person 1'},
        "statements": [{'@id': 'Statement 1'}],
    }

def test_update_new(mockcfg, mockfactoid1):
    "Create new factoid via PUT"
    connector = factoid.FactoidConnector(mockcfg)
    rdata = connector.update("Foo99", mockfactoid1)
    assert rdata["@id"] == "Foo99"
    assert rdata["createdBy"] == "Foo Bar"
    assert rdata["createdWhen"] == mockfactoid1["createdWhen"]
    assert rdata["modifiedWhen"] == ""
    assert rdata["modifiedBy"] == ""
    assert rdata["person"]["@id"] == "Person 1"
    assert rdata["source"]["@id"] == "Source 1"
    assert rdata["statements"][0]["@id"] == "Statement 1"


def test_update_update(mockcfg, mockfactoid1):
    "Test updating an existing person"
    # create entry
    connector = factoid.FactoidConnector(mockcfg)
    connector.update("Foo99", mockfactoid1)
    mockfactoid1["createdBy"] = "Bar Foo"
    mockfactoid1["modifiedBy"] = "Foo Bar"
    mockfactoid1["modifiedWhen"] = datetime.datetime(2021, 1, 2, 12, 0, 0).isoformat()
    mockfactoid1["person"] = {"@id": "Person 1a"}
    mockfactoid1["source"] = {"@id": "Source 1a"}
    mockfactoid1["statements"] = [{"@id": "Statement 1a"}]

    # update entry
    rdata = connector.update("Foo99", copy.deepcopy(mockfactoid1))

    assert rdata["@id"] == "Foo99"
    assert rdata["createdBy"] == mockfactoid1["createdBy"]
    assert rdata["createdWhen"] == mockfactoid1["createdWhen"]
    assert rdata["modifiedBy"] == mockfactoid1["modifiedBy"]
    assert rdata["modifiedWhen"] == mockfactoid1["modifiedWhen"]
    assert rdata['person']['@id'] == mockfactoid1["person"]["@id"]
    assert rdata['source']['@id'] == mockfactoid1["source"]["@id"]
    assert rdata['statements'][0]['@id'] == mockfactoid1["statements"][0]["@id"]


def test_create(mockcfg, mockfactoid1):
    "Test the save() method."
    connector = factoid.FactoidConnector(mockcfg)
    rdata = connector.create(mockfactoid1)
    assert rdata["@id"]
    assert rdata["createdBy"] == mockfactoid1["createdBy"]
    assert rdata["createdWhen"] == mockfactoid1["createdWhen"]
    assert rdata['person']['@id'] == mockfactoid1["person"]["@id"]
    assert rdata['source']['@id'] == mockfactoid1["source"]["@id"]
    assert rdata['statements'][0]['@id'] == mockfactoid1["statements"][0]["@id"]


def test_delete(mockcfg, mockfactoid1):
    "Test the delete method."
    connector = factoid.FactoidConnector(mockcfg)
    # TODO: find a better way (without create)
    connector.create(mockfactoid1)
    rdata = connector.get(mockfactoid1["@id"])
    assert rdata
    connector.delete(mockfactoid1["@id"])
    rdata = connector.get(mockfactoid1["@id"])
    assert rdata is None


def test_delete_non_existing_object(mockcfg):
    "Calling delete() on a non existing object should cause an exception."
    connector = factoid.FactoidConnector(mockcfg)
    with pytest.raises(orm.ObjectNotFound):
        connector.delete("foobarfoo")