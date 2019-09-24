"Provides the central read from json function."
import json
import re
import datetime
import tempfile
import os
import hashlib
from papilotte.validator import validate
from jsonschema.exceptions import ValidationError
import sys


def use_cache(orig_file, cache_file):
    "Return True if data can be read from cache file."
    use_cache = False
    if os.path.exists(cache_file):
        if os.path.getmtime(orig_file) < os.path.getmtime(cache_file):
            use_cache = True
    return use_cache


def get_cache_file_name(jsonfile):
    """Return a the name of a cache file.

    The file will reside in a temp folder and will be different for same
    jsonfile names in different paths.
    This function will also make sure that the cache dir exists.
    """
    cache_dir = os.path.join(
        tempfile.gettempdir(), hashlib.md5(jsonfile.encode("utf-8")).hexdigest()
    )
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, os.path.basename(jsonfile))


def get_stmt_metadata(factoid, property_name):
    """Return value of property_name for statement.

    Takes the value from statement or, if statement does not have
    such a property from the factoid.
    """
    value = factoid.get(property_name)
    stmt = factoid['statement']
    if property_name in stmt and stmt[property_name]:
        value = stmt[property_name]
    return value


def read_json_file(jsonfile):
    """Read the json File from disk.

    On the root level the json can be a list of factoids or a
    dict with a property 'factoids'.
    TODO: validate.
    TODO: when validation is implemented, fixing data should no longer be necessary!
    TODO: as soon as we have database support (sqlite here) implemented,
          we can insert the data into the database and keep it there until
          data changes. Then we can also scip the mock filter and use the
          database conncector logic.
    """
    cache_file = get_cache_file_name(jsonfile)
    # TODO: add some more efficient caching (see: https://gist.github.com/cactus/4073643)
    if use_cache(jsonfile, cache_file):
        with open(cache_file) as file_:
            data = json.load(file_)
    else:  # read original file and do some cleanup
        with open(jsonfile, encoding="utf-8") as file_:
            data = json.load(file_)
        if isinstance(data, dict):  # date might also be a json object
            data = data["factoids"]
            # add missing metadata to statements
            for factoid in data:
                factoid['statement']['createdBy'] = get_stmt_metadata(factoid, 'createdBy')
                factoid['statement']['createdWhen'] = get_stmt_metadata(factoid, 'createdWhen')
                if 'modifiedBy' in factoid:
                    factoid['statement']['modifiedBy'] = get_stmt_metadata(factoid, 'modifiedBy')
                if 'modifiedWhen' in factoid:
                    factoid['statement']['modifiedWhen'] = get_stmt_metadata(factoid, 'modifiedWhen')
        with open(cache_file, "w") as file_:
            json.dump(data, file_)
    return data
