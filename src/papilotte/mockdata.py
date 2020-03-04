"""Module to generate Mock Factoids for testing.
"""
import argparse
import json
import datetime

statement_counter = 0

def make_metadate(num, is_modification_date=False):
    "Return a datetime iso string"
    start_date = datetime.datetime(2003, 2, 15)
    delta = datetime.timedelta(minutes=num*3) 
    mdate = start_date + delta
    if is_modification_date:
        mdate = mdate + delta
    return mdate.isoformat()

def make_uris(num, path_prefix):
    "Return list of uris."
    rv = []
    num_of_uris_to_create = num % 5
    suffixes = 'abcdefgh'
    for i in range(num_of_uris_to_create):
        suffix = suffixes[i]
        rv.append('https://example.com/{}/{}{}'.format(path_prefix, num, suffix))
    return rv

def make_historical_date(num, after=datetime.date(1800, 5, 5)):
    "Create a ISO-Date-String."
    # every 20th date is missing
    if num % 20 == 0:
        return ""
    day_offset = ((num + 17) * 2343) % (365 * 3)
    hdate = after + datetime.timedelta(days=day_offset)
    return hdate.isoformat()

def make_labeled_uri(num, uri_prefix, label_prefix, modulo):
    "Create a dict with 2 keys: `label` and `uri`."
    data = {
        "uri": "https://example.com/{}/{:05d}".format(uri_prefix, num % modulo),
        "label": "{} {:05d}".format(label_prefix, num % 125)
    }
    # make part of data incomplete
    if num % 3 == 0:
        del data['uri']
    if num % 5 == 0:
        del data['label']
    return data
    

def make_person(pnum):
    """Create a single person as dict.

    :param num: A number (counter) where most values are based on.
    :type num: int
    :return: Person data as dict 
    """
    data = {
        "@id": "P{:05d}".format(pnum),
        "uris": make_uris(pnum, 'persons'),
        "createdBy": "Creator {:05d}".format(pnum // 75 + 1),
        "createdWhen": make_metadate(pnum),
        "modifiedBy": "Modifier {:05d}".format(pnum // 25 + 1),
        "modifiedWhen": make_metadate(pnum, True),
    }
    if pnum % 3 == 0:
        del data['modifiedWhen']
        del data["modifiedBy"]
    if pnum % 6 == 0:
        del data['createdWhen']
        del data['createdBy']
    return data



def make_source(snum):
    """Create a single source as dict.

    :param num: A number (counter) where most values are based on.
    :type num: int
    :return: Source data as dict 
    """
    data = {
        "@id": "S{:05}".format(snum),
        "uris": make_uris(snum, 'sources'),
        "label": "Source {:05d}".format(snum),
        "createdBy": "Creator {:05d}".format(snum // 65 + 1),
        "createdWhen": make_metadate(snum),
        "modifiedBy": "Modifier {:05d}".format(snum // 35 + 1),
        "modifiedWhen": make_metadate(snum, True)
    }
    if snum % 3 == 0:
        del data['modifiedWhen']
        del data["modifiedBy"]
    if snum % 6 == 0:
        del data['createdWhen']
        del data['createdBy']
    if snum % 5 == 0:
        del data["label"]
    return data

def make_statement(fnum, snum) :
    """Create a single statement as dict.

    :param num: A number (counter) where most values are based on.
    :type num: int
    :return: Statement data as dict 
    """
    global statement_counter
    statement_counter += 1
    num = fnum + snum
    data = {
        "@id": "Stmt{:05d}".format(statement_counter),
        "createdBy": "Creator {:05d}".format(fnum // 50 + 1),
        "createdWhen": make_metadate(fnum),
        "modifiedBy": "Modifier {:05d}".format(fnum // 20 + 1),
        "modifiedWhen": make_metadate(fnum, True),
        "uris": make_uris(statement_counter, 'statements'),
        "name": "Statement {:05d}".format(statement_counter),
        "date": {"sortDate": make_historical_date(num), 
                 "label": "Historical Date {:05d}".format((snum + statement_counter) % 125 + 1)},
        "memberOf": make_labeled_uri(num, 'groups', 'Group', 125),
        "places": [],
        "relatesToPersons": [],
        "role": make_labeled_uri(num, "roles", "Role", 140),
        "statementContent": "Statement content {:05d}".format(num),
        "statementType": make_labeled_uri(num, "statementtypes", "Statement type", 40)
    }
    for i in range(num % 5):
        data["places"].append(make_labeled_uri(num + i, "places", 'Place', 755))
    for i in range(num % 3):
        data["relatesToPersons"].append(
            make_labeled_uri(num + i, "relatedpersons", "Related person", 300))
    if num % 2 == 0:
        del data['modifiedWhen']
        del data["modifiedBy"]
    if num % 4 == 0:
        del data['createdWhen']
        del data['createdBy']
    if num % 5 == 0:
        del data["name"]
    if num % 7 == 0:
        del data["statementContent"]
    return data

def make_factoid(num, base_url='http://localhost:5000/api'):
    """Create a single factoid as dict.

    :param num: A number (counter) where all values are based on.
    :param base_url: The base url used to construct references. Default value is
            `https://localhost:5000/api'.
    :type num: int
    :type base_uri: str
    :return: factoid data (including all sub objects) as dict
    """
    data = {
        "@id": "F{:05d}".format(num),
        "createdBy": "Creator {:05d}".format(num // 50 + 1),
        "createdWhen": make_metadate(num),
        "modifiedBy": "Modifier {:05d}".format(num // 20 + 1),
        "modifiedWhen": make_metadate(num, True),
    }
    p_num = (num % 75) + 1
    data["person"] = make_person(p_num)
    s_num = (num % 100) + 1
    data["source"] = make_source(s_num)
    data["statements"] = []
    for i in range(1, (num % 5) + 2):
        stmt = make_statement(num, i)
        data['statements'].append(stmt)
    if num > 10 and num % 7 == 0:
        derived_id = int(num / 10 + num % 10)
        data["derivedFrom"] = "{}/factoids/{}".format(base_url, derived_id)
    if num % 5 != 0:
        del data['modifiedWhen']
        del data["modifiedBy"]
    return data


def make_factoids(num_of_factoids, base_url='http://localhost:5000/api'):
    "A Factoid generator."
    counter = 1
    global statement_counter
    statement_counter = 0
    while True:
        if counter == num_of_factoids + 1:
            break
        yield make_factoid(counter, base_url)
        counter += 1
