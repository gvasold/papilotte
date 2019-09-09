"""System tests for persons.
"""
import requests
# pylint: disable=unused-argument


def test_get_id(mockserver, personsurl):
    "Test if server returns the requested person."
    response = requests.get(personsurl + '/Person%20004')
    assert response.ok
    assert response.json()['@id'] == 'Person 004'

def test_protocol(mockserver, personsurl):
    "Test the returned 'protocol' data"
    response = requests.get(personsurl)
    assert response.ok
    data = response.json()
    assert data["protocol"]["page"] == 1
    assert data["protocol"]["size"] == 30
    assert data["protocol"]["totalHits"] == 15


def test_pagination(mockserver, personsurl):
    "Test if pagination of persons works as expected."
    response = requests.get(personsurl + "?page=1&size=6")
    assert response.ok
    data = response.json()
    assert data["protocol"]["page"] == 1
    assert data["persons"][0]["@id"] == "Person 001"
    assert len(data["persons"]) == 6

    response = requests.get(personsurl + "?page=2&size=6")
    data = response.json()
    assert response.ok
    assert data["protocol"]["page"] == 2
    assert data["persons"][0]["@id"] == "Person 007"
    assert len(data["persons"]) == 6


def test_no_more_pages(mockserver, personsurl):
    "If no results or no more results are found, server must return 404"
    response = requests.get(personsurl + "?page=20")
    assert response.status_code == 404
    assert response.json()["detail"] == "No (more) results found."

    response = requests.get(personsurl + "?sourceId=xxx")
    assert response.status_code == 404
    assert response.json()["detail"] == "No (more) results found."


def test_size(mockserver, personsurl):
    "Size controls the number of persons returned"
    response = requests.get(personsurl + "?size=3")
    assert response.ok
    assert len(response.json()["persons"]) == 3

    response = requests.get(personsurl + "?size=14")
    assert response.ok
    assert len(response.json()["persons"]) == 14


def test_max_size(mockserver, personsurl):
    "Value of size= must not be greater than max_size."
    url = personsurl + "?size=500"
    response = requests.get(url)
    assert response.status_code == 400
    assert response.json()["detail"] == "Value of parameter size= must not be greater than 200"


def test_filter(mockserver, personsurl):
    """Some minimal filter tests.

    Diltering in tested in the connectpr object.
    """
    response = requests.get(personsurl + "?sourceId=Source+002")
    assert response.ok
    assert len(response.json()["persons"]) == 3

    # Search for personId must match the full id
    response = requests.get(personsurl + "?sourceId=Source")
    assert response.status_code == 404

    response = requests.get(personsurl + "?sourceId=Source+002&st=Statement content 3")
    # print(r.json())
    assert response.ok
    assert len(response.json()["persons"]) == 3


def test_filter_without_result(mockserver, personsurl):
    "Search for a non existing factoid."
    response = requests.get(personsurl + "?sourceId=Source+X")
    assert response.status_code == 404
