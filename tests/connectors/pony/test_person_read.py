"""Tests for papilotte.connectors.pony.person.
"""
import copy
import datetime

import pytest

from pony import orm

from papilotte.connectors.pony import person

@pytest.fixture()
def db10cfg_identical_persons(mockcfg):
    """Return a cfg dict containing a db prepopulated with 10 nearly identical persons
    The only difference is id. This is only used for testing the (implicit) second search field.
    """
    Person = mockcfg["db"].entities["Person"]
    with orm.db_session():
        for i in range(1, 101):
            data = {
                "@id": "P{:03d}".format(11 - i),
                "createdBy": "Creator 1",
                "createdWhen": datetime.datetime(2015, 1, 1).isoformat(),
                "modifiedBy": "Modifier 1",
                "modifiedWhen": datetime.datetime(2015, 1, 2).isoformat(),
                "uris": [
                    "https://example.com/persons/1",
                    "https://example.com/persons/2",
                ],
            }
            Person.create_from_ipif(data)
    yield mockcfg


def test_get(db200final_cfg):
    "Test the connector get method for a single person."
    connector = person.PersonConnector(db200final_cfg)
    pers = connector.get('P00001')
    assert pers['@id'] == 'P00001'
    assert pers['createdBy'] == 'Creator 00001'
    assert pers['createdWhen'] == '2003-02-15T00:03:00'
    assert pers['modifiedBy'] == 'Modifier 00001'
    assert pers['modifiedWhen'] == '2003-02-15T00:06:00'
    assert pers['uris'] == ['https://example.com/persons/1a']
    assert pers['factoid-refs'][0]['@id'] == 'F00075' 
    assert pers['factoid-refs'][0]['source-ref']['@id'] == 'S00076'
    assert pers['factoid-refs'][0]['person-ref']['@id'] == 'P00001'
    assert pers['factoid-refs'][0]['statement-refs'][0]['@id'] == 'Stmt00225'

    assert pers['factoid-refs'][1]['@id'] == 'F00150' 
    assert pers['factoid-refs'][1]['source-ref']['@id'] == 'S00051'
    assert pers['factoid-refs'][1]['person-ref']['@id'] == 'P00001'
    assert pers['factoid-refs'][1]['statement-refs'][0]['@id'] == 'Stmt00450'

def test_get_with_uri(db200final_cfg):
    "Test the connector get method for a single person when using an uri instead of the id."
    connector = person.PersonConnector(db200final_cfg)
    pers = connector.get('https://example.com/persons/2a')
    assert pers['@id'] == 'P00002'
    pers = connector.get('https://example.com/persons/2b')
    assert pers['@id'] == 'P00002'

def test_search_paging(db200final_cfg):
    "Test paging for search() without filtering."
    connector = person.PersonConnector(db200final_cfg)
    result = connector.search(size=30, page=1)
    assert len(result) == 30

    result = connector.search(size=30, page=2)
    assert len(result) == 30

    # Make sure all remaining persons are returned if size > number of pages
    result = connector.search(size=300, page=1)
    assert len(result) == 75
    
    # make sure accessing objects outside range does return an empty list
    result = connector.search(size=200, page=2)
    assert result == []


def test_search_sorting(db200final_cfg):
    "Test if sort_by parameter works."
    connector = person.PersonConnector(db200final_cfg)

    # default sort_by is 'createdWhen'
    result = connector.search(size=10, page=1)
    sort_fields = [p["createdWhen"] for p in result]
    assert sort_fields == sorted(sort_fields)

    # I've ommitted uris here, because ist doen not make much sense
    for fieldname in ("@id", "createdBy", "createdWhen", "modifiedBy", "modifiedWhen"):
        result = connector.search(size=10, page=1, sort_by=fieldname)
        sort_fields = [p[fieldname] for p in result]
        assert sort_fields == sorted(
            sort_fields
        ), "sorting for {} does not work".format(fieldname)

        result = connector.search(size=10, page=1, sort_by=fieldname, sort_order="ASC")
        sort_fields = [p[fieldname] for p in result]
        assert sort_fields == sorted(
            sort_fields
        ), "sorting for {} does not work".format(fieldname)

        result = connector.search(size=10, page=1, sort_by=fieldname, sort_order="DESC")
        sort_fields = [p[fieldname] for p in result]
        assert sort_fields == sorted(
            sort_fields, reverse=True
        ), "sorting for {} does not work".format(fieldname)

def test_search_sorting_second_value(db10cfg_identical_persons):
    "If sortBy values are identical use id as secondary sort value."
    connector = person.PersonConnector(db10cfg_identical_persons)
    result = connector.search(size=10, page=1, sort_by="createdWhen")
    sort_fields = [(p["createdWhen"], p["@id"]) for p in result]
    assert sort_fields == sorted(sort_fields)


def test_count(db200final_cfg):
    "Test the connectors count method."
    conector = person.PersonConnector(db200final_cfg)
    assert conector.count() == 75


def test_get_factoid_refs(db200final_cfg):
    connector = person.PersonConnector(db200final_cfg)
    p = connector.get('P00002')
    refs = p['factoid-refs']
    assert len(refs) == 3

    assert refs[0]['@id'] == 'F00001'
    assert refs[0]['source-ref']['@id'] == 'S00002'
    assert refs[0]['person-ref']['@id'] == 'P00002'
    assert refs[0]['statement-refs'][0]['@id'] == 'Stmt00001'

    assert refs[1]['@id'] == 'F00076'
    assert refs[1]['source-ref']['@id'] == 'S00077'
    assert refs[1]['person-ref']['@id'] == 'P00002'
    assert refs[1]['statement-refs'][0]['@id'] == 'Stmt00226'

    assert refs[2]['@id'] == 'F00151'
    assert refs[2]['source-ref']['@id'] == 'S00052'
    assert refs[2]['person-ref']['@id'] == 'P00002'
    assert refs[2]['statement-refs'][0]['@id'] == 'Stmt00451'

    
