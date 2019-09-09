"""System tests for the factoids.
"""
import requests


def test_get_id(mockserver, factoidsurl):
    "Test if server returns the requested factoid."
    # pylint: disable=unused-argument
    response = requests.get(factoidsurl + '/Factoid%20032')
    assert response.ok
    assert response.json()['@id'] == 'Factoid 032'

def test_protocol(mockserver, factoidsurl):
    "Test the returned 'protocol' data"
    # pylint: disable=unused-argument
    response = requests.get(factoidsurl)
    assert response.ok
    data = response.json()
    assert data["protocol"]["page"] == 1
    assert data["protocol"]["size"] == 30
    assert data["protocol"]["totalHits"] == 100


def test_pagination(mockserver, factoidsurl):
    "Test if pagination of factoids works as expected."
    # pylint: disable=unused-argument
    response = requests.get(factoidsurl + "?page=1")
    assert response.ok
    data = response.json()
    assert data["protocol"]["page"] == 1
    assert data["factoids"][0]["@id"] == "Factoid 001"
    assert len(data["factoids"]) == 30

    response = requests.get(factoidsurl + "?page=2")
    data = response.json()
    assert response.ok
    assert data["protocol"]["page"] == 2
    assert data["factoids"][0]["@id"] == "Factoid 031"
    assert len(data["factoids"]) == 30


def test_no_more_pages(mockserver, factoidsurl):
    "If no results or no more results are found, server must return 404"
    # pylint: disable=unused-argument
    rsponse = requests.get(factoidsurl + "?page=20")
    assert rsponse.status_code == 404
    assert rsponse.json()["detail"] == "No (more) results found."

    rsponse = requests.get(factoidsurl + "?personId=xxx")
    assert rsponse.status_code == 404
    assert rsponse.json()["detail"] == "No (more) results found."


def _test_sort_order(mockserver, factoidsurl):
    # TODO
    # pylint: disable=unused-argument
    response = requests.get(factoidsurl)
    assert response.ok
    data = response.json()
    assert data["factoids"][0]["@id"] == "Factoid 1"

def __test_sortorder_value_validation(mockserver, factoidsurl):
    "Test if validation of allowed values for sortBy."
    # TODO: deactivated validation. Needs more dicussion
    # pylint: disable=unused-argument
    response = requests.get(factoidsurl + '?sortBy=id')
    response = requests.get(factoidsurl + '?sortBy=createdWhen')
    assert response.ok
    response = requests.get(factoidsurl + '?sortBy=createdBy')
    assert response.ok
    assert response.ok
    response = requests.get(factoidsurl + '?sortBy=modifiedWhen')
    assert response.ok
    response = requests.get(factoidsurl + '?sortBy=modifiedBy')
    assert response.ok

    response = requests.get(factoidsurl + '?sortBy=xxx')
    assert response.status_code == 400
    assert 'sortBy is not allowed' in response.json()['detail']


def test_size(mockserver, factoidsurl):
    "Size controls the number of factoids returned"
    # pylint: disable=unused-argument
    response = requests.get(factoidsurl + "?size=3")
    assert response.ok
    assert len(response.json()["factoids"]) == 3

    response = requests.get(factoidsurl + "?size=50")
    assert response.ok
    assert len(response.json()["factoids"]) == 50


def test_max_size(mockserver, factoidsurl):
    "Value of size= must not be greater than max_size."
    # pylint: disable=unused-argument
    url = factoidsurl + "?size=500"
    response = requests.get(url)
    assert response.status_code == 400
    assert response.json()["detail"] == "Value of parameter size= must not be greater than 200"


def test_filter(mockserver, factoidsurl):
    """Some minimal filter tests.

    Diltering in tested in the connectpr object.
    """
    # pylint: disable=unused-argument

    response = requests.get(factoidsurl + "?personId=Person+002")
    assert response.ok
    assert len(response.json()["factoids"]) == 7

    # Search for personId must match the full id
    response = requests.get(factoidsurl + "?personId=Person")
    assert response.status_code == 404

    response = requests.get(factoidsurl + "?personId=Person+002&st=Statement content 3")
    # print(r.json())
    assert response.ok
    assert len(response.json()["factoids"]) == 2


def test_filter_without_result(mockserver, factoidsurl):
    "Search for a non existing factoid."
    # pylint: disable=unused-argument
    response = requests.get(factoidsurl + "?personId=Person X")
    assert response.status_code == 404
