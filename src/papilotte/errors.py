class DeletionError(Exception):
    "Thrown by connectors if deletion of a resource fails."
    pass

class ConfigurationError(Exception):
    "Thrown if bad configuration values are detected."
    pass