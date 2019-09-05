"""Mock PersonConnector.
"""
from papilotte.connectors.abstractconnector import AbstractConnector
from papilotte.connectors.mock import util
from papilotte.connectors.mock.filter import Filter


class PersonConnector(AbstractConnector):
    """A Mock PersonConnector.

    The main purpose of this connector is testing and demonstration.

    # TODO: implement save()
    # TODO: implement update()
    # TODO: implement delete()
    """

    def __init__(self, options):
        super().__init__(options)
        self.data = util.get_mockdata(options.get('mockdata_file'))

    def get(self, obj_id):
        """Return the person dict with id person_id or None.

        :param object_id: the id of the person object to return
        :type object_id: string
        :return: The object as defined in the openAPI definition or None
        :rtype: dict
        """
        found = None
        for factoid in self.data:
            if factoid['person']['@id'] == obj_id:
                found = factoid['person']
                break
        return found

    def search(self, size, page, sort_by='createdWhen', **filters):
        """Find all objects which match the filter conditions set via
        filters.

        The filter conditions are defined in the openapi spec of
        person.

        :param size: the number of results per page.
        :type size: int
        :param page: the number of the result page, starting with 1 (first page).
        :type page: int
        :param sort_by: the field the output should be sorted by. Default is 'createdWhen'.
                        It is suggegested to alway use '@id' as as second sort field, to
                        keep result order consistent for paging.
        :type sort_by: str
        :return: a list of person objects (represented as dictionaries)
        :rtype: list
        """
        # Filtering on factoids is a little arkward here, but I want to
        # have a single filter object to keep things simple.
        factoids_found = Filter.filter(self.data, **filters)
        persons_found = self._extract_persons(factoids_found)
        # sort results
        persons_found.sort(key=lambda x: (x[sort_by], x['createdWhen']))
        # paging
        first_result_of_page = (page - 1) * size
        last_result_of_page = first_result_of_page + size if \
                first_result_of_page + size <= len(persons_found) else len(persons_found)
        return persons_found[first_result_of_page:last_result_of_page]

    def count(self, **filters):
        """Return the number of persons matching the filters.
        :param **filters: a **kwargs containing any number of filter parameters
        :type **filters: dict
        :return: the number of persons found
        :rtype: int
        """
        persons_found = []
        factoids_found = Filter.filter(self.data, **filters)
        persons_found = self._extract_persons(factoids_found)
        return len(persons_found)


    def save(self, data):
        """Return
        TODO: implement

        This method MAY be overriden by any custom implementation
        It MUST be overriden for any implementation of compliance level 3.

        :raises: TODO: a generic db excption?
        """
        raise NotImplementedError('save is yet not implemented for mock connector persons')
    #     # As it's a mock we do not save anything.
    #     # TODO: think about if metadata enrichment should be done
    #     #   here or in the api code (preferably api code?)
    #     data['id'] = uuid.uuid1().hex
    #     return data

    def update(self, obj_id, data):
        """
        Update an existing object specified by object_id.

        TODO: implement

        This method MAY be overriden by any custom implementation
        It MUST be overriden for any implementation of compliance level 3.

        :raises: NotImplementedError
        """
        raise NotImplementedError('update is yet not implemented for mock connector persons')


    def delete(self, obj_id):
        """
        Update an existing object specified by object_id.

        TODO: implement

        This method MAY be overriden by any custom implementation
        It MUST be overriden for any implementation of compliance level 3.

        :raises: NotImplementedError
        """
        raise NotImplementedError('update is yet not implemented for mock connector persons')


    @classmethod
    def _extract_persons(cls, factoids):
        """Return a distinct list of persons from all factoids in factoids.

        :param factoids: a list of factoid dicts
        :type factoid: list
        :return: a distinct list of persons contained in factoids
        :rtype: list
        """
        persons_found = []
        # we are only interested in distinct person objects
        existing_ids = []  # it's faster to compare ids than full dicts
        for factoid in factoids:
            if not factoid['person']['@id'] in existing_ids:
                persons_found.append(factoid['person'])
                existing_ids.append(factoid['person']['@id'])
        return persons_found
