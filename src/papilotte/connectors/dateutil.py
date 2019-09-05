"""
connector.dateutil
~~~~~~~~~~~~~~~~~~

Utility function for dealing with (incomplete) dates.
"""
import calendar
import re

def parse_single_date(datestr, postquem=True):
    """Transform a single date (or part of a full date) into a ISO date.

    This function takes a string representing an (incomplete) date like
    yyyy-mm-dd or yyyy-mm or yyyy and
    converts it into another string representing a full date (yyy-mm-dd).

    So for example 1932-1 becomes 1932-01-01 or 1932-01-31 if postquem
    is set to False.

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
        if postquem:
            if month is None:
                month = '01'
            if day is None:
                day = '01'
        else: # antequem
            if month is None:
                month = 12
            if day is None:
                day = str(calendar.monthrange(int(year), int(month))[1])
    else:
        raise ValueError("'{}' is not a valid date".format(datestr))
    return '{}-{:02d}-{:02d}'.format(year, int(month), int(day))

def from_to_date(from_, to_):
    """Return a 2-element tuple of a date interval.

    This function transforms two strings representing dates into
    a tuple of strings representing the same date but with
    all elements (yyyy-mm-dd). This function is able to handle
    incomplete dates like yyyy or yyyy-mm.

    If only one value is used, the interval will guess the other value
    depending on the accuracy of the given date. So:

        from_to_date(1900, None)

    will return 1900-01-01, 1900-12-31.

    :param from_: The date of the terminus postquem. Can be set to None.
    :type from_: str or None
    :param to_: The date of the terminus antequem. Can be set to None.
    :type to: str or None
    :return: A tuple of two date strings like 2015-07-12, 2015-07-15
    :rtype: tuple of 2 strings
    :raises: ValueError if a date string cannot be interpreted as date.
    """
    if from_ is None and to_ is None:
        from_to = None, None
    elif from_ is not None and to_ is not None:
        from_to = parse_single_date(from_), parse_single_date(to_, False)
    elif from_ is not None and to_ is None:
        # (2019-03-19, None) becomes 2019-03-19, 2019-03-19
        # (2019-03, None becomes) 2019-03-01, 2019-03-31
        # (2019, None) becomes 2019-01-01, 2019-12-31
        from_to = parse_single_date(from_), parse_single_date(from_, False)
    else: # from_ is None, to_ is set
        from_to = parse_single_date(to_), parse_single_date(to_, False)
    return from_to
