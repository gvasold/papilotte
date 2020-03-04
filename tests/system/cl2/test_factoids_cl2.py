import copy

import pytest
from flask import current_app as app
from pony import orm

from papilotte.api import factoids

TEST_URL = '/api/factoids'

mock_ipif = {
    '@id': '1',
    'createdBy': 'c1',
    'createdWhen': '2015-05-04T12:13:14',
    'source': {'@id': 'source1'},
    'person': {'@id': 'person1'},
    'statement': {'@id': 'statement 1'}
}

def test_update(mockclient_cl2, factoid1):
    "Update an existing factoid."
    newdata = {}

    newdata["@id"] = "2"  # on purpose wrong id should be removed automatically
    newdata["createdBy"] = "Foo"
    newdata["createdWhen"] = "2017-05-05T13:14:15"
    newdata["modifiedBy"] = "Bar"
    newdata["modifiedWhen"] = "2017-05-06T13:14:15"
    newdata['source'] = {'@id': 'ssss'}
    newdata['person'] = {'@id': 'pppp'}
    newdata['statement'] = {'@id': 'ststst'}
    r = mockclient_cl2.put(TEST_URL + "/1", json=newdata)
    assert r.status_code == 200

    data = r.json
    assert data["@id"] == "1"
    assert data["createdBy"] == "Foo"
    assert data["createdWhen"] == "2017-05-05T13:14:15"
    assert data["modifiedBy"] == "Bar"
    assert data["modifiedWhen"] == "2017-05-06T13:14:15"
    assert data['source']['@id'] == 'ssss'
    assert data['person']['@id'] == 'pppp'
    assert data['statements'][0]['@id'] == 'ststst'


# TODO: disabled as this is not yet part of the spec
def _test_update_with_invalid_id(mockclient_cl2, factoid1):
    "Only specific chars are allowed as id."
    r = mockclient_cl2.put(TEST_URL + "/1f$oo(2", json=factoid1)
    assert r.status_code == 400


# TODO: test cor compliance level0 und 1, which both must fail for update


def test_no_modify_for_cl1(mockclient_cl1, factoid1):
    "Data modifying requests are not allowed in compliance level 1."
    # creation via POST
    r = mockclient_cl1.post(TEST_URL, json=mock_ipif)
    assert r.status_code == 501
    # creation via put
    r = mockclient_cl1.put(TEST_URL + "/foo", json=mock_ipif)
    assert r.status_code == 501
    # delete
    r = mockclient_cl1.delete(TEST_URL + "/foo")
    assert r.status_code == 501


def test_no_modify_for_cl0(mockclient_cl0):
    "Data modifying requests are not allowed in compliance level 0."
    # creation via POST
    r = mockclient_cl0.post(TEST_URL, json=mock_ipif)
    assert r.status_code == 501
    # creation via put
    r = mockclient_cl0.put(TEST_URL + "/foo", json=mock_ipif)
    assert r.status_code == 501
    # delete
    r = mockclient_cl0.delete(TEST_URL + "/foo")
    assert r.status_code == 501


def test_create_factoid(mockclient_cl2):
    "Test creatio of a factoid."
    factoid1 = copy.deepcopy(mock_ipif)
    factoid1["@id"] = "1001"
    r = mockclient_cl2.post(TEST_URL, json=factoid1)
    assert r.status_code == 200
    assert r.json["@id"] == "1001"

    # Creating the same factoid is not allowed
    r = mockclient_cl2.post(TEST_URL, json=factoid1)
    assert r.status_code == 409
    assert "already exists" in r.json["detail"]


# TODO: disabled as this is not yet part of the spec
def _test_create_factoid_with_invalid_id(mockclient_cl2):
    "Only specific chars are allowed as id."
    r = mockclient_cl2.put(TEST_URL + "/1foo(2", json={"@id": "[$a"})
    assert r.status_code == 400


def test_delete_factoid(mockclient_cl2): 
    "Delete a factoid."
    # deleting a factoid requires that it is not used in any factoid,
    # which actually should be impossible. But nevertheless we create a
    # solitaire factoid to test deletion purpose
    r = mockclient_cl2.delete(TEST_URL + '/F00009')
    assert r.status_code == 200
