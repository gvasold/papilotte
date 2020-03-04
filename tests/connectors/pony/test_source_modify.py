"""Tests for papilotte.connectors.pony.source
"""
import copy
import datetime

import pytest

from pony import orm

from papilotte.connectors.pony import source


@pytest.fixture
def mocksource1():
    "Return a single Source as mock dict."
    return {
        "@id": "Foo99",
        "createdBy": "Foo Bar",
        "createdWhen": datetime.datetime(2020, 1, 1, 12, 0, 0).isoformat(),
        "uris": ["https://example.com/sources/1", "https://example.com/sources/2"],
        "label": "Label 1"
    }



def test_update_new(mockcfg, mocksource1):
    "Create new source via PUT"
    connector = source.SourceConnector(mockcfg)
    rdata = connector.update("Foo99", mocksource1)
    assert rdata["@id"] == "Foo99"
    assert rdata["createdBy"] == "Foo Bar"
    assert rdata["createdWhen"] == mocksource1["createdWhen"]
    assert rdata["modifiedWhen"] == ""
    assert rdata["modifiedBy"] == ""
    assert rdata["label"] == mocksource1['label']
    assert rdata["uris"] == [
        "https://example.com/sources/1",
        "https://example.com/sources/2",
    ]



def test_update_update(mockcfg, mocksource1):
    "Test updating an existing person"
    # create entry
    connector = source.SourceConnector(mockcfg)
    connector.update("Foo99", mocksource1)
    mocksource1["createdBy"] = "Bar Foo"
    mocksource1["modifiedBy"] = "Foo Bar"
    mocksource1["label"] = "Label 1a"
    mocksource1["modifiedWhen"] = datetime.datetime(2021, 1, 2, 12, 0, 0).isoformat()
    mocksource1["uris"] = ["https://example.com/persons/1a", "https://example.com/persons/2a"]

    # update entry
    rdata = connector.update("Foo99", copy.deepcopy(mocksource1))
    assert rdata["@id"] == "Foo99"
    assert rdata["createdBy"] == mocksource1["createdBy"]
    assert rdata["createdWhen"] == mocksource1["createdWhen"]
    assert rdata["modifiedBy"] == mocksource1["modifiedBy"]
    assert rdata["modifiedWhen"] == mocksource1["modifiedWhen"]
    assert rdata["label"] == mocksource1["label"]
    assert rdata["uris"] == mocksource1["uris"]



def test_create(mockcfg, mocksource1):
    "Test the save() method."
    connector = source.SourceConnector(mockcfg)
    rdata = connector.create(mocksource1)
    assert rdata["@id"]
    assert rdata["createdBy"] == mocksource1["createdBy"]
    assert rdata["createdWhen"] == mocksource1["createdWhen"]
    assert rdata["label"] == mocksource1["label"]
    assert rdata["uris"] == mocksource1["uris"]

def test_delete(mockcfg, mocksource1):
    "Test the delete method."
    connector = source.SourceConnector(mockcfg)
    # TODO: find a better way (without create)
    connector.create(mocksource1)
    rdata = connector.get(mocksource1["@id"])
    assert rdata
    connector.delete(mocksource1["@id"])
    rdata = connector.get(mocksource1["@id"])
    assert rdata is None


def test_delete_non_existing_object(mockcfg):
    "Calling delete() on a non exisiting object should cause an exception."
    connector = source.SourceConnector(mockcfg)
    with pytest.raises(orm.ObjectNotFound):
        connector.delete("foobarfoo")



