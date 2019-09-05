"""Utility function for the mock connector.
"""
import json
import os.path

from papilotte.connectors.mock import mockdata


def get_mockdata(mockdata_file=None):
    """Return a list of factoid dicts.

    If mockdata_file is set (what only makes sense for very special
    testing or demonstration purposes), mock data will be read
    from file. In all other cases mock data will be generated on the
    fly via the mockdata module.
    """
    mock_data = []
    if mockdata_file is None:
        generator = mockdata.generate_factoid()
        for _ in range(100):
            mock_data.append(next(generator))
    else:
        if os.path.isfile(mockdata_file):
            with open(mockdata_file) as file_:
                mock_data = json.load(file_)
        else:
            raise FileNotFoundError(
                "'Mockdata file '%s' does not exist!" % mockdata_file
            )
    return mock_data
