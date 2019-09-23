"""Handles all methods on .../statements
"""
import importlib

from connexion import problem
from flask import request

from papilotte import options

connector_module = importlib.import_module(options["connector"])


def get_statement_by_id(id):
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
def get_statements(size, page, body=None, sortBy="createdWhen", **filters):
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


