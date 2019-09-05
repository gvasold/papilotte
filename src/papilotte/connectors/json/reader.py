"Provides the central read from json function."
import json
import re
import datetime
import tempfile
import os
import hashlib


def fix_metadata_date(date_str, default_date_str):
    """Make sure date_str is a date string in this format: yyyy-mm-dd.
    
    :param date_str: A string representing a date as used in createdWhen
    :type date_str: str
    :default_date_str: A value to use if date_str is None. This must be in 
                       format yyyy-mm-dd.
    :return: The date part of date_str or default_date if date_str is None.
    :rtype: str
    """
    if date_str is None:
        date_str = default_date_str
    else:
        if not re.match(r"^\d{4}-\d{1,2}-\d{1,2}$", date_str):
            # fix a time stamp
            match = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2}).*", date_str)
            if match:
                date_str = "%04d-%02d-%02d" % (
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                )
            else:
                raise ValueError("'%s' is not a valid date!" % date_str)
    return date_str


def fix_metadata(factoid, contact, today_str):
    """Insert missing or not fully correct metadata for all data.

    Try do set missing metdata where appropriate.
    We do this to keep data consistent as these operations normally would
    be done during the creation process. 

    For now er try to fix as much as possible. Should be replaced by proper
    validation.
    # TODO: this is more of a hack until we can use the database
    :param contact: the contact property from configuration. This is used if data does
                    not contain creator info.
    """
    factoid["createdWhen"] = fix_metadata_date(factoid.get("createdWhen"), today_str)
    factoid["modifiedWhen"] = fix_metadata_date(
        factoid.get("modifiedWhen"), factoid["createdWhen"]
    )
    if "createdBy" not in factoid:
        factoid["createdBy"] = contact
    if "modifiedBy" not in factoid:
        factoid["modifiedBy"] = factoid["createdBy"]
    # make sure each statement, source and person has metadata.
    # Use factoid metadata for missing values.
    for obj in (factoid["statement"], factoid["source"], factoid["person"]):
        for property in ("createdWhen", "createdBy"):
            if property not in obj or not obj[property]:
                obj[property] = factoid[property]
        obj["createdWhen"] = fix_metadata_date(
            obj["createdWhen"], factoid["createdWhen"]
        )
        if "modifiedBy" not in obj or not obj["modifiedBy"]:
            obj["modifiedBy"] = obj["createdBy"]
        if "modifiedWhen" not in obj or not obj["modifiedWhen"]:
            obj["modifiedWhen"] = obj["createdWhen"]
    return factoid


# def read_original_json(jsonfile):
#     """Read jsonfile into an array of dicts


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


def read_json_file(jsonfile, contact):
    """Read the json File from disk.

    On the root level the json can be a list of factoids or a
    dict with a property 'factoids'.
    TODO: as soon as we have database support (sqlite here) implemented,
          we can insert the data into the database and keep it there until
          data changes. Then we can also scip the mock filter and use the
          database conncector logic.
    """
    factoids = []
    cache_file = get_cache_file_name(jsonfile)
    # TODO: add some more efficient caching (see: https://gist.github.com/cactus/4073643)
    if use_cache(jsonfile, cache_file):
        with open(cache_file) as file_:
            factoids = json.load(file_)
    else:  # read original file and do some cleanup
        with open(jsonfile, encoding="utf-8") as file_:
            data = json.load(file_)
            if isinstance(data, dict):  # date might also be a json object
                data = data["factoids"]
        today = datetime.date.today()
        today_str = "%04d-%02d-%02d" % (today.year, today.month, today.day)
        for factoid in data:
            factoids.append(fix_metadata(factoid, contact, today_str))
        with open(cache_file, "w") as file_:
            json.dump(factoids, file_)
    return factoids
