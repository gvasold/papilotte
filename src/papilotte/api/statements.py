"""Handles all methods on .../statements
"""
import importlib

from connexion import problem
from flask import request

from papilotte import options

connector_module = importlib.import_module(options["connector"])


def get(id):
    """Handle a GET request on .../statements/{id}.
    """
    connector = connector_module.StatementConnector(options)
    data = connector.get(id)
    if data is None:
        return problem(404, "Not found", "Statement %s does not exist." % id)
    data["id"] = request.url
    return data


def validate_search(func):
    "Validating decorator for search."
    # TODO: validate allowed sort_by names!
    def wrapper(*args, **kwargs):
        if kwargs["size"] > options["max_size"]:
            return problem(
                400,
                "Bad Request",
                "Value of parameter size= must not be greater than %d"
                % options["max_size"],
            )
        return func(*args, **kwargs)

    return wrapper


@validate_search
def search(size, page, body=None, sortBy="createdWhen", **filters):
    """Handle a GET request on .../statements.
    """
    connector = connector_module.StatementConnector(options)
    statements = connector.search(size, page, sortBy, **filters)
    if not statements:
        return problem(404, "Not found", "No (more) results found.")
    total_hits = connector.count(**filters)
    return {
        "protocol": {"page": page, "size": size, "totalHits": total_hits},
        "statements": statements,
    }


def post(body):
    """Handles a POST request on .../statements.
    """
    # TODO: in der Spec darf hier id nicht erlaubt sein!?!
    # Oder sollte die id ausgelesen und verwendet werden?
    # Tendenz: eher simpel halten!
    # TODO: metadata enrichment if not set
    if options["compliance_level"] < 2:
        return problem(
            501,
            "Not implemented",
            "Compliance level {} does not allow POST requests.".format(
                options["compliance_level"]
            ),
        )
    connector = connector_module.StatementConnector(options)
    data = connector.save(body)
    return data


def put(id, body):
    """Handles a PUT request on .../statements/{id}.
    """
    # TODO: in der Spec darf hier id nicht erlaubt sein!?!
    # TODO: metadata enrichment if not set
    if options["compliance_level"] < 2:
        return problem(
            501,
            "Not implemented",
            "Compliance level {} does not allow PUT requests.".format(
                options["compliance_level"]
            ),
        )
    connector = connector_module.PersonConnector(options)
    data = connector.update(id, body)
    return data

