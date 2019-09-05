"""System tests for /describe.
"""
import requests
from conftest import BASE_URL


def test_describe(mockserver):
    "Test request to /describe."
    # pylint: disable=unused-argument
    url = BASE_URL + "describe"
    response = requests.get(url)
    data = response.json()
    assert (
        data["provider"]
        == "Name of the individual or " + "institution running the service"
    )
    assert data["complianceLevel"] == 1
    assert data["contact"] == "contact@example.com"
    assert (
        data["description"] == "Short description of the data " + "the service provides"
    )
    assert data["formats"] == ["application/json"]
