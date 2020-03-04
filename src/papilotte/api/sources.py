"""Handles all methods on .../sources
"""
from connexion import problem
from flask import request

from flask import current_app as app
from papilotte.exceptions import DeletionError
from papilotte.exceptions import (CreationException, DeletionError,
                                  ReferentialIntegrityError, InvalidIdError)
from papilotte.api import is_valid_id, split_sortby, fix_ids

ALLOWED_SORT_BY_VALUES = ['id', 'label', 'createdWhen', 'createdBy', 'modifiedWhen', 'modifiedBy']
# These are excluded by spec: ['createdAfter', 'createdBefore', 'createdBy', 'modifiedAfter', 'modifiedBefore', 'modifiedBy', 'sourceId']
# These filters can be used in CL0
# TODO: re-check against spec
ALLOWED_FILTERS_CL0 = ['factoidid', 'from', 'memberof', 'name', 'personId', 'place', 'relatestoperson', 
    'role', 'sourceid', 'statementcontent', 'statementid', 'to']

# These filters can be used in CL1 and CL2
ALLOWED_EXTRA_FILTERS = ['f', 'p', 's', 'st']

def get_connector():
    "Utility function: return the configured papilotte connector."
    connector_module = app.config['PAPI_CONNECTOR_MODULE']
    connector_configuration = app.config['PAPI_CONNECTOR_CONFIGURATION']
    return connector_module.SourceConnector(connector_configuration)

def validate_search(func):
    "Validating decoration for search function."
    def wrapper(*args, **kwargs):
        # validate size
        if kwargs["size"] > app.config["PAPI_MAX_SIZE"]:
            return problem( 400, "Bad Request",
                "Value of parameter size= must not be greater than %d"
                % app.config["PAPI_MAX_SIZE"]
            )
        # validate value of sortBy    
        sort_by, _ = split_sortby(kwargs['sortBy'])
        if sort_by.lower() not in [v.lower() for v in ALLOWED_SORT_BY_VALUES]:
            return problem( 400, "Bad Request",
                "Value '{}' of parameter sortBy= is not allowed. Use one of these values: {}".format(
                    kwargs['sortBy'], ", ".join(ALLOWED_SORT_BY_VALUES)))
        # validate filter names (depending on compliance level)
        non_filters = ('size', 'page', 'sortBy', 'body')
        if app.config['PAPI_COMPLIANCE_LEVEL'] == 0:
            for kw in kwargs:
                if kw not in non_filters and not kw.lower() in ALLOWED_FILTERS_CL0:
                    return problem(400, "Bad Request", "'{}' is not a valid filter for compliance level 0".format(kw))
        else: # compliance level > 0
            allowed_filters = ALLOWED_FILTERS_CL0 + ALLOWED_EXTRA_FILTERS
            for kw in kwargs:
                if kw not in non_filters and not kw.lower() in allowed_filters:
                    return problem(400, "Bad Request", 
                        "'{}' is not a valid filter for compliance level {}".format(kw, app.config['PAPI_COMPLIANCE_LEVEL']))
        return func(*args, **kwargs)
    return wrapper


@validate_search
def get_sources(size, page, sortBy='createdWhen', body=None, **filters):
    """Return a (filtered) list of sources.
    """
    connector = get_connector()
    # we assume all other kwargs are filters
    sort_by, sort_order = split_sortby(sortBy)

    # from is a reserved word, so we replace it with 'from_'
    from_ = filters.pop('from', '')
    if from_: filters['from_'] = from_
    
    sources = connector.search(size, page, sort_by, sort_order, **filters)
    if not sources:
        return problem(404, "Not found", "No (more) results found.")
    total_hits = connector.count(**filters)
    return {
        "protocol": {"page": page, "size": size, "totalHits": total_hits},
        "sources": sources
    }


def get_source_by_id(id):
    "Return source object with id `id` or raise a 404 error."
    connector = get_connector()
    data = connector.get(id)
    if data is None:
        return problem(404, "Not found", "Source %s does not exist." % id)
    return data

def create_source(body):
    # TODO: metadata enrichment if not set?
    if app.config["PAPI_COMPLIANCE_LEVEL"] < 2:
        return problem(
            501,
            "Not implemented",
            "Compliance level {} does not allow PUT requests.".format(
                app.config["PAPI_COMPLIANCE_LEVEL"]
            ),
        )
    connector = get_connector()
    # it seems that connexion converts '@id' to 'id'??
    # to make thing consistent for further processing, we revert this
    body = fix_ids(body)
    #if not '@id' in body and 'id' in body:
    #    body['@id'] = body['id']

    # This should be handled by spec!
    #if '@id' in body and not is_valid_id(body['@id']):
    #    return problem(400, "Bad Request", 'Illegal character in id')

    try:
        data = connector.create(body)
        return data
    except CreationException as err:
        return problem( 409, "Conflict", str(err))

def update_source(id, body):
    # TODO: metadata enrichment if not set?

    if app.config["PAPI_COMPLIANCE_LEVEL"] < 2:
        return problem(
            501,
            "Not implemented",
            "Compliance level {} does not allow PUT requests.".format(
                app.config["PAPI_COMPLIANCE_LEVEL"]
            ),
        )
    # This should be handled by spec!
    #if not is_valid_id(id):
    #    return problem(400, "Bad Request", str('Illegal character in id.'))
    connector = get_connector()
    data = connector.update(id, body)
    return data

def delete_source(id):
    """Delete Source with id `id`. 

    Only allowed in comliance level 2.
    """
    if app.config["PAPI_COMPLIANCE_LEVEL"] < 2:
        return problem(
            501,
            "Not implemented",
            "Compliance level {} does not allow DELETE requests.".format(
                app.config["PAPI_COMPLIANCE_LEVEL"]
            ),
        )
    connector = get_connector()
    if connector.get(id) is None:
        return problem(404, "Not found", "Source %s does not exist." % id)
    try:
        connector.delete(id)
    except ReferentialIntegrityError as err:
        return problem(409, "Conflict", str(err))
    except DeletionError as err:
        # a more generic probem during deletion
        return problem(500, "Server Error", str(err))
