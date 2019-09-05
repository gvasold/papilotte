"""Handles all methods on .../persons
"""
import importlib

from connexion import problem
from flask import request

from papilotte import options


connector_module = importlib.import_module(options["connector"])


def get(id):
    """Handle a GET request on .../persons/{id}.
    """
    connector = connector_module.PersonConnector(options)
    data = connector.get(id)
    if data is None:
        return problem(404, "Not found", "Person %s does not exist." % id)
    data["id"] = request.url
    return data


def validate_search(func):
    "Validating decoration for search function."
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
def search(size, page, sortBy="createdWhen", body=None, **filters):
    """Handle a GET request on .../persons.
    """
    connector = connector_module.PersonConnector(options)
    persons = connector.search(size, page, sortBy, **filters)
    if not persons:
        return problem(404, "Not found", "No (more) results found.")
    total_hits = connector.count(**filters)
    return {
        "protocol": {"page": page, "size": size, "totalHits": total_hits},
        "data": persons,
    }


def post(body):
    """Handles a POST request on .../persons.
    :param body: The payload in json format like specified in
        the api spec
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
    connector = connector_module.PersonConnector(options)
    data = connector.save(body)
    return data


def put(id, body):
    """Handles a PUT request on .../persons/{id}.
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
