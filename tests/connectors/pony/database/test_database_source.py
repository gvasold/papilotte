"""Tests for connectors.pony.database.Source
"""
from pony import orm
from papilotte.connectors.pony import database
import pytest
import datetime
import copy            


def test_create_from_ipif(db, data1):
    "Create a source with given id."
    Source = db.entities['Source']
    data = data1['factoids'][0]['source']
    with orm.db_session:
        s = Source.create_from_ipif(data)
        
        assert s.id == data['@id']
        assert s.createdBy == data['createdBy']
        assert s.createdWhen == datetime.datetime.fromisoformat(data['createdWhen'])
        assert s.modifiedBy == data['modifiedBy']
        assert s.label == data['label']
        assert s.modifiedWhen == datetime.datetime.fromisoformat(data['modifiedWhen'])
        assert len(s.uris) == len(data['uris'])
        assert sorted([u.uri for u in s.uris]) == sorted(data['uris'])

def test_create_from_ipif_without_id(db, data1):
    "Create a source with auto generated id."
    Source = db.entities['Source']
    data = data1['factoids'][0]['source']
    data.pop('@id')
    with orm.db_session:
        s = Source.create_from_ipif(data)
        assert s.id

def test_create_from_ipif_double_id(db, data1):
    "Creating a Source with an existing id should result in exception."
    Source = db.entities['Source']
    data = data1['factoids'][0]['source']
    with orm.db_session:
        Source.create_from_ipif(data)
        with pytest.raises(orm.CacheIndexError):
            Source.create_from_ipif(data)
    


def test_make_id(db, data1):
    "Test if make_id generates unique ids."
    Source = db.entities['Source']
    data = data1['factoids'][0]['source']
    data.pop('@id')
    # we create a Source from data, so id is taken
    with orm.db_session:
        s1 = Source.create_from_ipif(data)

        # Calling make_id with the same data should result in different id
        new_id = Source.make_id(data)
        assert new_id != s1.id


def test_update_from_ipif(db, data1):
    "A simple update on an existing object"
    Source = db.entities['Source']
    data_1 = data1['factoids'][0]['source']
    data_2 = copy.deepcopy(data_1)
    data_2['createdBy'] = 'Foo Foo Bar'
    data_2['uris'].pop(0)
    with orm.db_session:
        s = Source.create_from_ipif(data_1)
        s.update_from_ipif(data_2)
  
        assert s.id == data_2['@id']
        assert s.createdBy == data_2['createdBy']
        assert s.createdWhen == datetime.datetime.fromisoformat(data_2['createdWhen'])
        assert s.modifiedBy == data_2['modifiedBy']
        assert s.label == data_2['label']
        assert s.modifiedWhen == datetime.datetime.fromisoformat(data_2['modifiedWhen'])
        assert len(s.uris) == len(data_2['uris'])
        assert sorted([u.uri for u in s.uris]) == sorted(data_2['uris'])


def test_update_from_ipif_with_different_id(db, data1):
    "Make sure '@id' is ignored when updating."
    Source = db.entities['Source']
    data = data1['factoids'][0]['source']
    with orm.db_session:
        s = Source(id='abc')

        s.update_from_ipif(data)
        assert s.id == 'abc'

def test_to_ipif(db, data1):
    Source = db.entities['Source']
    data = data1['factoids'][0]['source']
    with orm.db_session:
        s = Source.create_from_ipif(data)
    s_ipif = s.to_ipif()
    assert s_ipif['@id'] == data['@id']
    assert s_ipif['createdWhen'] == data['createdWhen']
    assert s_ipif['createdBy'] == data['createdBy']
    assert s_ipif['modifiedWhen'] == data['modifiedWhen']
    assert s_ipif['modifiedBy'] == data['modifiedBy']
    assert s_ipif['label'] == data['label']
    assert len(s_ipif['uris']) == len(data['uris'])
    assert sorted(s_ipif['uris']) == sorted(data['uris'])


def test_deep_delete(db, data1):
    """Test source.safe_delete().
    
    safe_delete() not only deletes the source, but also all related
    SourceURIs, if they are orphaned after deleting the Source object.
    """
    Source = db.entities['Source']
    SourceURI = db.entities['SourceURI']
    # Create 2 Sources which share 1 URI
    s1_data = data1['factoids'][0]['source']
    s2_data = copy.deepcopy(s1_data)
    s2_data['@id'] = 's2a'
    s2_data['uris'].pop(0)
    with orm.db_session:
        s1 = Source.create_from_ipif(s1_data)
        s2 = Source.create_from_ipif(s2_data)
        assert len(s1.uris) == 2
        assert len(s2.uris) == 1
        # Deleting s2 should not affect SOurceURIs as both are referred from s1
        s2.deep_delete()
        assert len(orm.select(u.uri for u in SourceURI)[:]) == 2
        # Re-create s2
        s2 = Source.create_from_ipif(s2_data)
        # deleting s1 should only delete the 1 orphaned SourceURI
        s1.deep_delete()
        assert len(orm.select(u.uri for u in SourceURI)[:]) == 1
        # After deleting s2 no PersonURIs should remain
        s2.deep_delete()
        assert len(orm.select(u.uri for u in SourceURI)[:]) == 0

def test_ipif_refs(db200final):
    """Test the factoid-refs specific part of to_ipif().
    This can only be tested with full factoids."""
    Source = db200final.entities['Source']
    with orm.db_session:
        s = Source['S00002']
        refs = s.to_ipif()['factoid-refs']
        assert len(refs) == 2

        assert refs[0]['@id'] == 'F00001'
        assert refs[0]['source-ref']['@id'] == 'S00002'
        assert refs[0]['person-ref']['@id'] == 'P00002'
        assert refs[0]['statement-refs'][0]['@id'] == 'Stmt00001'

        assert refs[1]['@id'] == 'F00101'
        assert refs[1]['source-ref']['@id'] == 'S00002'
        assert refs[1]['person-ref']['@id'] == 'P00027'
        assert refs[1]['statement-refs'][0]['@id'] == 'Stmt00301'
