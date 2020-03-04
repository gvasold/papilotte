import copy

import pytest
from flask import current_app as app
from pony import orm

from papilotte.api import statements

### Test the get methods

TEST_URL =  '/api/statements'


def test_get_by_id_missing(mockclient_cl0):
    "Request a non existing object."
    response = mockclient_cl0.get(TEST_URL + "/foo1234bar")
    assert response.status_code == 404


def test_get_by_id(mockclient_cl0, statement1):
    "Test if statement is returned as expected."
    response = mockclient_cl0.get(TEST_URL + "/Stmt00001")
    assert response.status_code == 200
    data = response.json

    assert data["@id"] == statement1['@id']
    assert data["createdBy"] == statement1["createdBy"]
    assert data["createdWhen"] == statement1["createdWhen"]
    assert data["uris"] == statement1["uris"]
    assert data['name'] == statement1['name'] 
    assert data['date'] == statement1["date"]
    assert data['memberOf'] == statement1["memberOf"]
    assert data['places'] == statement1["places"]
    assert data['role'] == statement1["role"]
    assert data['statementContent'] == statement1["statementContent"]
    assert data['statementType'] == statement1["statementType"]

    refs = data["factoid-refs"]
    assert len(refs) == 1
    assert refs[0]['@id'] == 'F00001'
    assert refs[0]['source-ref']['@id'] == 'S00002'
    assert refs[0]['statement-refs'][0]['@id'] == 'Stmt00001'


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
    assert data["protocol"]["totalHits"] == 600