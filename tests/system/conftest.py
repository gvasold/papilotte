"""pytest fixtures for system tests.
"""


import sys

import pytest
import toml
import copy
import json
import os
import tempfile
from papilotte import server, configuration
from papilotte.connectors.pony import database
from pony import orm
from papilotte import mockdata

BASE_URL = "/api/" 


# A basic configuration for testing
BASE_CFG = {
    'server': {
        'connector': "papilotte.connectors.pony",
        'host': "localhost",
        'port': 5000,
        'responseValidation': False,  # FIXME: set to true if api reflect the new schemas
        'debug': True
    },
    'logging': {
        'logLevel': "info",
        'logTo': "console"
    },
    'api': {
        'complianceLevel': 2,
        'basePath': "/api",
        'maxSize': 800
    },
    'metadata': {
        'contact': "MockContact",
        'provider': "MockProvider",
        'description': "MockDescription"
    },
    'connector': {
        'provider': "sqlite",
        'filename': "/tmp/x.db"
    }
}

@pytest.fixture
def person1():
    "Return person with id 'P00001' from test data as dict"
    for factoid in mockdata.make_factoids(200):
        if factoid["person"]["@id"] == "P00001":
            return factoid['person']

@pytest.fixture
def source1():
    "Return source with id 'S00001' from test data as dict"
    for factoid in mockdata.make_factoids(200):
        if factoid["source"]["@id"] == "S00001":
            return factoid['source']

@pytest.fixture
def statement1():
    "Return statement with id Stmt00001 from test data as dict"
    for factoid in mockdata.make_factoids(200):
        for stmt in factoid['statements']:
            if stmt["@id"] == "Stmt00001":
                return stmt

@pytest.fixture
def factoid1():
    "Return factoid with id F00001 from test data as dict."
    for factoid in mockdata.make_factoids(200):
        if factoid['@id'] == 'F00001':
            return factoid

@pytest.fixture(scope='module')
def db200_static_file():
    """Generate a pre-populated read only database with 200 factoids.

    The database lives in a temporary directory.
    Return the path to the sqlite dabase file.
    """
    with tempfile.TemporaryDirectory() as tmp_path:
        dbfile = os.path.join(tmp_path, 'test.db')
        db = database.make_db(provider='sqlite', filename=dbfile)
        Factoid = db.entities['Factoid']
        with orm.db_session: 
            for factoid in mockdata.make_factoids(200):
                Factoid.create_from_ipif(factoid)
            db.commit()
            conn = db.get_connection()
            conn.execute("PRAGMA query_only = ON")
        yield dbfile

@pytest.fixture
def db20_file():
    """Generate a pre-populated database with 20 factoids.
    This database can be used to test modifying access to objects.

    The database lives in a temporary directory.
    Return the path to the sqlite dabase file.
    """
    with tempfile.TemporaryDirectory() as tmp_path:
        dbfile = os.path.join(tmp_path, 'test.db')
        db = database.make_db(provider='sqlite', filename=dbfile)
        Factoid = db.entities['Factoid']
        with orm.db_session: 
            for factoid in mockdata.make_factoids(20):
                Factoid.create_from_ipif(factoid)
        yield dbfile


@pytest.fixture(scope='module')
def cfgfile_cl0(db200_static_file):
    """Return path to configfile for compliance level 0.

    This fixture not only configures the server, but also
    creates a static mock database with 200 factoids in the temporary
    directory where the configfile is written to.
    """
    import shutil
    fname = os.path.dirname(db200_static_file).split('/')[-1] + '.db'
    shutil.copy(db200_static_file, '/tmp/' + fname)
    cfg = copy.deepcopy(BASE_CFG)
    cfgfile = os.path.join(os.path.dirname(db200_static_file), 'papi.toml')
    cfg['connector']['filename'] = db200_static_file
    cfg['api']['complianceLevel'] = 0
    with open(cfgfile, 'w') as fh:
        fh.write(toml.dumps(cfg))
        fh.flush()
    yield cfgfile

@pytest.fixture(scope="module")
def cfgfile_cl1(db200_static_file):
    """Return path to configfile for compliance level 1.

    This fixture not only configures the server, but also
    creates a mock database with 200 factoids in the temporary
    directory where the configfile is written to.

    As compliance level 1 is read only by default, we can set scope to session.
    """
    cfg = copy.deepcopy(BASE_CFG)
    cfgfile = os.path.join(os.path.dirname(db200_static_file), 'papi.toml')
    cfg['connector']['filename'] = db200_static_file
    cfg['api']['complianceLevel'] = 1
    with open(cfgfile, 'w') as fh:
        fh.write(toml.dumps(cfg))
        fh.flush()
    yield cfgfile

@pytest.fixture
def cfgfile_cl2(db20_file):
    """Return path to configfilei for compliance level 2.

    This fixture not only configures the server, but also
    creates a mock database with 20 factoids in the temporary
    directory where the configfile is written to.
    """
    cfg = copy.deepcopy(BASE_CFG)
    cfgfile = os.path.join(os.path.dirname(db20_file), 'papi.toml')
    cfg['connector']['filename'] = db20_file
    cfg['api']['complianceLevel'] = 2
    with open(cfgfile, 'w') as fh:
        fh.write(toml.dumps(cfg))
        fh.flush()
    yield cfgfile

@pytest.fixture(scope='module')
def mockclient_cl0(cfgfile_cl0):
    """Return a test client for a complianceLevel 0 server.
    The server has a database with 200 mock factoids.
    
    As compliance level 0 is read only by default, we can set scope to session.
    """
    app = server.create_app(cfgfile_cl0)
    with app.app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def mockclient_cl1(cfgfile_cl1):
    """Return a test client for a complianceLevel 0 server.
    The server has a database with 200 mock factoids.

    As compliance level 1 is read only by default, we can set scope to session.
    """
    app = server.create_app(cfgfile_cl1)
    with app.app.test_client() as client:
        yield client

@pytest.fixture
def mockclient_cl2(cfgfile_cl2):
    """Return a test client for a complianceLevel 0 server.
    The server has a database with 20 mock factoids.
    """
    app = server.create_app(cfgfile_cl2)
    with app.app.test_client() as client:
        yield client
