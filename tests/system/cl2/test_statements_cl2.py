import copy

import pytest
from flask import current_app as app
from pony import orm

from papilotte.api import statements

TEST_URL = '/api/statements'


def test_update(mockclient_cl2, statement1):
    "Update an existing statement."
    newdata = {}

    newdata["@id"] = "2"  # on purpose wrong id should be removed automatically
    newdata["createdBy"] = "Foo"
    newdata["createdWhen"] = "2017-05-05T13:14:15"
    newdata["modifiedBy"] = "Bar"
    newdata["modifiedWhen"] = "2017-05-06T13:14:15"
    newdata["uris"] = ["https://example.com/statements/1a", "https://example.com/statements/2a"]
    r = mockclient_cl2.put(TEST_URL + "/1", json=newdata)
    # statements only allowes get requests
    assert r.status_code == 405
    # data = r.json
    # assert data["@id"] == "1"
    # assert data["createdBy"] == "Foo"
    # assert data["createdWhen"] == "2017-05-05T13:14:15"
    # assert data["modifiedBy"] == "Bar"
    # assert data["modifiedWhen"] == "2017-05-06T13:14:15"
    # assert data["uris"] == newdata["uris"]



def test_no_modify_for_cl1(mockclient_cl1):
    "Data modifying requests are not allowed in compliance level 1."
    # creation via POST
    r = mockclient_cl1.post(TEST_URL, json={"@id": "xxx"})

    # statements only allowes get requests
    assert r.status_code == 405
    # assert r.status_code == 501
    # creation via put
    r = mockclient_cl1.put(TEST_URL + "/foo", json={"@id": "xxx"})
    # statements only allowes get requests
    assert r.status_code == 405
    # assert r.status_code == 501
    # delete
    # statements only allowes get requests
    assert r.status_code == 405
    r = mockclient_cl1.delete(TEST_URL + "/foo")
    # statements only allowes get requests
    assert r.status_code == 405
    # assert r.status_code == 501

