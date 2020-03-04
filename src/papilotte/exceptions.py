

class ConfigurationError(Exception):
    pass

class APIException(Exception):
    "A generic exception type for the PAPI API."

class DeletionError(APIException):
    "Thrown by connectors if deletion of a resource fails."
    pass

class ReferentialIntegrityError(DeletionError):
    """Thrown if an object cannot be deleted because of referential integrity.
    """
    pass

class CreationException(APIException):
    """Must be raised for any Exception during creation of an object.
    """

class InvalidIdError(APIException):
    "Will be raise if an id contains a charachter not allowed in RFC3986#section-2.3."
    pass