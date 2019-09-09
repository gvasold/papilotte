"""System tests for sources.
"""
# pylint: disable=unused-argument
import requests


def test_get_id(mockserver, sourcesurl):
    "Test if the server returns the requested source."
    response = requests.get(sourcesurl + '/Source%20004')
    assert response.ok
    assert response.json()['@id'] == 'Source 004'

def test_protocol(mockserver, sourcesurl):
    "Test the returned 'protocol' data"
    response = requests.get(sourcesurl)
    assert response.ok
    data = response.json()
    assert data["protocol"]["page"] == 1
    assert data["protocol"]["size"] == 30
    assert data["protocol"]["totalHits"] == 25


def test_pagination(mockserver, sourcesurl):
    "Test if pagination of sources works as expected."
    response = requests.get(sourcesurl + "?page=1&size=6")
    assert response.ok
    data = response.json()
    assert data["protocol"]["page"] == 1
    assert data["sources"][0]["@id"] == "Source 001"
    assert len(data["sources"]) == 6

    response = requests.get(sourcesurl + "?page=2&size=6")
    data = response.json()
    assert response.ok
    assert data["protocol"]["page"] == 2
    assert data["sources"][0]["@id"] == "Source 007"
    assert len(data["sources"]) == 6


def test_no_more_pages(mockserver, sourcesurl):
    "If no results or no more results are found, server must return 404"
    response = requests.get(sourcesurl + "?page=20")
    assert response.status_code == 404
    assert response.json()["detail"] == "No (more) results found."

    response = requests.get(sourcesurl + "?personId=xxx")
    assert response.status_code == 404
    assert response.json()["detail"] == "No (more) results found."


def test_size(mockserver, sourcesurl):
    "Size controls the number of persons returned"
    response = requests.get(sourcesurl + "?size=3")
    assert response.ok
    assert len(response.json()["sources"]) == 3

    response = requests.get(sourcesurl + "?size=14")
    assert response.ok
    assert len(response.json()["sources"]) == 14


def test_max_size(mockserver, sourcesurl):
    "Value of size= must not be greater than max_size."
    url = sourcesurl + "?size=500"
    response = requests.get(url)
    assert response.status_code == 400
    assert response.json()["detail"] == "Value of parameter size= must not be greater than 200"


def test_filter(mockserver, sourcesurl):
    """Some minimal filter tests.

    Diltering in tested in the connectpr object.
    """
    response = requests.get(sourcesurl + "?personId=Person+002")
    assert response.ok
    assert len(response.json()["sources"]) == 5

    # Search for personId must match the full id
    response = requests.get(sourcesurl + "?personId=Person")
    assert response.status_code == 404

    response = requests.get(sourcesurl + "?personId=Person+002&st=Statement+content+3")
    assert response.ok
    assert len(response.json()["sources"]) == 1


def test_filter_without_result(mockserver, sourcesurl):
    "Search for a non existing factoid."
    response = requests.get(sourcesurl + "?personId=Person+X")
    assert response.status_code == 404
