#!/usr/bin/env python
"""This script can be used to validate a json file containing factoids.

Run `validate_factoids --help` for more information.
"""
import json
import yaml
import sys
import click
from papilotte import validator
from jsonschema.exceptions import ValidationError


def run(jsonfile, quiet=False, permissive=False, spec_file=None):
    """Does the real validation work.

    :param jsonfile: Path to the file to validate
    :type jsonfile: str
    :param quiet: If set to True suppresses all output
    :type quiet: bool
    :param permessive: If set to True, validation will allow object properties,
        which are not part of the IPIF specification. For compatibility it it
        advisable not to use this parameter.
    :param spec_file: OpenAPI spec file to use for validation
    :type spec_file: str
    :return: True if no validation errors occured.
    """
    with open(jsonfile, encoding="UTF-8") as file_:
        data = json.load(file_)
    if isinstance(data, dict):
        data = data["factoids"]
    valid_factoid_counter = 0
    invalid_factoid_counter = 0
    for factoid in data:
        f_id = factoid["@id"]
        try:
            strict = not permissive
            validator.validate(factoid, strict=strict, spec_file=spec_file)
            valid_factoid_counter += 1
        except ValidationError as err:
            invalid_factoid_counter += 1
            if not quiet:
                print(
                    "{} ... invalid\n\t{}".format(
                        f_id, validator.make_readable_validation_msg(err)
                    ),
                    flush=True,
                )
    if not quiet:
        print(
            "Checked {} factoids. Found {} invalid factoids.".format(
                (valid_factoid_counter + invalid_factoid_counter),
                invalid_factoid_counter,
            )
        )
    return invalid_factoid_counter == 0


@click.command()
@click.argument("jsonfile")
@click.option("-q", "--quiet", is_flag=True, help="Suppress output")
@click.option('-p', '--permissive', is_flag=True, 
              help="Allow properties which are not part of the IPIF spec")
@click.option(
    "-s",
    "--spec-file",
    default=None,
    help=(
        "Path to non default openapi spec file. Use it only if you have a "
        "custom spec file"
    ),
)
def main(jsonfile, quiet, permissive, spec_file):
    """Validates a json file containing factoids against the OpenAPI spec.

    The JSON file can contain the factoids directly as array:

        [{"@id": "Factoid 1", ...}, {"@id": "Factoid 2", ...}] 
    
    or as an object with a property 'factoids':

        {"factoids:" [{"@id": "Factoid 1", ...}, {"@id": "Factoid 2", ...}]}

    It might be a good idea to use this script on your data before adding it
    to Papilotte.

    Returns 0 if no validation errors were found, otherwise 1.
    """
    if run(jsonfile, quiet, permissive, spec_file):
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()

