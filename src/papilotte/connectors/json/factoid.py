"""A FactoidConnector for connectors.json.
"""
from papilotte.connectors import mock
from papilotte.connectors.json.reader import read_json_file


class FactoidConnector(mock.FactoidConnector):
    """A factoid connector which reads data from a json file.

    This connector only supports compliance levels 1 and 2.
    """

    # This connectors is very similar to the mock connector, that's
    # why we can use most of the methods from there.

    def __init__(self, options):
        super().__init__(options)
        self.data = read_json_file(options.get("json_file"), options["contact"])

    def save(self, data):
        "Creating a new factoid is not supported."
        msg = "papille.connectors.json does not support creating factoids"
        raise NotImplementedError(msg)

    def update(self, obj_id, data):
        "Updating a factoid is not supported."

        msg = "papille.connectors.json does not support updating factoids"
        raise NotImplementedError(msg)

    def delete(self, obj_id):
        "Deleting a factoid is not supported."
        msg = "papille.connectors.json does not support deleting factoids"
        raise NotImplementedError(msg)
