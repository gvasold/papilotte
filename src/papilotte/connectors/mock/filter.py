"""This module provides a class for filtering factoid objects.
"""
from papilotte.connectors import dateutil
from papilotte.connectors.mock.mockdate import MockDate


def person_contains(person, filter_by):
    """Return True if `filter_by` is found in `person`.

    :param person: a person dict
    :type person: dict
    :param filter_by: the string to search for
    :type filter_by: str
    :return: True if filter_by was found in person
    :rtype: bool
    """
    found = False
    if person is not None:
        if filter_by.lower() in person["@id"].lower():
            found = True
        elif filter_by in person.get("uris", []):
            found = True
    return found


def source_contains(source, filter_by):
    """Return True if `filter_by` is found in `source`.

    :param person: a source dict
    :type person: dict
    :param filter_by: the string to search for
    :type filter_by: str
    :return: True if filter_by was found in source
    :rtype: bool
    """
    found = False
    lc_filter_by = filter_by.lower()
    if source is not None:
        if lc_filter_by in source["@id"].lower():
            found = True
        elif lc_filter_by in source.get("label", "").lower():
            found = True
        elif filter_by in source.get("uris", []):
            found = True
    return found


def statement_contains(stmt, filter_by):
    """Return True if `filter_by` is found in statement `stmt`.

    :param person: a statement dict
    :type person: dict
    :param filter_by: the string to search for
    :type filter_by: str
    :return: True if filter_by was found in stmt
    :rtype: bool
    """

    found = False
    lc_filter_by = filter_by.lower()
    if stmt is not None:
        if lc_filter_by in stmt["@id"].lower():
            found = True
        elif filter_by == stmt.get("uri", ""):
            found = True
        elif labeled_uri_contains(stmt.get("statementType"), filter_by):
            found = True
        elif lc_filter_by in stmt.get("name", "").lower():
            found = True
        elif labeled_uri_contains(stmt.get("role"), filter_by):
            found = True
        elif date_contains_str(stmt.get("date"), filter_by):
            found = True
        elif labeled_uri_list_contains(stmt.get("places"), filter_by):
            found = True
        elif labeled_uri_list_contains(stmt.get("relatesToPersons"), filter_by):
            found = True
        elif labeled_uri_contains(stmt.get("memberOf"), filter_by):
            found = True
        elif lc_filter_by in stmt.get("statementContent", "").lower():
            found = True
    return found


def labeled_uri_contains(data, filter_by):
    """Return True if filter_by is found in the 2-property dict data.

    :param data: the dict to search in. Dict has two properties: label and uri.
                    Both labels can be missing or data can be None.
    :type data: dict
    :param filter_by: the string to search for
    :type filter_by: str
    :return: bool
    """
    found = False
    if data is not None:
        label = data.get("label", "")
        uri = data.get("uri", "")
        if filter_by.lower() in label.lower():
            found = True
        elif uri == filter_by:
            found = True
    return found


def labeled_uri_list_contains(data, filter_by):
    """Return True if filter_by is in the the list of 2-property dict data.

    :param data: A list of dicts to search in. Each dict has two properties:
                 label and uri.
                 Both labels can be missing or data can be None.
    :type data: list
    :param filter_by: the string to search for
    :type filter_by: str
    :return: bool
    """
    if data is not None:
        for element in data:
            if labeled_uri_contains(element, filter_by):
                return True
    return False


def date_contains_str(data, filter_by):
    """Return True if filter_by is found in the 2-property dict data.

    :param data: the dict to search in. Dict has two properties: label and sortdate.
                    Each can be missing or data can be None.
    :type data: dict
    :param filter_by: the string to search for
    :type filter_by: str
    :return: bool
    """
    found = False
    if data is not None:
        label = data.get("label", "")
        sortdate = data.get("sortdate", "")
        if filter_by.lower() in label.lower():
            found = True
        elif filter_by in sortdate:
            found = True
    return found


def date_is_equal_or_after(data, from_):
    """Return True if data['sortdate'] is not before from_.

    :param data: the dict to search in. Dict has two properties: label and sortdate.
                    Each can be missing or data can be None.
    :type data: dict
    :param from_: a MockDate object representing the filter_by date
                  If sortdate == from_ ist will also return True.
    :type from_: MockDate
    :return: bool
    """
    found = False
    if data is not None:
        sortdate = data.get("sortdate")
        if sortdate is not None:
            sortmockdate = MockDate(dateutil.parse_single_date(sortdate))
            if sortmockdate >= from_:
                found = True
    return found


def date_is_equal_or_before(data, to_):
    """Return True if data['sortdate'] is not after to_.

    :param data: the dict to search in. Dict has two properties: label and sortdate.
                    Each can be missing or data can be None.
    :type data: dict
    :param to_: a MockDate object representing the terminus antequem
    :type to_: MockDate
    :return: bool
    """
    found = False
    if data is not None:
        sortdate = data.get("sortdate")
        if sortdate is not None:
            sortmockdate = MockDate(dateutil.parse_single_date(sortdate, False))
            if sortmockdate <= to_:
                found = True
    return found


class Filter:
    """Filter class for factoid lists.

    This class provides a method filter(factoids, **filters),
    which applies all filters of **filters.

    We use a class here to avoid the module.getattr()-hack.
    """

    # Map parameter names to filter functions
    # Any mapping not defined here will lead to a KeyError
    FILTER_FUNCTIONS = {
        "factoidId": "filter_by_f_id",
        "statementId": "filter_by_st_id",
        "sourceId": "filter_by_s_id",
        "personId": "filter_by_p_id",
        "p": "filter_by_person",
        "f": "filter_by_factoid",
        "s": "filter_by_source",
        "st": "filter_by_statement",
        "statementContent": "filter_by_stmt_content",
        "relatesToPerson": "filter_by_relates_to_person",
        "memberOf": "filter_by_member_of",
        "role": "filter_by_role",
        "name": "filter_by_name",
        "place": "filter_by_place",
        "from_": "filter_by_from",
        "to_": "filter_by_to",
    }

    @classmethod
    def filter(cls, factoids, **filters):
        """Return a filtered version of factoids.

        This method calls a filter function for each filter parameter
        provided via filters.
        :param factoids: A list of factoid objects
        :type factoids: list
        :param filters: A dictionary of filter parameters an their values.
        :type filters: dict
        :return: A list of factoids
        :rtype: list
        :raises: KeyError
        """
        for filter_param in filters:
            function_name = cls.FILTER_FUNCTIONS[filter_param]
            function = getattr(cls, function_name)
            factoids = function(factoids, filters[filter_param])
        return factoids

    @classmethod
    def filter_by_f_id(cls, factoids, filter_by):
        """Return factoids filtered by f_id (factoid.id).

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: the f_id to filter by
        :return: A (filtered) list of factoids
        :rtype: list
        """
        return [factoid for factoid in factoids if factoid["@id"] == filter_by]

    @classmethod
    def filter_by_s_id(cls, factoids, filter_by):
        """Return factoids filtered by s_id (source.id).

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: the s_id to filter by
        :return: A (filtered) list of factoids
        :rtype: list
        """
        return [
            factoid for factoid in factoids if factoid["source"]["@id"] == filter_by
        ]

    @classmethod
    def filter_by_st_id(cls, factoids, filter_by):
        """Return factoids filtered by st_id (statement.id).

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: the st_id to filter by
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        for factoid in factoids:
            if factoid['statement']["@id"] == filter_by:
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_p_id(cls, factoids, filter_by):
        """Return factoids filtered by p_id (person.id).

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: the p_id to filter by
        :return: A (filtered) list of factoids
        :rtype: list
        """
        return [
            factoid for factoid in factoids if factoid["person"]["@id"] == filter_by
        ]

    @classmethod
    def filter_by_person(cls, factoids, filter_by):
        """Return factoids filtered substring in all elements of person.

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in all elements of
            persons
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        for factoid in factoids:
            if person_contains(factoid["person"], filter_by):
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_source(cls, factoids, filter_by):
        """Return factoids filtered substring in all elements of source.

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in all elements of
            source
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        for factoid in factoids:
            if source_contains(factoid["source"], filter_by):
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_statement(cls, factoids, filter_by):
        """Return factoids filtered in all elements of statement.

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in all elements of
            statement
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        # lc_filter_by = filter_by.lower()
        for factoid in factoids:
            if statement_contains(factoid['statement'], filter_by):
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_stmt_content(cls, factoids, filter_by):
        """Return factoids filtered substring in statement_contents.

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in statementContents
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        lc_filter_by = filter_by.lower()
        for factoid in factoids:
            stmt = factoid["statement"]
            if lc_filter_by in stmt.get("statementContent", "").lower():
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_relates_to_person(cls, factoids, filter_by):
        """Return factoids filtered substring in relatesToPerson.

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in relatesToPerson
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        for factoid in factoids:
            stmt = factoid["statement"]
            if labeled_uri_list_contains(stmt.get("relatesToPersons"), filter_by):
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_member_of(cls, factoids, filter_by):
        """Return factoids filtered substring in memberOf.

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in memberOf
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        for factoid in factoids:
            stmt = factoid["statement"]
            if labeled_uri_contains(stmt.get("memberOf"), filter_by):
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_role(cls, factoids, filter_by):
        """Return factoids filtered substring in role.

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in role
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        for factoid in factoids:
            stmt = factoid["statement"]
            if labeled_uri_contains(stmt.get("role"), filter_by):
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_place(cls, factoids, filter_by):
        """Return factoids filtered substring in place.

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in place
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        for factoid in factoids:
            stmt = factoid["statement"]
            if labeled_uri_list_contains(stmt["places"], filter_by):
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_name(cls, factoids, filter_by):
        """Return factoids filtered substring in name.

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in name
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        lc_filter_by = filter_by.lower()
        for factoid in factoids:
            stmt = factoid["statement"]
            if lc_filter_by in stmt.get("name", "").lower():
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_from(cls, factoids, filter_by):
        """Return factoids filtered by filter_by (terminus postquem).

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in date.from
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        from_ = MockDate(dateutil.parse_single_date(filter_by))
        for factoid in factoids:
            stmt = factoid["statement"]
            if date_is_equal_or_after(stmt.get("date"), from_):
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_to(cls, factoids, filter_by):
        """Return factoids filtered by filter_by (terminus antequem).

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in date.to
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        to_ = MockDate(dateutil.parse_single_date(filter_by, False))
        for factoid in factoids:
            stmt = factoid["statement"]
            if date_is_equal_or_before(stmt.get("date"), to_):
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def filter_by_factoid(cls, factoids, filter_by):
        """Return factoids filtered substring in all elements of factoids.

        :param factoids: A list of factoids
        :type factoids: list
        :param filter_by: A string to search for in all elements of
            factoids
        :return: A (filtered) list of factoids
        :rtype: list
        """
        matching_factoids = []
        lc_filter_by = filter_by.lower()
        for factoid in factoids:
            found = False
            if lc_filter_by in factoid["@id"].lower():
                found = True
            elif person_contains(factoid["person"], filter_by):
                found = True
            elif source_contains(factoid["source"], filter_by):
                found = True
            elif statement_contains(factoid['statement'], filter_by):
                found = True
            if found:
                matching_factoids.append(factoid)
        return matching_factoids

    @classmethod
    def _get_nested_value(cls, obj, path):
        """Use path (a/b/c) to get a nested value.

        Attention: This method does not (yet) support lists (only as
        return value, id est value of last path element)!

        :param obj: An (json) object as nested dicts.
        :type obj: dict
        :param path: A string specifying the path to the wanted value.
                 Single path elements are separated by '/'. This method
                 does not support lists (only as return value).
        :type path: str
        :return: The value of the path endpoint of None if one or more
                 path elements are missing.
        :raises: KeyError is raised is object contains a list at
            any position which is not the last one.
        """
        val = None
        path_elements = path.split("/")
        for i, key in enumerate(path_elements):
            # we have reached the last path element
            if i == len(path_elements) - 1:
                val = obj.get(key)
            else:
                obj = obj.get(key)
                if obj is None:
                    break
                elif not isinstance(obj, dict):
                    raise TypeError("Method does not support lists!")
        return val
