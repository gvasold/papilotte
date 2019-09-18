from papilotte.validator import get_schema, validate
from jsonschema.exceptions import ValidationError
import pytest


def test_get_schema():
    "Test if jsonschema extraction from openapi spec works."
    data = get_schema()
    assert 'Factoid' in data['components']['schemas']


def test_validate(minimal_factoid):
    "Validate a simple factoid."
    validate(minimal_factoid)


def test_validate_full(mock_factoid):
    "Validate a full factoid."
    validate(mock_factoid)


def test_missing_source_id(mock_factoid):
    "Validation an invalid factoid must raise a ValidationError."
    del mock_factoid["source"]["@id"]
    with pytest.raises(ValidationError):
        validate(mock_factoid)
