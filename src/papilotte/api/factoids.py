"""Handles all methods on .../factoids
"""

import importlib

from connexion import problem

from papilotte import options
from papilotte.errors import DeletionError

connector_module = importlib.import_module(options["connector"])


def get_factoid_by_id(id):
    """Handle a GET request on .../factoids/{id}.

    :param factoid_id: the id of the factoid to return.
    :type status: str
    :return: a single factoid
    :rtype: Factoid
    """
    connector = connector_module.FactoidConnector(options)
    data = connector.get(id)
    if data is None:
        return problem(404, "Not found", "Factoid %s does not exist." % id)
    return data


def validate_search(func):
    "Validation decorator for search."
    # TODO: validate allowed sort_by names! Either in spec or here.
    def wrapper(*args, **kwargs):
        if kwargs["size"] > options["max_size"]:
            return problem(
                400,
                "Bad Request",
                "Value of parameter size= must not be greater than %d"
                % options["max_size"],
            )
        ## FIXME: Gibt es eine Möglichkeit, tiefer zu suchen?
        ##        z.B. statement/id usw.????
        # allowed_sortby_values = ('createdWhen', 'createdBy',
        #        'modifiedWhen', 'modifiedBy', 'id')
        # if 'sortBy' in kwargs:
        #    if kwargs['sortBy'] not in allowed_sortby_values:
        #        return problem(400, "Bad Request",
        #            ("Value %s of sortBy is not allowed. Use one of "
        #            "%s!") % (kwargs['sortBy'], ', '.join(allowed_sortby_values)))
        return func(*args, **kwargs)

    return wrapper


@validate_search
def get_factoids(size, page, sortBy="createdWhen", body=None, **filters):
    """Handle a GET request on .../factoids.

    For some strange reason, body= is only used in connexion with python 3.7
    """
    connector = connector_module.FactoidConnector(options)
    factoids = connector.search(size, page, sortBy, **filters)
    if not factoids:
        return problem(404, "Not found", "No (more) results found.")
    total_hits = connector.count(**filters)
    return {
        "protocol": {"page": page, "size": size, "totalHits": total_hits},
        "factoids": factoids,
    }


def create_factoid(body):
    """Handles a POST request on .../factoids.
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

    connector = connector_module.FactoidConnector(options)
    data = connector.save(body)
    return data


def update_factoid(id, body):
    """Handles a PUT request on .../factoids/{id}.

    :param id: the id of the factoid to update.
    :type status: str
    :return: a single factoid
    :rtype: Factoid
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
    connector = connector_module.FactoidConnector(options)
    data = connector.update(id, body)
    return data


def delete_factoid(id):
    """Delete a Factoid.

    :param id: the id of the factoid to delete
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
    connector = connector_module.FactoidConnector(options)
    data = connector.get(id)
    if data is None:
        return problem(
            404, "Not found", "factoid '{}' does not exist.".format(id)
        )
    try:
        connector.delete(id)
    except DeletionError as err:
        return problem('409', 'Conflict', err)

        