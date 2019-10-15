"""Provides function for (external) json validation.
"""
import jsonschema
import copy
from pkg_resources import resource_filename
import yaml
import json

cached_schema = {}
cached_strict_schema = {}

class JSONValidationError(Exception):
    pass


def make_readable_validation_msg(err):
    "Extract compact information from ValidationError err."
    clean_path = [el for el in err.schema_path if el != "properties"]
    error_path = "->".join(clean_path[:-1])
    return "{}: {}".format(err.message, error_path)


def get_schema(spec_file=None):
    """Return the jsonschema contained in spec_file.

    Using this function directly does not make much sense. Use validate() instead.

    Uses caching to speed things up.

    :param spec_file: The path the the OpenAPI spec file to use for
                      validation.
    :type spec_file: str
    :return: A dict containing the jsonschema extracted from the OpenAPI spec.
    """
    global cached_schema
    if not cached_schema:
        # Use the default spec file
        if not spec_file:
            spec_file = resource_filename("papilotte", "openapi/ipif.yml")

        with open(spec_file, encoding="UTF-8") as file_:
            spec_data = yaml.safe_load(file_)
        schema_dict = {}
        for schema_name, schema in spec_data["components"]["schemas"].items():
            if "example" in schema:
                del schema["example"]
            schema_dict[schema_name] = schema
        # It's easier to keep the $refs untouched than to simplify the structure
        cached_schema = {
            "$schema": "http://json-schema.org/schema#",
            "additionalProperties": False,
            "components": {"schemas": schema_dict},
        }
    return cached_schema



def get_strict_schema(spec_file=None):
    """Return the jsonschema contained in spec_file for strict validation.

    Using this function directly does not make much sense. Use validate() instead.

    Uses caching to speed things up.

    :param spec_file: The path the the OpenAPI spec file to use for
                      validation.
    :type spec_file: str
    :return: A dict containing the jsonschema extracted from the OpenAPI spec.
    """
    global cached_strict_schema
    if not cached_strict_schema:
        # Use the default spec file
        if not spec_file:
            spec_file = resource_filename("papilotte", "openapi/ipif.yml")

        with open(spec_file, encoding="UTF-8") as file_:
            spec_data = yaml.safe_load(file_)
        schema_dict = {}
        for schema_name, schema in spec_data["components"]["schemas"].items():
            if "example" in schema:
                del schema["example"]
            if (
                "object" not in schema or schema["type"] == "object"
            ) and "additionalProperties" not in schema:
                schema["additionalProperties"] = False                
            schema_dict[schema_name] = schema
        # It's easier to keep the $refs untouched than to simplify the structure
        cached_strict_schema = {
            "$schema": "http://json-schema.org/schema#",
            "additionalProperties": False,
            "components": {"schemas": schema_dict},
        }
    return cached_strict_schema


def validate(factoid, strict=False, spec_file=None):
    """Validate a single factoid.

    :param factoid: A single factoid
    :type factoid: dict
    :param strict: If set to True, formats does not validate if data contains 
        properties which are not specified in the spec. Using this is recommend
        for external validation.
    :type strict: bool
    :param spec_file: Path to the OpenAPI spec file to use for validation.
            If omitted, the default ipif spec file will be used.
    :type spec_file: str
    :raises: jsonschema.exceptions.ValidationError, jsonschema.exception.SchemaError
    :return: None
    """
    if strict:
        schemata = get_strict_schema(spec_file)
    else:
        schemata = get_schema(spec_file)
    factoid_schema = schemata["components"]["schemas"]["Factoid"]
    schemastore = {"": schemata}
    resolver = jsonschema.RefResolver(
        base_uri="", referrer=schemata, store=schemastore
    )
    format_checker = jsonschema.FormatChecker()
    jsonschema.validate(
        factoid, factoid_schema, format_checker=format_checker, resolver=resolver
    )
