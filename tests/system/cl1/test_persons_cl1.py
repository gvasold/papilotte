import copy

import pytest
from flask import current_app as app
from pony import orm

from papilotte.api import persons

TEST_URL = '/api/persons'

### Test the get methods


def test_get_person_valid_size(mockclient_cl1):
    "Using a valid size must lead to status code 200."
    r = mockclient_cl1.get(TEST_URL + "?size=20")
    assert r.status_code == 200


def test_get_person_invalid_size(mockclient_cl1):
    "Using a size > maxSize must lead to status code 400."
    r = mockclient_cl1.get(TEST_URL + "?size=99999")
    assert r.status_code == 400
    assert "size= must not be greater than" in r.json["detail"]


def test_get_invalid_filter(mockclient_cl1):
    """Each comliance level has a set of allowed filters.
    Test 's' which is not allowed with cl0
    """
    r = mockclient_cl1.get(TEST_URL + "?personId=foo")
    assert r.status_code == 400


def test_get_valid_filter(mockclient_cl1):
    """Each comliance level has a set of allowed filters.
    Test 's' which is not allowed with cl0 but ok for cl1
    """
    r = mockclient_cl1.get(TEST_URL + "?p=1")
    assert r.status_code == 200


def test_get_pagination(mockclient_cl1):
    """Test parameters page and size.
    """
    # There should be 30 Person in testset.
    r = mockclient_cl1.get(TEST_URL + "?size=100")
    assert r.status_code == 200
    assert len(r.json["persons"]) == 75

    # Get the first 50
    r = mockclient_cl1.get(TEST_URL + "?size=50")
    assert r.status_code == 200
    assert len(r.json["persons"]) == 50

    # Get the remaining 25
    r = mockclient_cl1.get(TEST_URL + "?size=50&page=2")
    assert r.status_code == 200
    assert len(r.json["persons"]) == 25


def test_get_valid_sort_by(mockclient_cl1):
    "Try out a valid value for sortBy"
    r = mockclient_cl1.get(TEST_URL + "?sortBy=createdBy")
    assert r.status_code == 200


def test_get_invalid_sort_by(mockclient_cl1):
    "Test an invald Value for sortBy."
    r = mockclient_cl1.get(TEST_URL + "?sortBy=name")
    assert r.status_code == 400
    assert "sortBy= is not allowed" in r.json["detail"]


def test_get_sortby(mockclient_cl1):
    "Test the sortBy parameter"
    for fieldname in persons.ALLOWED_SORT_BY_VALUES:
        if fieldname == "id":
            real_fieldname = "@id"
        else:
            real_fieldname = fieldname

        # sort order without suffix must be the same as result of a python sort
        r = mockclient_cl1.get(TEST_URL + "?sortBy={}".format(fieldname))
        assert r.status_code == 200
        fields = [p[real_fieldname] for p in r.json["persons"]]
        assert fields == sorted(fields), "unexpected sort order for {}".format(
            fieldname
        )

        # sort order with suffix 'ASC' must be the same as result of a python sort
        r = mockclient_cl1.get(TEST_URL + "?sortBy={}".format(fieldname + "ASC"))
        assert r.status_code == 200
        fields = [p[real_fieldname] for p in r.json["persons"]]
        assert fields == sorted(fields), "unexpected sort order for {}".format(
            fieldname
        )

        # sort order with suffix 'DESC' must be the same as reversed result of a python sort
        r = mockclient_cl1.get(TEST_URL + "?sortBy={}".format(fieldname + "DESC"))
        assert r.status_code == 200
        fields = [p[real_fieldname] for p in r.json["persons"]]


def test_get_with_no_filters(mockclient_cl1):
    """Test get without filters"""
    r = mockclient_cl1.get(TEST_URL + "?size=100")
    assert r.status_code == 200
    assert len(r.json["persons"]) == 75


def test_get_with_filter_person(mockclient_cl1):
    """Test some of the filters operating on person."""
    r = mockclient_cl1.get(TEST_URL + "?size=100&p=P00063")
    assert r.status_code == 200
    assert len(r.json["persons"]) == 1


def test_get_with_filter_factoid(mockclient_cl1):
    """Test some of the filters operating on factoid."""
    r = mockclient_cl1.get(TEST_URL + "?size=100&f=F00062")
    assert r.status_code == 200
    assert len(r.json["persons"]) == 1


def test_get_with_filter_person_factoid(mockclient_cl1):
    """Test some of the filters operating on factoid and person."""
    r = mockclient_cl1.get(TEST_URL + "?size=100&f=F00062&p=P00063")
    assert r.status_code == 200
    assert r.json["persons"][0]["@id"] == "P00063"
    r = mockclient_cl1.get("/api/persons?size=100&f=F00062&p=P00064")
    assert r.status_code == 404


def test_get_with_filter_source(mockclient_cl1):
    """Test some of the filters operating on source."""
    r = mockclient_cl1.get(TEST_URL + "?size=100&s=S00063")
    assert r.status_code == 200
    assert len(r.json["persons"]) == 2


def test_get_with_filter_person_source(mockclient_cl1):
    """Test some of the filters operating on factoid and source."""
    r = mockclient_cl1.get(TEST_URL + "?size=100&s=S00063&p=P00063")
    assert r.status_code == 200
    assert r.json["persons"][0]["@id"] == "P00063"
    r = mockclient_cl1.get(TEST_URL + "?size=100&s=S00036&p=P00064")
    assert r.status_code == 404


def test_get_with_filter_statement(mockclient_cl1):
    """Test some of the filters operating on source."""
    r = mockclient_cl1.get(TEST_URL + "?size=100&st=Stmt00062")
    assert r.status_code == 200
    assert len(r.json["persons"]) == 1


def test_get_with_filter_person_statement(mockclient_cl1):
    """Test some of the filters operating on factoid and source."""
    r = mockclient_cl1.get("/api/persons?size=100&st=Stmt00183&p=P00063")
    assert r.status_code == 200
    assert r.json["persons"][0]["@id"] == "P00063"
    r = mockclient_cl1.get(TEST_URL + "?size=100&st=Stmt00055&p=P00064")
    assert r.status_code == 404