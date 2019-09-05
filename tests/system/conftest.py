"""pytest fixtures for system tests.
"""


import sys

import pytest
from xprocess import ProcessStarter

# These values are used to automatically start a server for system tests
SERVER_NAME = "papilotte"
SERVER_PORT = "16165"
# Set this to False if you want to start the server by hand
AUTOSTART_SERVER = True


BASE_URL = "http://localhost:%s/api/" % SERVER_PORT

@pytest.fixture(scope="session")
def factoidsurl():
    "Return the base url for system tests agains factoids."
    return BASE_URL + "factoids"


@pytest.fixture(scope="session")
def personsurl():
    "Return the base url for system tests agains persons."
    return BASE_URL + "persons"


@pytest.fixture(scope="session")
def sourcesurl():
    "Return the base url for system tests agains sources."
    return BASE_URL + "sources"


@pytest.fixture(scope="session")
def statementsurl():
    "Return the base url for system tests agains statements."
    return BASE_URL + "statements"


@pytest.fixture(scope="session")
def mockserver(xprocess):
    """Start the server with mock connector for integration tests.
    """
    # Sometimes it comes in handy to run the server manually (eg. for debugging)
    # So we only start the server if it is not running

    if AUTOSTART_SERVER:

        class Starter(ProcessStarter):
            "Start a papilotte server to run tests against it."
            pattern = "Running on"
            args = [
                sys.executable,
                "-m",
                "papilotte",
                "run",
                "-p",
                "16165",
            ]  # , '--connector', 'papilotte.connectors.mock']

        xprocess.ensure(SERVER_NAME, Starter)

        yield

        xprocess.getinfo(SERVER_NAME).terminate()
    else:
        yield
