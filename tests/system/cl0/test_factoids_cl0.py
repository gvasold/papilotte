import copy

import pytest
from flask import current_app as app
from pony import orm

from papilotte.api import factoids


TEST_URL =  '/api/factoids'


def test_get_by_id_missing(mockclient_cl0):
    "Request a non existing object."
    response = mockclient_cl0.get(TEST_URL + "/foo1234bar")
    assert response.status_code == 404


def test_get_by_id(mockclient_cl0, factoid1):
    "Test if source is returned as expected."
    response = mockclient_cl0.get(TEST_URL + "/F00001")
    assert response.status_code == 200
    data = response.json
    assert data["@id"] == factoid1['@id']
    assert data["createdBy"] == factoid1["createdBy"]
    assert data["createdWhen"] == factoid1["createdWhen"]

    assert data['source-ref']['@id'] == 'S00002'
    assert data['person-ref']['@id'] == 'P00002'
    assert data['statement-refs'][0]['@id'] == 'Stmt00001'


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
    assert data["protocol"]["totalHits"] == 200