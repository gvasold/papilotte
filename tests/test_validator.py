from papilotte.validator import get_schema, get_strict_schema, validate
from jsonschema.exceptions import ValidationError
import pytest


def test_get_schema():
    "Test if jsonschema extraction from openapi spec works."
    data = get_schema()
    assert "Factoid" in data["components"]["schemas"]


def test_get_strict_schema():
    """Test if jsonschema contains additionalProperties=False."""
    data = get_strict_schema()
    schemas = data["components"]["schemas"]
    assert not schemas["Factoid"]["additionalProperties"]
    assert not schemas["Person"]["additionalProperties"]
    assert not schemas["Source"]["additionalProperties"]
    assert not schemas["Statement"]["additionalProperties"]


def test_validate(minimal_factoid):
    "Validate a simple factoid."
    validate(minimal_factoid)


def test_validate_full(mock_factoid):
    "Validate a full factoid."
    validate(mock_factoid)


def test_strict_validation(mock_factoid):
    "Test the strict mode of validation."
    # Validate has a strict parameter, which is set to False by default.
    # So adding additional properties should be ok if strict=False
    mock_factoid["foo"] = "bar"
    validate(mock_factoid)
    # but it should raise a validation error if set to True
    with pytest.raises(ValidationError):
        validate(mock_factoid, strict=True)


def test_validate_sortdate(mock_factoid):
    "Sortdate defines a regex pattern which should be tested, too"
    # year only is valid
    mock_factoid["statement"]["date"]["sortdate"] = "1899"
    validate(mock_factoid)
    # year-month is valid
    mock_factoid["statement"]["date"]["sortdate"] = "1899-05"
    validate(mock_factoid)
    # year-month-day is valid
    mock_factoid["statement"]["date"]["sortdate"] = "1899-05-12"
    validate(mock_factoid)
    # yyyy-00-dd is invalid
    mock_factoid["statement"]["date"]["sortdate"] = "1899-00-12"
    with pytest.raises(ValidationError):
        validate(mock_factoid)
    # yyyy-mm-00 is invalid
    mock_factoid["statement"]["date"]["sortdate"] = "1899-05-00"
    with pytest.raises(ValidationError):
        validate(mock_factoid)
    # yyyy-00-00 is invalid
    mock_factoid["statement"]["date"]["sortdate"] = "1899-00-00"
    with pytest.raises(ValidationError):
        validate(mock_factoid)


def test_missing_source_id(mock_factoid):
    "Validation an invalid factoid must raise a ValidationError."
    del mock_factoid["source"]["@id"]
    with pytest.raises(ValidationError):
        validate(mock_factoid)

