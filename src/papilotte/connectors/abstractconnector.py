"""Defines an abstract base class for all connectors.
"""


class AbstractConnector:
    """An abstract connector class.

    You must write your own Connector Class based this class, which
    overrides all methods.
    """

    def __init__(self, options):
        """Initilaize a Connector object.

        :param options: a dictionary containing the server configuration
        :type: dict
        """
        self.options = options
        if self.__class__ == "AbstractConnector":
            raise NotImplementedError(
                (
                    "AbstractConnector must not be used directly. "
                    "You have to write your own subclass."
                )
            )

    def get(self, obj_id):
        """Return the object with id obj_id.

        This method MUST be overriden by any custom implementation.

        :param obj_id: the id of the object to return
        :type obj_id: string
        :return: The object as defined in the openAPI definition
        :rtype: dict
        :raises: KeyError?? # TODO: use more suitable Exception?
        """
        raise NotImplementedError("Abstract method 'get' must be overriden!")

    def search(self, size, page, sort_by="createdWhen", **filters):
        """Find all objects that match the filter conditions set via
        filters.

        The method supports paging via size (entry per page) and
        page (start with page n).
        The filter conditions are defined in the openapi specof the
        object.

        :param size: Number of results per page
        :type size: int
        :param page: the page number to return
        :type page: int
        :param sort_by: the field name used to sort the result to keep paging consistent
                  default value is 'createdWhen', but allowed is any field name contained
                  in the response objects.
        :type sort_by: str
        :param **filters: **kwargs for filter parameter and values
        :type filters: dict
        :return: a list of matching objects. May be empty.
        :rtype: list
        """
        raise NotImplementedError("Abstract method 'find' must be overriden!")

    def count(self, **filters):
        """Return number of objects matching filter conditions.

        If no filter conditions are provided, count() will return the
        number of all object available.

        The filter conditions are defined in the openapi definition of
        the object.

        :param **filters: Filter conditions as described in the openapi
                          spec.
        :return: The number of objects matching the filter conditions
        :rtype: int
        """
        raise NotImplementedError("Abstract method 'count' must be overriden!")

    def save(self, data):
        """Return

        This method MAY be overriden by a custom implementation.
        It MUST be overriden for any implementation of compliance level 3.

        :raises: TODO: a generic db excption?
        """
        raise NotImplementedError(
            (
                "Abstract method 'save' must be overrriden to comply with "
                "compliance level 3!"
            )
        )

    def update(self, obj_id, data):
        """
        Update an existing object specified by object_id.

        This method MAY be overriden by a custom implementation.
        It MUST be overriden for any implementation of compliance level 3.

        :raises: NotImplementedError
        """
        raise NotImplementedError(
            (
                "Abstract method 'update' must be overrriden to comply with"
                "compliance level 3!"
            )
        )

    def delete(self, obj_id):
        """Delete an exsting object specified by object_id.

        This method MAY be overriden by a custom implementation.
        It MUST be overriden for any implementation of compliance level 3.

        This methods takes care of reference integrity.

        :param obj_id: the id of the object to delete
        """
        raise NotImplementedError(
            (
                "Abstract method 'delete' must be overrriden to comply with"
                "compliance level 3!"
            )
        )
