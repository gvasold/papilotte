import copy

import pytest
from flask import current_app as app
from pony import orm

from papilotte.api import sources
TEST_URL = '/api/sources'


def test_update(mockclient_cl2, source1):
    "Update an existing source."
    newdata = {}

    newdata["@id"] = "2"  # on purpose wrong id
    newdata["createdBy"] = "Foo"
    newdata["createdWhen"] = "2017-05-05T13:14:15"
    newdata["modifiedBy"] = "Bar"
    newdata["modifiedWhen"] = "2017-05-06T13:14:15"
    newdata["uris"] = ["https://example.com/sources/1a", "https://example.com/sources/2a"]
    r = mockclient_cl2.put(TEST_URL + "/1", json=newdata)
    assert r.status_code == 200
    data = r.json
    assert data["@id"] == "1"
    assert data["createdBy"] == "Foo"
    assert data["createdWhen"] == "2017-05-05T13:14:15"
    assert data["modifiedBy"] == "Bar"
    assert data["modifiedWhen"] == "2017-05-06T13:14:15"
    assert data["uris"] == newdata["uris"]


# TODO: disabled as this is not yet part of the spec
def _test_update_with_invalid_id(mockclient_cl2, source1):
    "Only specific chars are allowed as id."
    r = mockclient_cl2.put(TEST_URL + "/1f$oo(2", json=source1)
    assert r.status_code == 400


# TODO: test cor compliance level0 und 1, which both must fail for update


def test_no_modify_for_cl1(mockclient_cl1):
    "Data modifying requests are not allowed in compliance level 1."
    # creation via POST
    r = mockclient_cl1.post(TEST_URL, json={"@id": "xxx"})
    assert r.status_code == 501
    # creation via put
    r = mockclient_cl1.put(TEST_URL + "/foo", json={"@id": "xxx"})
    assert r.status_code == 501
    # delete
    r = mockclient_cl1.delete(TEST_URL + "/foo")
    assert r.status_code == 501


def test_no_modify_for_cl0(mockclient_cl0):
    "Data modifying requests are not allowed in compliance level 0."
    # creation via POST
    r = mockclient_cl0.post(TEST_URL, json={"@id": "xxx"})
    assert r.status_code == 501
    # creation via put
    r = mockclient_cl0.put(TEST_URL + "/foo", json={"@id": "xxx"})
    assert r.status_code == 501
    # delete
    r = mockclient_cl0.delete(TEST_URL + "/foo")
    assert r.status_code == 501


def test_create_source(mockclient_cl2, source1):
    "Test creatio of a source."
    source1["@id"] = "1001"
    r = mockclient_cl2.post(TEST_URL, json=source1)
    assert r.status_code == 200
    assert r.json["@id"] == "1001"

    # Creating the same source is not allowed
    r = mockclient_cl2.post(TEST_URL, json=source1)
    assert r.status_code == 409
    assert "already exists" in r.json["detail"]


# TODO: disabled as this is not yet part of the spec
def _test_create_source_with_invalid_id(mockclient_cl2):
    "Only specific chars are allowed as id."
    r = mockclient_cl2.put(TEST_URL + "/1foo(2", json={"@id": "[$a"})
    assert r.status_code == 400


def test_delete_source(mockclient_cl2): 
    "Delete a source."
    # deleting a source requires that it is not used in any factoid,
    # which actually should be impossible. But nevertheless we create a
    # solitaire source to test deletion purpose
    mockclient_cl2.put(TEST_URL + "/LonerSource", json={"@id": "LonerSource"})
    r = mockclient_cl2.delete(TEST_URL + "/LonerSource")
    assert r.status_code == 204

    ## Check if it is really gone
    r = mockclient_cl2.get(TEST_URL + "/LonerSource")
    assert r.status_code == 404

    # Try to delete a non existing source
    r = mockclient_cl2.delete(TEST_URL + "/Sxxxxxxx2")
    assert r.status_code == 404


def test_referential_integrity(mockclient_cl2, source1):
    """Deleting a Source, which is is referenced by factoids must lead to a 409.
    """
    r = mockclient_cl2.delete(TEST_URL + "/S00002")
    assert r.status_code == 409
    assert "at least one factoid" in r.json["detail"]
