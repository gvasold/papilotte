import copy

import pytest
from flask import current_app as app
from pony import orm

from papilotte.api import persons

TEST_URL = '/api/persons'


def test_get_person_by_id_missing(mockclient_cl0):
    "Request a non existing person"
    response = mockclient_cl0.get(TEST_URL + "/foo1234bar")
    assert response.status_code == 404


def test_get_person_by_id(mockclient_cl0, person1):
    "Test if person is returned as expected."
    response = mockclient_cl0.get(TEST_URL + "/P00001")
    assert response.status_code == 200
    data = response.json
    assert data["@id"] == "P00001"
    assert data["createdBy"] == person1["createdBy"]
    assert data["createdWhen"] == person1["createdWhen"]
    assert data["modifiedBy"] == person1["modifiedBy"]
    assert data["modifiedWhen"] == person1["modifiedWhen"]
    assert data["uris"] == person1["uris"]

    refs = data["factoid-refs"]
    assert len(refs) == 2
    assert refs[0]['@id'] == 'F00075'
    assert refs[0]['source-ref']['@id'] == 'S00076'
    assert refs[0]['statement-refs'][0]['@id'] == 'Stmt00225'

    assert refs[1]['@id'] == 'F00150'
    assert refs[1]['source-ref']['@id'] == 'S00051'
    assert refs[1]['statement-refs'][0]['@id'] == 'Stmt00450'

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
    assert data["protocol"]["totalHits"] == 75