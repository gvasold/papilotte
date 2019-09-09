"""Handles all methods on .../sources
"""

import importlib

from connexion import problem
from flask import request

from papilotte import options
from papilotte.errors import DeletionError

connector_module = importlib.import_module(options["connector"])


def get(id):
    """Handle a GET request on .../sources/{id}.
    """
    connector = connector_module.SourceConnector(options)
    data = connector.get(id)
    if data is None:
        return problem(404, "Not found", "Source %s does not exist." % id)
    data["id"] = request.url
    return data


def validate_search(func):
    "Validating decorator for search function."
    # TODO: validate allowed sortBy names!
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
    """Handle a GET request on .../sources.
    """
    connector = connector_module.SourceConnector(options)
    sources = connector.search(size, page, sortBy, **filters)
    if not sources:  # is None or len(sources) == 0:
        return problem(404, "Not found", "No (more) results found.")
    total_hits = connector.count(**filters)
    return {
        "protocol": {"page": page, "size": size, "totalHits": total_hits},
        "sources": sources,
    }


def post(body):
    """Handles a POST request on .../sources.
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
    connector = connector_module.SourceConnector(options)
    data = connector.save(body)
    return data


def put(id, body):
    """Handles a PUT request on .../sources/{id}.
    """
    # TODO: in der Spec darf hier id nicht erlaubt sein!?!
    # TODO: metadata enrichment if not set
    # TODO: id must only contain chars allowed in RFC3986#section-2.3: [A-Za-z0-9_.\-~]
    # everything else must be encoded via urllib.parse.quote
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


def delete(id):
    """Delete a source.

    :param id: the id of the source to delete
    :type id: str
    :return: None
    """
    if options["compliance_level"] < 2:
        return problem(
            501,
            "Not implemented",
            "Compliance level {} does not allow DELETE requests.".format(
                options["compliance_level"]
            ),
        )
    connector = connector_module.SourceConnector(options)
    data = connector.get(id)
    if data is None:
        return problem(404, "Not found", "source '{}' does not exist.".format(id))
    try:
        connector.delete(id)
    except DeletionError as err:
        return problem("409", "Conflict", err)
