"""Tests for papilotte.connectors.pony.source
"""
import copy
import datetime

import pytest

from pony import orm

from papilotte.connectors.pony import statement


@pytest.fixture
def cfg_10_identical_statements(mockcfg):
    """Return a cfg dict containing a db prepopulated with 10 nearly identical statements
    The only difference is id.
    """
    Statement = mockcfg["db"].entities["Statement"]
    with orm.db_session():
        for i in range(1, 101):
            data = {
                "@id": "S{:03d}".format(11 - i),
                "createdBy": "Creator 1",
                "createdWhen": datetime.datetime(2015, 1, 1).isoformat(),
                "modifiedBy": "Modifier 1",
                "modifiedWhen": datetime.datetime(2015, 1, 2).isoformat(),
                "uris": [
                    "https://example.com/statements/1",
                    "https://example.com/statements/2",
                ],
            }
            Statement.create_from_ipif(data)
    yield mockcfg


def test_get(db200final_cfg):
    "Test the connector get method without filters."
    connector = statement.StatementConnector(db200final_cfg)
    stmt = connector.get('Stmt00001')
    assert stmt['@id'] == 'Stmt00001'
    assert stmt['createdBy'] == 'Creator 00001'
    assert stmt['createdWhen'] == '2003-02-15T00:03:00'
    assert stmt['modifiedBy'] == ''
    assert stmt['modifiedWhen'] == ''
    assert stmt['name'] == 'Statement 00001'
    assert stmt['date']['sortDate'] == '1802-04-22'
    assert stmt['date']['label'] == 'Historical Date 00003'
    assert stmt['role']['uri'] == 'https://example.com/roles/00002'
    assert stmt['role']['label'] == 'Role 00002'
    assert stmt['statementContent'] == 'Statement content 00002'
    assert stmt['statementType']['uri'] == 'https://example.com/statementtypes/00002'
    assert stmt['statementType']['label'] == 'Statement type 00002'
    assert stmt['memberOf']['uri'] == 'https://example.com/groups/00002'
    assert stmt['memberOf']['label'] == 'Group 00002'
    assert stmt['uris'] == ['https://example.com/statements/1a']
    assert stmt['places'][0]['uri'] == 'https://example.com/places/00002'
    assert stmt['places'][0]['label'] == 'Place 00002'
    assert stmt['places'][1]['label'] == 'Place 00003'
    assert stmt['relatesToPersons'][0]['uri'] == 'https://example.com/relatedpersons/00002'
    assert stmt['relatesToPersons'][0]['label'] == 'Related person 00002'
    assert stmt['relatesToPersons'][1]['label'] == 'Related person 00003'

    assert stmt['factoid-refs'][0]['@id'] == 'F00001' 
    assert stmt['factoid-refs'][0]['source-ref']['@id'] == 'S00002'
    assert stmt['factoid-refs'][0]['person-ref']['@id'] == 'P00002'
    assert stmt['factoid-refs'][0]['statement-refs'][0]['@id'] == 'Stmt00001'
    assert stmt['factoid-refs'][0]['statement-refs'][1]['@id'] == 'Stmt00002'

def test_get_with_uri(db200final_cfg):
    "Test the connector get method for a single statement when using an uri instead of the id."
    connector = statement.StatementConnector(db200final_cfg)
    pers = connector.get('https://example.com/statements/2a')
    assert pers['@id'] == 'Stmt00002'
    pers = connector.get('https://example.com/statements/2b')
    assert pers['@id'] == 'Stmt00002'


def test_search_paging(db200final_cfg):
    "Test search() without filtering."
    connector = statement.StatementConnector(db200final_cfg)
    result = connector.search(size=30, page=1)
    assert len(result) == 30

    result = connector.search(size=30, page=2)
    assert len(result) == 30

    # Make sure all remaining sources are returned if size > number of pages
    result = connector.search(size=1000, page=1)
    assert len(result) == 600
    
    # make sure accessing objects outside range does return an empty list
    result = connector.search(size=600, page=2)
    assert result == []


def test_search_sorting(db200final_cfg):
    "Test if sort_by parameter works."
    connector = statement.StatementConnector(db200final_cfg)

    # default sort_by is 'createdWhen'
    result = connector.search(size=10, page=1)
    sort_fields = [s["createdWhen"] for s in result]
    assert sort_fields == sorted(sort_fields)

    # I've ommitted uris here, because ist does not make much sense
    # TODO: add addditional sort_by test values
    for fieldname in ("@id", "createdBy", "createdWhen", "modifiedBy", "modifiedWhen"):
        result = connector.search(size=10, page=1, sort_by=fieldname)
        sort_fields = [s[fieldname] for s in result]
        assert sort_fields == sorted(
            sort_fields
        ), "sorting for {} does not work".format(fieldname)

        result = connector.search(size=10, page=1, sort_by=fieldname, sort_order="ASC")
        sort_fields = [s[fieldname] for s in result]
        assert sort_fields == sorted(
            sort_fields
        ), "sorting for {} does not work".format(fieldname)

        result = connector.search(size=10, page=1, sort_by=fieldname, sort_order="DESC")
        sort_fields = [s[fieldname] for s in result]
        assert sort_fields == sorted(
            sort_fields, reverse=True
        ), "sorting for {} does not work".format(fieldname)


def test_search_sorting_second_value(cfg_10_identical_statements):
    "If sortBy values are identical use id as secondary sort value."
    connector = statement.StatementConnector(cfg_10_identical_statements)
    result = connector.search(size=10, page=1, sort_by="createdWhen")
    sort_fields = [(s["createdWhen"], s["@id"]) for s in result]
    assert sort_fields == sorted(sort_fields)

def test_count(db200final_cfg):
    "Test the connectors count method."
    conector = statement.StatementConnector(db200final_cfg)
    assert conector.count() == 600

