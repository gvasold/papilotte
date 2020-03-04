"""System tests for /describe.
"""
import requests

import pytest
import connexion



def test_describe(mockclient_cl0):
    response = mockclient_cl0.get('/api/describe')
    assert response.status_code == 200
    data = response.json
    assert data["provider"] == "MockProvider"
    assert data["complianceLevel"] == 0
    assert data["contact"] == "MockContact"
    assert data["description"] == "MockDescription"
    assert data["formats"] == ["application/json"]


