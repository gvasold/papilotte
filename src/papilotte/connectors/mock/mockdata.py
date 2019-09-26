"""Generators for mock data.

Provides these generators:

    * generate_person()
    * generate_source()
    * generate_statement()
    * generate_factoid()

Repeated calls generate the same output.
"""


import calendar
import datetime
import itertools
import math

FIRST_DATETIME = datetime.datetime(2004, 5, 3, 17, 23, 55)


def get_datetime(base_date, counter, use_extra_offset=False):
    """Generate a date-time string.
    
    The string follows RFC 3339 (eg. 2005-04-12T15:22:13-02:00).
    It is guaranteed, that a higher counter leads to a later datetime.

    :param base_date: a datetime.datetime object used as base datetime.
    :type base_date: datetime.datetime
    :param counter: an int. Typically the counter of a loop.
    :type counter: int
    :param use_extra_offset: Indicates wheather an extra time offset
          should be used or not. The extra comes in handy for
          modification dates.
    :type use_extra_offset: bool
    :return: a string in the form YYYY-MM-DD
    :rtype: str
    """
    offset_seconds = counter * 123456
    if use_extra_offset:
        offset_seconds += (counter % 5) * counter * 80000
    newdate = base_date + datetime.timedelta(seconds=offset_seconds)
    return newdate.isoformat() + '+02:00'


def get_creator(counter):
    """Return a creator name based on counter.

    :param counter: An integer. This value normally comes from a loop.
    :type counter: int
    :return: A string usable as value for createdBy
    :rtype: str
    """
    id_ = (counter - 1) % 5
    return "Creator %d" % (id_ + 1)


def get_modifier(counter):
    """Return a modifier name based on counter.

    :param counter: An integer. This value normally comes from a loop.
    :type counter: int
    :return: A string usable as value for modifiedBy
    :rtype: str
    """
    id_ = (counter + 1) % 3
    return "Modifier %d" % (id_ + 1)


def get_uris(counter):
    """Return a list of uris modifier name based on counter.

    :param counter: An integer. This value normally comes from a loop.
    :type counter: int
    :return: A list of strings, where each element represents an uri.
    :rtype: list
    """
    rv = []
    num = counter * (counter + 1) % 8
    for i in range(num):
        rv.append("http://example.com/%d" % (i + 1))
    return rv


def make_date(num):
    """Create a date object consisting of a label and sortdate.

    :param num: a number derived from a counter
    :type num: int
    :return: A dict consisting of 2 keys: label and sortdate. The dict
        might also be empty.
    :rtype: dict
    """
    # compute idempotent year, month, date
    year = 1800 + (num % 50)
    month = num % 12
    if month == 0:
        month = 12
    day = num % 31
    if day == 0:
        day = 31
    if day == 31 and month in (4, 6, 9, 11):
        day = 30
    elif month == 2 and day > 28:
        if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0):
            day = 29
        else:
            day = 28
    # decide if date is full, year and month or only year
    format_indicator = num % 5
    if format_indicator == 1:
        date_dict = {"label": "%d" % year, "sortdate": "%d" % year}
    elif format_indicator == 2:
        date_dict = {
            "label": "%s %d" % (calendar.month_name[month], year),
            "sortdate": "%d-%02d" % (year, month),
        }
    elif format_indicator == 3:
        date_dict = {
            "label": "%d %s %d" % (day, calendar.month_name[month], year),
            "sortdate": "%d-%02d-%02d" % (year, month, day),
        }
    elif format_indicator == 4:
        date_dict = {}
    else:  # 0
        date_dict = None
    return date_dict


def make_label_objects(num, base_label, counter):
    """Create a list of simple dicts, each consisting of a label and uri 
    key and value.

    :param num: Specify the number of elements of the list.
    :param type: int
    :param base_label: A string which sets the first part of the label
                       for each dict.
    :type base_label: str
    :param counter: An integer which normally comes from a loop counter.
    :return: A list if dictionaries. Each dictionary has
             two keys: label and uri.
    :rtype: list
    """
    rv = []
    for i in range(1, num + 1):
        rv.append(
            {
                "label": "%s %d_%d" % (base_label.capitalize(), counter, i),
                "uri": "http://example.com/%s/%d/%d"
                % (base_label.replace(" ", "_"), counter, i),
            }
        )
    return rv


def generate_person(max_num=15):
    """Generator function for person object.

    We take care that any person with a specific id carries the same data.

    :param max_num: Maximimal number of different persons. 15 means that only
                    15 different person objects are generated no matter how often
                    next() is called.
    :type max_num: int
    :return: A generator for persons.
             Call next(generator) to generate a new person
    :rtype: generator
    """
    counter = 0
    cache = {}
    while True:
        p_id = "Person %03d" % ((counter % max_num) + 1)
        if p_id not in cache:
            obj = {}
            obj["@id"] = p_id
            obj["uris"] = get_uris(counter)
            obj["createdBy"] = get_creator(counter)
            obj["createdWhen"] = get_datetime(FIRST_DATETIME, counter, False)
            obj["modifiedBy"] = get_modifier(counter)
            obj["modifiedWhen"] = get_datetime(FIRST_DATETIME, counter, True)
            cache[p_id] = obj
        counter += 1
        yield cache[p_id]


def generate_source(max_num=25):
    """Generator function for source object.

    :param max_num: Maximimal number of different sources. 25 means that only
                    25 different source objects are generated no matter how often
                    next() is called.
    :type max_num: int
    :return: A generator for sources.
             Call next() to generate a new source
    :rtype: generator
    """
    counter = 0
    cache = {}
    while True:
        s_id = "Source %03d" % ((counter % max_num) + 1)
        if s_id not in cache:
            obj = {}
            obj["@id"] = s_id
            obj["label"] = "Label %s" % s_id
            obj["uris"] = get_uris(counter)
            obj["createdBy"] = get_creator(counter)
            obj["createdWhen"] = get_datetime(FIRST_DATETIME, counter, False)
            obj["modifiedBy"] = get_modifier(counter)
            obj["modifiedWhen"] = get_datetime(FIRST_DATETIME, counter, True)
            cache[s_id] = obj
        counter += 1
        yield cache[s_id]


def generate_statement(factoid, factoid_counter):
    """Generator function for statement objects.

    :param factoid: A factoid dict (or a mock which must contain these properties):
                      @id, createdBy, createdWhen, modifiedBy, modifiedWhen
    :type factoid: dict
    :param factoid_counter: A number indication home many factoids have been created
                            before. This is only used to broaden the variance of dates,
                            so it can be any number.
    :type factoid_counter: int
    :return: A generator for statements.
             Call next() to generate a new statement.
    :rtype: generator
    """
    counter = 1
    while True:
        obj = {}
        obj["@id"] = "F%dS%d" % (factoid_counter, counter)
        obj["uri"] = "http://example.com/statements/%d/%d" % (factoid_counter, counter)
        obj["statementType"] = make_label_objects(
            1, "statement type", (counter * factoid_counter) % 20
        )[0]
        obj["name"] = "Name %d" % ((counter * factoid_counter % 10) + 1)
        obj["role"] = make_label_objects(1, "role", counter * factoid_counter % 15)[0]
        the_date = make_date(counter * factoid_counter)
        if the_date is not None:
            obj["date"] = the_date
        obj["places"] = make_label_objects(
            counter % 40, "place", ((counter * factoid_counter) % 50) + 1
        )
        obj["relatesToPersons"] = make_label_objects(
            counter % 12, "related person", (counter * factoid_counter) % 45
        )
        obj["memberOf"] = make_label_objects(
            1, "member of", ((counter * factoid_counter) % 30) + 1
        )[0]
        obj["statementContent"] = "Statement content %d" % (
            (counter * factoid_counter % 25) + 1
        )
        obj["createdBy"] = factoid["createdBy"]
        obj["createdWhen"] = factoid["createdWhen"]
        obj["modifiedBy"] = factoid["modifiedBy"]
        obj["modifiedWhen"] = factoid["modifiedWhen"]
        counter += 1
        yield obj


def generate_factoid():
    """Generator function for factoid objects.

    :return: A generator for factoids.
             Call next() to generate a new factoid.
    :rtype: generator
    """
    p_generator = generate_person(15)
    s_generator = generate_source(25)
    counter = 0
    while True:
        counter += 1
        factoid = {}
        factoid["@id"] = "Factoid %03d" % counter
        factoid["person"] = next(p_generator)
        factoid["source"] = next(s_generator)
        factoid["createdBy"] = get_creator(counter)
        factoid["createdWhen"] = get_datetime(FIRST_DATETIME, counter, False)
        factoid["modifiedBy"] = get_modifier(counter)
        factoid["modifiedWhen"] = get_datetime(FIRST_DATETIME, counter, True)
        # No need for a generator here, but I keep it as it already exists
        st_generator = generate_statement(factoid, counter)
        factoid["statement"] = next(st_generator)
        yield factoid


def make_factoids(num):
    """Generate num mock factoids.

    This is a helper function to generate any number of factoids for testing.
    """
    factoids = []
    generator = generate_factoid()
    for _ in range(num):
        factoids.append(next(generator))
    return factoids


if __name__ == "__main__":
    import json

    g = generate_factoid()
    for fid in range(100):
        print(json.dumps(next(g)))
        print()
