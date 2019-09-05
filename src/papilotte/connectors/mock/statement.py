"""Mock PersonConnector.
"""
from papilotte.connectors.abstractconnector import AbstractConnector
from papilotte.connectors.mock import util
from papilotte.connectors.mock.filter import Filter

class StatementConnector(AbstractConnector):
    """A mock statement connector.

    The main purpose of this connector is testing and demonstration.

    # TODO: implement save()
    # TODO: implement update()
    # TODO: implement delete()
    """

    def __init__(self, options):
        super().__init__(options)
        self.data = util.get_mockdata(options.get('mockdata_file'))

    def get(self, obj_id):
        """Return the statement with id statement_id or None.

        :param statement_id: the id of the statement to return
        :type statement_id: string
        :return: The statement as defined in the openAPI definition or None
        :rtype: dict
        """
        found = None
        for factoid in self.data:
            if factoid['statement']['@id'] == obj_id:
                found = factoid['statement']
        return found

    def search(self, size, page, sort_by='createdWhen', **filters):
        """Find all statements which match the filter conditions set via
        filters.

        The filter conditions are defined in the openapi spec of
        statement.

        :param size: the number of results per page.
        :type size: int
        :param page: the number of the result page, starting with 1 (first page).
        :type page: int
        :param sort_by: the field the output should be sorted by. Default is 'createdWhen'.
                        It is suggegested to alway use '@id' as as second sort field, to
                        keep result order consistent for paging.
        :type sort_by: str
        :return: a list of statement objects (represented as dictionaries)
        :rtype: list
        """
        # Filtering on factoids is a little arkward here, but I want to
        # have a single filter object to keep things simple
        factoids_found = Filter.filter(self.data, **filters)
        statements_found = self._extract_statements(factoids_found)
        # sort results
        statements_found.sort(key=lambda x: (x[sort_by], x['createdWhen']))
        # paging
        first_result_of_page = (page - 1) * size
        last_result_of_page = first_result_of_page + size if \
                first_result_of_page + size <= len(statements_found) else len(statements_found)
        return statements_found[first_result_of_page:last_result_of_page]



    def count(self, **filters):
        """Return the number of statements matching the filters.

        :param **filters: a **kwargs containing any number of filter parameters
        :type **filters: dict
        :return: the number of statements found
        :rtype: int
        """
        statements_found = []
        factoids_found = Filter.filter(self.data, **filters)
        statements_found = self._extract_statements(factoids_found)
        return len(statements_found)

    def save(self, data):
        """Return

        This method MAY be overriden by any custom implementation
        It MUST be overriden for any implementation of compliance level 3.

        TODO: implement

        :raises: TODO: a generic db excption?
        """
        raise NotImplementedError(
            "save is yet not implemented for mock connector statement"
        )
    #     # As it's a mock we do not save anything.
    #     # TODO: think about if metadata enrichment should be done
    #     #   here or in the api code (preferably api code?)
    #     data['id'] = uuid.uuid1().hex
    #     return data

    def update(self, obj_id, data):
        """
        Update an existing object specified by object_id.

        This method MAY be overriden by any custom implementation
        It MUST be overriden for any implementation of compliance level 3.

        TODO: implement

        :raises: NotImplementedError
        """
        raise NotImplementedError(
            "update is yet not implemented for mock connector statement"
        )

    def delete(self, obj_id):
        """
        TODO: implement
        """
        raise NotImplementedError(
            "delete is yet not implemented for mock connector statement"
        )

    @classmethod
    def _extract_statements(cls, factoids):
        """Return a distinct list of statements from all factoids in factoids.

        :param factoids: a list of factoid dicts
        :type factoid: list
        :return: a distinct list of statements contained in factoids
        :rtype: list
        """
        # statements are distinct by nature!
        statements_found = []
        for factoid in factoids:
            statements_found.append(factoid['statement'])
        return statements_found
