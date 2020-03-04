"""Tests for connectors.pony.database.Person
"""
from pony import orm
from papilotte.connectors.pony import database
import pytest
import datetime
import copy            


def test_create_from_ipif(db, data1):
    "Create a person with given id."
    Person = db.entities['Person']
    data = data1['factoids'][0]['person']
    with orm.db_session:
        p = Person.create_from_ipif(data)
        assert p.id == data['@id']
        assert p.createdBy == data['createdBy']
        assert p.createdWhen == datetime.datetime.fromisoformat(data['createdWhen'])
        assert p.modifiedBy == data['modifiedBy']
        assert p.modifiedWhen == datetime.datetime.fromisoformat(data['modifiedWhen'])
        assert len(p.uris) == len(data['uris'])
        assert sorted([u.uri for u in p.uris]) == sorted(data['uris'])

def test_create_from_ipif_without_id(db, data1):
    "Create a person with auto generated id."
    Person = db.entities['Person']
    data = data1['factoids'][0]['person']
    data.pop('@id')
    with orm.db_session:
        p = Person.create_from_ipif(data)
        assert p.id

def test_create_from_ipif_double_id(db, data1):
    "Creating a Person with an existing id should result in exception."
    Person = db.entities['Person']
    data = data1['factoids'][0]['person']
    with orm.db_session:
        Person.create_from_ipif(data)
        with pytest.raises(orm.CacheIndexError):
            Person.create_from_ipif(data)
    


def test_make_id(db, data1):
    "Test if make_id generates unique ids."
    Person = db.entities['Person']
    data = data1['factoids'][0]['person']
    data.pop('@id')
    # we create a Person from data, so id is taken
    with orm.db_session:
        p1 = Person.create_from_ipif(data)

        # Calling make_id with the same data should result in different id
        new_id = Person.make_id(data)
        assert new_id != p1.id


def test_update_from_ipif(db, data1):
    "A simple update on an existing object"
    Person = db.entities['Person']
    PersonURI = db.entities['PersonURI']
    p_data1 = data1['factoids'][0]['person']
    # change some data
    p_data2 = copy.deepcopy(p_data1)
    p_data2['createdBy'] = 'Foo Foo Bar'
    p_data2['uris'].pop(0)
    with orm.db_session:
        p = Person.create_from_ipif(p_data1)

        p.update_from_ipif(p_data2)
        
        assert p.id == p_data2['@id']
        assert p.createdBy == p_data2['createdBy']
        assert p.createdWhen == datetime.datetime.fromisoformat(p_data2['createdWhen'])
        assert p.modifiedBy == p_data2['modifiedBy']
        assert p.modifiedWhen == datetime.datetime.fromisoformat(p_data2['modifiedWhen'])
        assert len(p.uris) == len(p_data2['uris'])
        assert sorted([u.uri for u in p.uris]) == sorted(p_data2['uris'])
        # Make sure no orphaned PersonURIs exist
        assert orm.select(p for p in PersonURI if len(p.persons) == 0).count() == 0


def test_update_from_ipif_with_different_id(db, data1):
    "Make sure '@id' is ignored when updating."
    Person = db.entities['Person']
    data = data1['factoids'][0]['person']
    with orm.db_session:
        p = Person(id='abc')

        p.update_from_ipif(data)
        assert p.id == 'abc'

def test_to_ipif(db, data1):
    Person = db.entities['Person']
    data = data1['factoids'][0]['person']
    with orm.db_session:
        p = Person.create_from_ipif(data)
    p_ipif = p.to_ipif()
    assert p_ipif['@id'] == data['@id']
    assert p_ipif['createdWhen'] == data['createdWhen']
    assert p_ipif['createdBy'] == data['createdBy']
    assert p_ipif['modifiedWhen'] == data['modifiedWhen']
    assert p_ipif['modifiedBy'] == data['modifiedBy']
    assert len(p_ipif['uris']) == len(data['uris'])
    assert sorted(p_ipif['uris']) == sorted(data['uris'])

def test_deep_delete(db, data1):
    """Test if orphaned child elements are deleted, when person is deleted.
    """
    Person = db.entities['Person']
    PersonURI = db.entities['PersonURI']
    # Create 2 Persons which share 1 URI
    p1_data = data1['factoids'][0]['person']
    p2_data = copy.deepcopy(p1_data)
    p2_data['@id'] = 'p2a'
    p2_data['uris'].pop(0)
    with orm.db_session:
        p1 = Person.create_from_ipif(p1_data)
        p2 = Person.create_from_ipif(p2_data)
        assert len(p1.uris) == 2
        assert len(p2.uris) == 1
        # Deleting p2 should not affect PersonURIs as both are referred from p1
        p2.deep_delete()
        assert len(orm.select(u.uri for u in PersonURI)[:]) == 2
        # Re-create p2
        p2 = Person.create_from_ipif(p2_data)
        # deleting p1 should only delete the 1 orphaned PersonURI
        p1.deep_delete()
        assert len(orm.select(u.uri for u in PersonURI)[:]) == 1
        # After deleting p2 no PersonURIs should remain
        p2.deep_delete()
        assert orm.select(u.uri for u in PersonURI).count() == 0

def test_ipif_refs(db200final):
    """Test the factoid-refs specific part of to_ipif().
    This can only be tested with full factoids."""
    Person = db200final.entities['Person']
    with orm.db_session:
        p = Person['P00002']
        refs = p.to_ipif()['factoid-refs']
        assert len(refs) == 3
        assert refs[0]['@id'] == 'F00001'
        assert refs[0]['source-ref']['@id'] == 'S00002'
        assert refs[0]['person-ref']['@id'] == 'P00002'
        
        assert refs[0]['statement-refs'][0]['@id'] == 'Stmt00001'

        assert refs[1]['@id'] == 'F00076'
        assert refs[1]['source-ref']['@id'] == 'S00077'
        assert refs[1]['person-ref']['@id'] == 'P00002'
        assert refs[1]['statement-refs'][0]['@id'] == 'Stmt00226'
        assert refs[1]['statement-refs'][1]['@id'] == 'Stmt00227'

        assert refs[2]['@id'] == 'F00151'
        assert refs[2]['source-ref']['@id'] == 'S00052'
        assert refs[2]['person-ref']['@id'] == 'P00002'
        assert refs[2]['statement-refs'][0]['@id'] == 'Stmt00451'
