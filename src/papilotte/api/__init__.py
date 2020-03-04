import re
import datetime
import calendar

from papilotte.exceptions import InvalidIdError

def is_valid_id(id_):
    """Test if on allowed chars are in id.
    
    These chars are: [A-Za-z0-9_.\\-~]
    See RFC3986#section-2.3
    # Possibly extend to IRI?
    """
    if not re.match(r'^[%A-Za-z0-9_.\\\-~]*$', id_):
        return False
    return True


def split_sortby(sort_by):
    """"Split the value of sortBy.
    
    sortBy can have a trailing 'ASC' oder 'DESC'. 
    This function returns the fieldname and 'ASC' or 'DESC' as tuple.
    """
    asc_desc = 'ASC'
    if sort_by.lower().endswith('asc'):
        sort_by_value = sort_by[:-3]
    elif sort_by.lower().endswith('desc'):
        sort_by_value = sort_by[:-4]
        asc_desc = 'DESC'
    else:
        sort_by_value = sort_by
    return sort_by_value, asc_desc


def parse_search_date(datestr, postquem=True):
    """Transform a single date (or part of a full date) into a iso style date format.

    This function takes a string representing an (incomplete) date like
    `yyyy-mm-dd` or `yyyy-mm` or `yyyy` and converts it to a full date string
    (yyyy-mm-dd).

    Examples:
    1932-1 becomes 1932-01-01 or 1932-01-31 if `postquem=` is set to `False`.

    :param datestr: A string representing an (incomplete) date like
                    2015-07-15, 2015-7 or 2015.
    :type datestr: str
    :param postquem: A boolean indication if datestr is a terminus
                     postquem (default: True) or terminus antequem
                     (False).
    :type postquem: bool
    :return: A string representing a full ISO date: yyyy-mm-dd
    :rtype: str
    :raises: ValueError is datestr is not interpretable as date.
    """
    match = re.match(r'^(-?\d{1,5})-?([01]?\d)?-?([0-3]?\d)?$', datestr)
    if match:
        year = match.group(1)
        month = match.group(2)
        day = match.group(3)
        if postquem: # terminus postquem
            if month is None:
                month = '01'
            if day is None:
                day = '01'
        else: # terminus antequem
            if month is None:
                month = 12
            if day is None:
                day = str(calendar.monthrange(int(year), int(month))[1])
        year = int(year)
        month =  int(month)
        day = int(day)
        # some extra validation
        if month < 0 or month > 12:
            raise ValueError("'{}' is not a valid date".format(datestr))
        if day not in range(1, calendar.monthrange(year, month)[-1] + 1):
            raise ValueError("'{}' is not a valid date".format(datestr))
    else:
        raise ValueError("'{}' is not a valid date".format(datestr))

    return "{:04d}-{:02d}-{:02d}".format(int(year), int(month), int(day))


def fix_ids(data):
    """Replace all 'id' in data by '@id'.

    It seems that connexion converts '@id' to 'id'. 
    To make thing consistent for further processing, we revert this.
    This function can handle all kind of input data (full factoids but also single sources etc.)
    """
    if not '@id' in data and 'id' in data:
        data['@id'] = data.pop('id')
    if 'person' in data and not '@id' in data['person'] and 'id' in data['person']:
        data['person']['@id'] = data['person'].pop('id')
    if 'source' in data and not '@id' in data['source'] and 'id' in data['source']:
        data['source']['@id'] = data['source'].pop('id')
    if 'statements' in data:
        for stmt in data['statements']:
            if not '@id' in stmt and 'id' in stmt:
                stmt['@id'] = stmt.pop('id')
    return data
