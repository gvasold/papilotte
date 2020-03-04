import copy

import pytest
from flask import current_app as app
from pony import orm

from papilotte.api import sources

### Test the get methods

TEST_URL =  '/api/sources'

def test_get_by_id_missing(mockclient_cl0):
    "Request a non existing object."
    response = mockclient_cl0.get(TEST_URL + "/foo1234bar")
    assert response.status_code == 404


def test_get_by_id(mockclient_cl0, source1):
    "Test if source is returned as expected."
    response = mockclient_cl0.get(TEST_URL + "/S00001")
    assert response.status_code == 200
    data = response.json

    assert data["@id"] == source1['@id']
    assert data["createdBy"] == source1["createdBy"]
    assert data["createdWhen"] == source1["createdWhen"]
    assert data["modifiedBy"] == source1["modifiedBy"]
    assert data["modifiedWhen"] == source1["modifiedWhen"]
    assert data["uris"] == source1["uris"]
    assert data["label"] == source1["label"]

    refs = data["factoid-refs"]
    assert len(refs) == 2
    assert refs[0]['@id'] == 'F00100'
    assert refs[0]['source-ref']['@id'] == 'S00001'
    assert refs[0]['statement-refs'][0]['@id'] == 'Stmt00300'

    assert refs[1]['@id'] == 'F00200'
    assert refs[1]['source-ref']['@id'] == 'S00001'
    assert refs[1]['statement-refs'][0]['@id'] == 'Stmt00600'

def test_get_invalid_filter(mockclient_cl0):
    """Each comliance level has a set of allowed filters.
    Test 's' which is not allowed with cl0
    """
    r = mockclient_cl0.get(TEST_URL + "?s=foo")
    assert r.status_code == 400


def test_protocol(mockclient_cl0):
    "Test the returned 'protocol' data"
    r = mockclient_cl0.get(TEST_URL)
    assert r.status_code == 200
    data = r.json
    assert data["protocol"]["page"] == 1
    assert data["protocol"]["size"] == 30
    assert data["protocol"]["totalHits"] == 100