"""Tests for papilotte.connectors.pony.source
"""
import copy
import datetime

import pytest

from pony import orm

from papilotte.connectors.pony import source

@pytest.fixture()
def cfg_10_identical_sources(mockcfg):
    """Return a cfg dict containing a db prepopulated with 10 nearly identical sources
    The only difference is id.
    """
    Source = mockcfg["db"].entities["Source"]
    with orm.db_session():
        for i in range(1, 101):
            data = {
                "@id": "S{:03d}".format(11 - i),
                "createdBy": "Creator 1",
                "createdWhen": datetime.datetime(2015, 1, 1).isoformat(),
                "modifiedBy": "Modifier 1",
                "modifiedWhen": datetime.datetime(2015, 1, 2).isoformat(),
                "label": "Label 1",
                "uris": [
                    "https://example.com/sources/1",
                    "https://example.com/sources/2",
                ],
            }
            Source.create_from_ipif(data)
    yield mockcfg


def test_get(db200final_cfg):
    "Test the connector get method without filters."
    connector = source.SourceConnector(db200final_cfg)
    src = connector.get('S00001')
    assert src['@id'] == 'S00001'
    assert src['createdBy'] == 'Creator 00001'
    assert src['createdWhen'] == '2003-02-15T00:03:00'
    assert src['modifiedBy'] == 'Modifier 00001'
    assert src['modifiedWhen'] == '2003-02-15T00:06:00'
    assert src['label'] == 'Source 00001'
    assert src['uris'] == ['https://example.com/sources/1a']
    assert src['factoid-refs'][0]['@id'] == 'F00100' 
    assert src['factoid-refs'][0]['source-ref']['@id'] == 'S00001'
    assert src['factoid-refs'][0]['person-ref']['@id'] == 'P00026'
    assert src['factoid-refs'][0]['statement-refs'][0]['@id'] == 'Stmt00300'

    assert src['factoid-refs'][1]['@id'] == 'F00200' 
    assert src['factoid-refs'][1]['source-ref']['@id'] == 'S00001'
    assert src['factoid-refs'][1]['person-ref']['@id'] == 'P00051'
    assert src['factoid-refs'][1]['statement-refs'][0]['@id'] == 'Stmt00600'


def test_get_with_uri(db200final_cfg):
    "Test the connector get method for a single source when using an uri instead of the id."
    connector = source.SourceConnector(db200final_cfg)
    pers = connector.get('https://example.com/sources/2a')
    assert pers['@id'] == 'S00002'
    pers = connector.get('https://example.com/sources/2b')
    assert pers['@id'] == 'S00002'

def test_search_paging(db200final_cfg):
    "Test search() without filtering."
    connector = source.SourceConnector(db200final_cfg)
    result = connector.search(size=30, page=1)
    assert len(result) == 30

    result = connector.search(size=30, page=2)
    assert len(result) == 30

    # Make sure all remaining sources are returned if size > number of pages
    result = connector.search(size=300, page=1)
    assert len(result) == 100
    
    # make sure accessing objects outside range does return an empty list
    result = connector.search(size=200, page=2)
    assert result == []

def test_search_sorting(db200final_cfg):
    "Test if sort_by parameter works."
    connector = source.SourceConnector(db200final_cfg)

    # default sort_by is 'createdWhen'
    result = connector.search(size=10, page=1)
    sort_fields = [s["createdWhen"] for s in result]
    assert sort_fields == sorted(sort_fields)

    # I've ommitted uris here, because ist doen not make much sense
    for fieldname in ("@id", "createdBy", "createdWhen", "label", "modifiedBy", "modifiedWhen"):
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


def test_search_sorting_second_value(cfg_10_identical_sources):
    "If sortBy values are identical use id as secondary sort value."
    connector = source.SourceConnector(cfg_10_identical_sources)
    cfg_10_identical_sources
    result = connector.search(size=10, page=1, sort_by="createdWhen")
    sort_fields = [(s["createdWhen"], s["@id"]) for s in result]
    assert sort_fields == sorted(sort_fields)


def test_count(db200final_cfg):
    "Test the connectors count method."
    conector = source.SourceConnector(db200final_cfg)
    assert conector.count() == 100

