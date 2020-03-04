"""Tests for papilotte.connectors.pony.factoid
"""
import copy
import datetime

import pytest

from pony import orm

from papilotte.connectors.pony import factoid
@pytest.fixture()
def cfg_10_identical_factoids(mockcfg):
    """Return a cfg dict containing a db prepopulated with 10 nearly identical factoids
    The only difference is id.
    """
    Factoid = mockcfg["db"].entities["Factoid"]
    with orm.db_session():
        for i in range(1, 101):
            data = {
                "@id": "F{:03d}".format(11 - i),
                "createdBy": "Creator 1",
                "createdWhen": datetime.datetime(2015, 1, 1).isoformat(),
                "modifiedBy": "Modifier 1",
                "modifiedWhen": datetime.datetime(2015, 1, 2).isoformat(),
                "source": {'@id': 'Source 1'},
                "person": {'@id': 'Person 1'},
                "statements": [{'@id': 'Statement {:03d}'.format(i)}]
            }
            Factoid.create_from_ipif(data)
    yield mockcfg


def test_get(db200final_cfg):
    "Test the connector get method without filters."
    connector = factoid.FactoidConnector(db200final_cfg)
    factoid1 = connector.get('F00001')
    assert factoid1['@id'] == 'F00001'
    assert factoid1['createdBy'] == 'Creator 00001'
    assert factoid1['createdWhen'] == '2003-02-15T00:03:00'
    assert factoid1['modifiedBy'] == ''
    assert factoid1['modifiedWhen'] == ''
    assert factoid1['derivedFrom'] == ''

    assert factoid1['@id'] == 'F00001' 
    assert factoid1['source-ref']['@id'] == 'S00002'
    assert factoid1['person-ref']['@id'] == 'P00002'
    assert factoid1['statement-refs'][0]['@id'] == 'Stmt00001'
    assert factoid1['statement-refs'][1]['@id'] == 'Stmt00002'


def test_search_paging(db200final_cfg):
    "Test search() without filtering."
    connector = factoid.FactoidConnector(db200final_cfg)
    result = connector.search(size=30, page=1)
    assert len(result) == 30

    result = connector.search(size=30, page=2)
    assert len(result) == 30

    # Make sure all remaining sources are returned if size > number of pages
    result = connector.search(size=300, page=1)
    assert len(result) == 200
    
    # make sure accessing objects outside range does return an empty list
    result = connector.search(size=200, page=2)
    assert result == []

def test_search_sorting(db200final_cfg):
    "Test if sort_by parameter works."
    connector = factoid.FactoidConnector(db200final_cfg)

    # default sort_by is 'createdWhen'
    result = connector.search(size=10, page=1)
    sort_fields = [f["createdWhen"] for f in result]
    assert sort_fields == sorted(sort_fields)

    # I've ommitted uris here, because it does not make much sense
    for fieldname in ("@id", "createdBy", "createdWhen", "modifiedBy", "modifiedWhen"):
        result = connector.search(size=10, page=1, sort_by=fieldname)
        sort_fields = [f[fieldname] for f in result]
        assert sort_fields == sorted(
            sort_fields
        ), "sorting for {} does not work".format(fieldname)

        result = connector.search(size=10, page=1, sort_by=fieldname, sort_order="ASC")
        sort_fields = [f[fieldname] for f in result]
        assert sort_fields == sorted(
            sort_fields
        ), "sorting for {} does not work".format(fieldname)

        result = connector.search(size=10, page=1, sort_by=fieldname, sort_order="DESC")
        sort_fields = [f[fieldname] for f in result]
        assert sort_fields == sorted(
            sort_fields, reverse=True
        ), "sorting for {} does not work".format(fieldname)

def test_search_sorting_second_value(cfg_10_identical_factoids):
    "If sortBy values are identical use id as secondary sort value."
    connector = factoid.FactoidConnector(cfg_10_identical_factoids)
    cfg_10_identical_factoids
    result = connector.search(size=10, page=1, sort_by="createdWhen")
    sort_fields = [(f["createdWhen"], f["@id"]) for f in result]
    assert sort_fields == sorted(sort_fields)


def test_count(db200final_cfg):
    "Test the connectors count method."
    "Test the connectors count method."
    conector = factoid.FactoidConnector(db200final_cfg)
    assert conector.count() == 200

