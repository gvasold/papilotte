"""Tests filtering (searching) for papilotte.connectors.pony.statement
"""
import copy
import datetime

import pytest

from pony import orm

from papilotte.connectors.pony import factoid


def test_filter_by_factoid_id(db200final_cfg):
    "Test the factoidId filter."
    # TODO
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, factoidId="F00154")) == 1
    # searching for ids only matches full ids (not parts of id)
    assert connector.search(size=100, page=1, factoidId="F0015") == []

def test_filter_by_from(db200final_cfg):
    "Filter by from= parameter"
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, from_='1803-03-30')) == 18

def test_filter_by_member_of(db200final_cfg):
    "Filter by memberOf= parameter"
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, memberOf='Group 00051')) == 6
    # search for partial entry in label
    assert len(connector.search(size=100, page=1, memberOf='oup 00051')) == 6
    # searching in label is case insensitive
    assert len(connector.search(size=100, page=1, memberOf='group 00051')) == 6

    # searching in uri is case sensitive and only matches full matches
    assert len(connector.search(size=100, page=1, memberOf='https://example.com/groups/00053')) == 6
    # Upercase 'G' should not be found
    assert connector.search(size=100, page=1, memberOf='https://example.com/Groups/00053') == []
    assert connector.search(size=100, page=1, memberOf='https://example.com/Groups/00053') == []
    assert connector.search(size=100, page=1, memberOf='https://example.com/Groups/0005') == []

def test_filter_by_name(db200final_cfg):
    "Filter by name= parameter"
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, name="Statement 0001")) == 4
    assert len(connector.search(size=100, page=1, name="statement 0001")) == 4
    assert len(connector.search(size=100, page=1, name="atement 0001")) == 4

def test_filter_by_place(db200final_cfg):
    "Filter by name= parameter"
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, place="Place 00053")) == 8
    assert len(connector.search(size=100, page=1, place="place 00053")) == 8
    assert len(connector.search(size=100, page=1, place="ace 00053")) == 8
    
    assert len(connector.search(size=100, page=1, place="https://example.com/places/00053")) == 4
    assert connector.search(size=100, page=1, place="https://example.com/PLaces/00053") == [] 
    assert connector.search(size=100, page=1, place="https://example.com/places/0005") == [] 

def test_filter_by_relates_to_person(db200final_cfg):
    "Filter by name= parameter"
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, relatesToPerson="Related person 00056")) == 6
    assert len(connector.search(size=100, page=1, relatesToPerson="related person 00056")) == 6
    assert len(connector.search(size=100, page=1, relatesToPerson="lated person 00056")) == 6
    
    assert len(connector.search(size=100, page=1, 
                relatesToPerson="https://example.com/relatedpersons/00058")) == 3
    assert connector.search(size=100, page=1, 
                relatesToPerson="https://example.com/RelatedPersons/00058") == []
    assert connector.search(size=100, page=1, 
                relatesToPerson="https://example.com/relatedpersons/0005") == []


def test_filter_by_role(db200final_cfg):
    "Filter by name= parameter"
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, role="Role 00051")) == 6
    assert len(connector.search(size=100, page=1, role="role 00051")) == 6
    assert len(connector.search(size=100, page=1, role="le 00051")) == 6

    assert len(connector.search(size=100, page=1, role="https://example.com/roles/00053")) == 6
    assert connector.search(size=100, page=1, role="https://example.com/ROLES/00053") == []
    assert connector.search(size=100, page=1, role="https://example.com/roles/0005") == []


def test_filter_by_source_id(db200final_cfg):
    "Test the sourceId filter."
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, sourceId="S00055")) == 2
    # searching for ids only matches full ids (not parts of id)
    assert connector.search(size=100, page=1, factoidId="F001") == []

def test_filter_by_source_label(db200final_cfg):
    "Test the label filter."
    connector = factoid.FactoidConnector(db200final_cfg)
    # search for exact label
    assert len(connector.search(size=100, page=1, label="Source 00002")) == 2
    # search for part of label
    assert len(connector.search(size=100, page=1, label="Source 0000")) == 16
    # search for non existing label
    assert connector.search(size=100, page=1, label="FooFooBar") == []

def test_filter_by_statement_content(db200final_cfg):
    "Filter by statementContent= parameter"
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, statementContent="Statement content 00061")) == 3
    assert len(connector.search(size=100, page=1, statementContent="statement content 00061")) == 3
    assert len(connector.search(size=100, page=1, statementContent="ement content 00061")) == 3

def test_filter_by_statement_type(db200final_cfg):
    "Filter by statementContent= parameter"
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, statementType="Statement type 00061")) == 6
    assert len(connector.search(size=100, page=1, statementType="statement TYPE 00061")) == 6
    assert len(connector.search(size=100, page=1, statementType="tement type 00061")) == 6
    assert len(connector.search(size=100, page=1, 
        statementType="https://example.com/statementtypes/00021")) == 9
    assert connector.search(size=100, page=1, 
        statementType="https://example.com/statementtypes/0002") == []

def test_filter_by_statement_id(db200final_cfg):
    "Test the statementId filter."
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=200, page=1, statementId="Stmt00024")) == 1
    # searching for ids only matches full ids (not parts of id)
    assert connector.search(size=100, page=1, factoidId="Stmt001") == []

def test_filter_by_to(db200final_cfg):
    "Filter by statementContent= parameter"
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, to='1800-06-01')) == 15



# ------------- Compliance level 1+ get tests ----------------------------------------------


# TODO: more tests
def test_filter_by_p(db200final_cfg):
    "Test the p= parameter."
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=200, page=1, p="P00058")) == 2
    assert len(connector.search(size=200, page=1, p="P0005")) == 22
    assert len(connector.search(size=200, page=1, p="https://example.com/persons/17a")) == 3
    # Test if only full uris are matched, so only '17a', but not 17
    assert len(connector.search(size=200, page=1, p="https://example.com/persons/17")) == 0

# TODO: more tests
def test_filter_by_f(db200final_cfg):
    "Test the f= parameter"
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=220, page=1, f="F00033")) == 1
    assert len(connector.search(size=200, page=1, f="F0003")) == 10




# TODO: more tests
def test_filter_by_s(db200final_cfg):
    "Test the s= parameter."
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=200, page=1, s="S00033")) == 2
    assert len(connector.search(size=200, page=1, s="S0003")) == 20
    assert len(connector.search(size=200, page=1, s="Source 00031")) == 2


# TODO: more tests? 
def test_filter_by_st(db200final_cfg):
    "Test the st= parameter."
    connector = factoid.FactoidConnector(db200final_cfg)
    assert len(connector.search(size=100, page=1, s="Source 00031")) == 2

    # id
    assert len(connector.search(size=100, page=1, st="Stmt00048")) == 1
    # date.label
    assert len(connector.search(size=100, page=1, st="Historical Date 00061")) == 2
    # memberOf.label
    assert len(connector.search(size=100, page=1, st="Group 00061")) == 6
    # memberOf.uri
    assert len(connector.search(size=100, page=1, st="https://example.com/groups/00061")) == 3
    # name
    assert len(connector.search(size=100, page=1, st="Statement 00048")) == 1
    # role.label
    assert len(connector.search(size=100, page=1, st="Role 00061")) == 6
    # statementContent
    assert len(connector.search(size=100, page=1, st="Statement content 00061")) == 3
    # statementtype.label
    assert len(connector.search(size=100, page=1, st="Statement type 00061")) == 6
    # statementType.uri
    assert len(connector.search(size=100, page=1, st="https://example.com/statementtypes/00021")) == 9
    # places.label
    assert len(connector.search(size=100, page=1, st="Place 00051")) == 10
    # places.uri
    assert len(connector.search(size=100, page=1, st="https://example.com/places/00053")) == 4
    # relatesToPersons.label
    assert len(connector.search(size=100, page=1, st="Related person 00056")) == 6
    # relatesToPersons.uri
    assert len(connector.search(size=100, page=1, st="https://example.com/relatedpersons/00058")) == 3
    # uris
    assert len(connector.search(size=100, page=1, st="https://example.com/statements/61a")) == 1


# FIXME: enable when implemented
def test_filter_factoid_and_source(db200final_cfg):
    "Test the sourceId filter together with factoid filter."
    connector = factoid.FactoidConnector(db200final_cfg)
    # there are 2 person with this source id
    assert len(connector.search(size=100, page=1, sourceId="S00055")) == 2
    # if we add a factoidId, there should be only one left
    assert len(connector.search(size=100, page=1, sourceId="S00055", factoidId="F00054")) == 1



def test_get_factoid_refs(db200final_cfg):
    connector = factoid.FactoidConnector(db200final_cfg)
    fact = connector.get('F00001')

    assert fact['source-ref']['@id'] == 'S00002'
    assert fact['person-ref']['@id'] == 'P00002'
    assert fact['statement-refs'][0]['@id'] == 'Stmt00001'
