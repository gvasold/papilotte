"""Mock PersonConnector.
"""
#import uuid

from papilotte.connectors.abstractconnector import AbstractConnector
from papilotte.connectors.mock import util
from papilotte.connectors.mock.filter import Filter

class FactoidConnector(AbstractConnector):
    """A mock factoid connector.

    The main purpose of this connector is testing and demonstration.

    # TODO: implement save()
    # TODO: implement update()
    # TODO: implement delete()
    """

    def __init__(self, options):
        super().__init__(options)
        self.data = util.get_mockdata()

    def get(self, obj_id):
        """Return the object with id object_id or None.

        :param obj_id: the id of the object to return
        :type obj_id: string
        :return: The object as defined in the openAPI definition
        :rtype: dict
        """
        found = None
        for factoid in self.data:
            if factoid["@id"] == obj_id:
                found = factoid
                break
        return found

    def search(self, size, page, sort_by='createdWhen', **filters):
        """Find all factoids which match the filter conditions set via
        filters.

        The filter conditions are defined in the openapi spec of
        the object.

        TODO
        :rtype: List of ???
        TODO: Abklaeren: wonach soll da noch sortiert werden??
        Macht es Sinn, nach Feldern zu sortieren, die im output gar
        nicht vorkommen?
        """
        result = Filter.filter(self.data, **filters)
        #result.sort(key=lambda x: (x["createdWhen"], int(x['@id'].split()[-1])))
        result.sort(key=lambda x: (x["createdWhen"], x['@id']))
        first_result = (page - 1) * size
        last_result = (
            first_result + size if first_result + size <= len(result) else len(result)
        )
        return result[first_result:last_result]

    def count(self, **filters):
        """Return number of factoid objects matching filter conditions.

        If no filter conditions are provided, count() will return the
        number of all object available.

        The filter conditions are defined in the openapi definition of
        the object.

        :param **filters: Filter conditions as described in the openapi
                          spec.
        :return: The number of objects matching the filter conditions
        :rtype: int
        """
        result = Filter.filter(self.data, **filters)
        return len(result)

    def save(self, data):
        """Return
        TODO: implement
        This method MAY be overriden by any custom implementation
        It MUST be overriden for any implementation of compliance level 3.

        :raises: TODO: a generic db excption?
        """
        raise NotImplementedError('save is yet not implemented for mock connector factoids.')
    #     # As it's a mock we do not save anything.
    #     # TODO: think about if metadata enrichment should be done
    #     #   here or in the api code (preferably api code?)
    #     data["id"] = uuid.uuid1().hex
    #     return data

    def update(self, obj_id, data):
        """
        TODO: implement
        Update an existing object specified by object_id.

        This method MAY be overriden by any custom implementation
        It MUST be overriden for any implementation of compliance level 3.

        :raises: NotImplementedError
        """
        raise NotImplementedError('update is yet not implemented for mock connector factoids')


    def delete(self, obj_id):
        """
        TODO: implement
        Update an existing object specified by object_id.

        This method MAY be overriden by any custom implementation
        It MUST be overriden for any implementation of compliance level 3.

        :raises: NotImplementedError
        """
        raise NotImplementedError('delete is yet not implemented for mock connector factoids')
