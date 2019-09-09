"""System tests for statements.
"""
# pylint: disable=unused-argument
import requests


def test_get_id(mockserver, statementsurl):
    "Test if server returns the requested statement."
    response = requests.get(statementsurl + '/F4S1')
    assert response.ok
    assert response.json()['@id'] == 'F4S1'

def test_protocol(mockserver, statementsurl):
    "Test the returned 'protocol' data"
    response = requests.get(statementsurl)
    assert response.ok
    data = response.json()
    assert data["protocol"]["page"] == 1
    assert data["protocol"]["size"] == 30
    assert data["protocol"]["totalHits"] == 100


def test_pagination(mockserver, statementsurl):
    "Test if pagination of statements works as expected."
    response = requests.get(statementsurl + "?page=1&size=6")
    assert response.ok
    data = response.json()
    assert data["protocol"]["page"] == 1
    assert data["statements"][0]["@id"] == "F1S1"
    assert len(data["statements"]) == 6

    response = requests.get(statementsurl + "?page=2&size=6")
    data = response.json()
    assert response.ok
    assert data["protocol"]["page"] == 2
    assert data["statements"][0]["@id"] == "F7S1"
    assert len(data["statements"]) == 6


def test_no_more_pages(mockserver, statementsurl):
    "If no results or no more results are found, server must return 404"
    response = requests.get(statementsurl + "?page=20")
    assert response.status_code == 404
    assert response.json()["detail"] == "No (more) results found."

    response = requests.get(statementsurl + "?sourceId=xxx")
    assert response.status_code == 404
    assert response.json()["detail"] == "No (more) results found."


def test_size(mockserver, statementsurl):
    "Size controls the number of persons returned"
    respnse = requests.get(statementsurl + "?size=3")
    assert respnse.ok
    assert len(respnse.json()["statements"]) == 3

    respnse = requests.get(statementsurl + "?size=14")
    assert respnse.ok
    assert len(respnse.json()["statements"]) == 14


def test_max_size(mockserver, statementsurl):
    "Value of size= must not be greater than max_size."
    url = statementsurl + "?size=500"
    response = requests.get(url)
    assert response.status_code == 400
    assert response.json()["detail"] == "Value of parameter size= must not be greater than 200"


def test_filter(mockserver, statementsurl):
    """Some minimal filter tests.

    Diltering in tested in the connectpr object.
    """
    response = requests.get(statementsurl + "?sourceId=Source+002")
    assert response.ok
    assert len(response.json()["statements"]) == 4

    # Search for personId must match the full id
    response = requests.get(statementsurl + "?sourceId=Source")
    assert response.status_code == 404

    response = requests.get(statementsurl + "?sourceId=Source+002&personId=Person+002")
    assert response.ok
    assert len(response.json()["statements"]) == 2


def test_filter_without_result(mockserver, statementsurl):
    "Search for a non existing factoid."
    response = requests.get(statementsurl + "?sourceId=Source+X")
    assert response.status_code == 404
