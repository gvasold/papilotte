import json
import os
import pytest
import tempfile
from papilotte.connectors.pony import database
from papilotte import mockdata
from pony import orm
from papilotte.mockdata import make_factoids

@pytest.fixture
def db():
    "Return an empty database."
    return database.make_db()


@pytest.fixture
def mockcfg():
    "Return a minimal configuration with an empty database."
    return {"db": database.make_db()}

@pytest.fixture(scope="session")
def db200final():
    """Provides a on-disk database with 200 factoids.

    This database MUST NOT be modified during tests!
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
        yield db

@pytest.fixture(scope="session")
def db200final_cfg(db200final):
    """Return a configuration dict (as needed by pony.person etc.)
    containing a database with with 200 factids.
    Do not write to this database (select queries only)
    """
    return {"db": db200final}

