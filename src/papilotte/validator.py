"""Provides function for (external) json validation.
"""
import jsonschema
from pkg_resources import resource_filename
import yaml
import json

cached_schema = {}

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
            spec_file = resource_filename('papilotte', 'openapi/ipif.yml')

        with open(spec_file, encoding='UTF-8') as file_:
            spec_data = yaml.safe_load(file_)
        schema_dict = {}
        for schema_name, schema in spec_data['components']['schemas'].items():
            if 'example' in schema:
                del schema['example']
            schema_dict[schema_name] = schema
        # It's easier to keep the $refs untouched than to simplify the structure
        cached_schema = {
            "$schema": "http://json-schema.org/schema#",
            'additionalProperties': False,
            'components': {'schemas': schema_dict}
        }
    return cached_schema

def validate(factoid, spec_file=None):
    """Validate a single factoid.

    :param spec_file: Path to the OpenAPI spec file to use for validation.
            If omitted, the default ipif spec file will be used.
    :type spec_file: str
    :raises: jsonschema.exceptions.ValidationError, jsonschema.exception.SchemaError
    :return: None
    """
    schemata = get_schema(spec_file)
    factoid_schema = schemata['components']['schemas']['Factoid']
    schemastore = {'': schemata}      
    resolver = jsonschema.RefResolver(base_uri='', referrer=schemata, store=schemastore)
    jsonschema.validate(factoid, factoid_schema, resolver=resolver)    
