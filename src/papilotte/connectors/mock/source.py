"""Mock PersonConnector.

A SourceConntector object generates 100 full Factoids for mocking.
It overrides all methods from connectors.abstractconnector.
"""
from papilotte.connectors.abstractconnector import AbstractConnector
from papilotte.connectors.mock import util
from papilotte.connectors.mock.filter import Filter


class SourceConnector(AbstractConnector):
    """A Mock SourceConnector.

    The main purpose of this connector is testing and demonstration.

    # TODO: implement save()
    # TODO: implement update()
    # TODO: implement delete()
    """

    def __init__(self, options):
        "Generate mock data"
        super().__init__(options)
        self.options = options
        self.data = util.get_mockdata(options.get("mockdata_file"))

    def get(self, obj_id):
        """Return the object with id object_id or None.

        :param obj_id: the id of the object to return
        :type obj_id: string
        :return: The object as defined in the openAPI definition or None
        :rtype: dict
        """
        found = None
        for factoid in self.data:
            if factoid["source"]["@id"] == obj_id:
                found = factoid["source"]
                break
        return found

    def search(self, size, page, sort_by="createdWhen", **filters):
        """Find all objects which match the filter conditions set via
        filters.

        The filter conditions are defined in the openapi spec of
        the object.

        :param size: the number of results per page.
        :type size: int
        :param page: the number of the result page, starting with 1 (first page).
        :type page: int
        :param sort_by: the field the output should be sorted by. Default is 'createdWhen'.
                        It is suggegested to alway use '@id' as as second sort field, to
                        keep result order consistent for paging.
        :type sort_by: str
        :return: a list of source objects (represented as dictionaries)
        :rtype: list
        """
        # Filtering on factoids is a little arkward here, but I want to
        # have a single filter object to keep things simple
        factoids_found = Filter.filter(self.data, **filters)
        sources_found = self._extract_sources(factoids_found)
        # sort results
        sources_found.sort(key=lambda x: (x[sort_by], x["createdWhen"]))
        # paging
        first_result_of_page = (page - 1) * size
        last_result_of_page = (
            first_result_of_page + size
            if first_result_of_page + size <= len(sources_found)
            else len(sources_found)
        )
        return sources_found[first_result_of_page:last_result_of_page]

    def count(self, **filters):
        """Return the number of sources matching the filters.

        :param **filters: a **kwargs containing any number of filter parameters
        :type **filters: dict
        :return: the number of sources found
        :rtype: int
        """
        sources_found = []
        factoids_found = Filter.filter(self.data, **filters)
        sources_found = self._extract_sources(factoids_found)
        return len(sources_found)

    def save(self, data):
        """Return
        TODO: implement

        This method MAY be overriden by any custom implementation
        It MUST be overriden for any implementation of compliance level 3.

        :raises: TODO: a generic db excption?
        """
        raise NotImplementedError(
            "save is yet not implemented for mock connector source"
        )

    #     # As it's a mock we do not save anything.
    #     # TODO: think about if metadata enrichment should be done
    #     #   here or in the api code (preferably api code?)
    #     # FIXME: implement if level 1 is completed
    #     data['@id'] = uuid.uuid1().hex
    #     return data

    def update(self, obj_id, data):
        """
        # FIXME: implement if level 1 is completed
        Update an existing object specified by obj_id.

        This method MAY be overriden by any custom implementation
        It MUST be overriden for any implementation of compliance level 3.

        :raises: NotImplementedError
        """
        raise NotImplementedError(
            "save is yet not implemented for mock connector source"
        )

    def delete(self, obj_id):
        """
        TODO: implement
        """
        raise NotImplementedError(
            "save is yet not implemented for mock connector source"
        )

    @classmethod
    def _extract_sources(cls, factoids):
        """Return a distinct list of sources from all factoids in factoids.

        :param factoids: a list of factoid dicts
        :type factoid: list
        :return: a distinct list of sources contained in factoids
        :rtype: list
        """
        sources_found = []
        # we are only interested in distinct source objects
        existing_ids = []  # it's faster to compare ids than full dicts
        for factoid in factoids:
            if not factoid["source"]["@id"] in existing_ids:
                sources_found.append(factoid["source"])
                existing_ids.append(factoid["source"]["@id"])
        return sources_found
