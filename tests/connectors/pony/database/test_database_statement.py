"""Tests for connectors.pony.database.Statement
"""
from pony import orm
from papilotte.connectors.pony import database
import pytest
import datetime
import copy            

def test_create_from_ipif(db, data1):
    "Create a statement with given id."
    Statement = db.entities['Statement']
    with orm.db_session:
        data = data1['factoids'][0]['statements'][0]
        s = Statement.create_from_ipif(data)

        assert s.id == data['@id']
        assert s.createdBy == data['createdBy']
        assert s.createdWhen == datetime.datetime.fromisoformat(data['createdWhen'])
        #assert s.modifiedBy == data.get('modifiedBy', '')
        #assert s.modifiedWhen == datetime.datetime.fromisoformat(data.get('modifiedWhen', None)
        assert s.name == data['name']
        assert s.statementContent == data['statementContent']
        assert s.date.label == data['date']['label']
        assert s.date.sortDate == datetime.datetime.fromisoformat(data['date']['sortDate']).date()
        assert s.role.uri == data['role']['uri']
        assert s.role.label == data['role']['label']
        assert s.statementType.uri == data['statementType']['uri']
        assert s.statementType.label == data['statementType']['label']
        assert s.memberOf.uri == data['memberOf']['uri']
        assert s.memberOf.label == data['memberOf']['label']
        assert len(s.places) == len(data['places'])
        assert sorted([p.label for p in s.places]) == sorted([p['label'] for p in data['places']])
        assert len(s.uris) == len(data['uris'])
        assert sorted([u.uri for u in s.uris]) == sorted(data['uris'])

        assert sorted([p.uri for p in s.places]) == sorted([p.get('uri', '') for p in data['places']])
        assert sorted([r.uri for r in s.relatesToPersons]) == sorted([r.get('uri', '') for r in data['relatesToPersons']])
        assert sorted([r.label for r in s.relatesToPersons]) == sorted([r.get('label', '') for r in data['relatesToPersons']])

def test_create_from_ipif_without_id(db, data1):
    "Create a statement with auto generated id."
    Statement = db.entities['Statement']
    with orm.db_session:
        data = data1['factoids'][0]['statements'][0]
        data.pop('@id')
        s = Statement.create_from_ipif(data)
        assert s.id

def test_create_from_ipif_double_id(db, data1):
    "Creating a Statement with an existing id should result in exception."
    Statement = db.entities['Statement']
    with orm.db_session:
        data = data1['factoids'][0]['statements'][0]
        Statement.create_from_ipif(data)
        with pytest.raises(orm.CacheIndexError):
            Statement.create_from_ipif(data)
    

def test_make_id(db, data1):
    "Test if make_id generates unique ids."
    Statement = db.entities['Statement']
    with orm.db_session:
        data = data1['factoids'][0]['statements'][0]
        data.pop('@id')
        # we create a Statement from data, so id is taken
        s1 = Statement.create_from_ipif(data)

        # Calling make_id with the same data should result in different id
        new_id = Statement.make_id(data)
        assert new_id != s1.id

def test_update_from_ipif(db, data1):
    "A simple update on an existing object"
    Statement = db.entities['Statement']
    with orm.db_session:    
        data = data1['factoids'][0]['statements'][0]
        data_new = copy.deepcopy(data)
        data_new['createdBy'] = 'Foo Foo Bar'
        data_new['uris'] = ['foooo']
        data_new['places'] = [{'label': 'foo', 'uri': 'foo'}]
        data_new['relatesToPersons'] = [{'label': 'bar', 'uri': 'bar'}]
        data_new['statementType'] = {'label': 'foo', 'uri': 'foo'}
        data_new['role'] = {'label': 'foo', 'uri': 'foo'}
        data_new['memberOf'] = {'label': 'foo', 'uri': 'foo'}
        data_new['date'] = {'label': 'foo', 'sortDate': datetime.date(1805, 3, 17).isoformat()}

        s = Statement.create_from_ipif(data)
        Date = db.entities['Date']
        Role = db.entities['Role']
        StatementType = db.entities['StatementType']
        MemberGroup = db.entities['MemberGroup']
        RelatesToPerson = db.entities['RelatesToPerson']
        Place = db.entities['Place']
        StatementURI = db.entities['StatementURI']

        s.update_from_ipif(data_new)

        assert s.id == data_new['@id']
        assert s.createdBy == data_new['createdBy']
        assert s.name == data_new['name']
        assert s.statementContent == data_new['statementContent']
        assert s.date.label == data_new['date']['label']
        assert s.date.sortDate == datetime.datetime.fromisoformat(data_new['date']['sortDate']).date()
        assert s.role.uri == data_new['role']['uri']
        assert s.role.label == data_new['role']['label']
        assert s.statementType.uri == data_new['statementType']['uri']
        assert s.statementType.label == data_new['statementType']['label']
        assert s.memberOf.uri == data_new['memberOf']['uri']
        assert s.memberOf.label == data_new['memberOf']['label']
        assert len(s.relatesToPersons) == len(data_new['relatesToPersons'])
        assert sorted([r.uri for r in s.relatesToPersons]) == sorted([r['uri'] for r in data_new['relatesToPersons']])
        assert sorted([r.label for r in s.relatesToPersons]) == sorted([r['label'] for r in data_new['relatesToPersons']])
        assert len(s.places) == len(data_new['places'])
        assert sorted([p.uri for p in s.places]) == sorted([p['uri'] for p in data_new['places']])
        assert sorted([p.label for p in s.places]) == sorted([p['label'] for p in data_new['places']])
        assert len(s.uris) == len(data_new['uris'])
        assert sorted([u.uri for u in s.uris]) == sorted(data_new['uris'])

        # Test if deletion of orphaned sub-objects works:
        # we replaced all sub-element, but still only 1 of each type may exists in db.
        assert orm.select(s for s in Statement).count() == 1
        assert orm.select(d for d in Date).count() == 1
        assert orm.select(r for r in Role).count() == 1
        assert orm.select(s for s in StatementType).count() == 1
        assert orm.select(m for m in MemberGroup).count() == 1
        assert orm.select(r for r in RelatesToPerson).count() == 1
        assert orm.select(p for p in Place).count() == 1
        assert orm.select(u for u in StatementURI).count() == 1

def test_update_from_ipif_with_different_id(db, data1):
    "Make sure '@id' is ignored when updating."
    Statement = db.entities['Statement']
    with orm.db_session:
        data = data1['factoids'][0]['statements'][0]
        s = Statement(id='abc')

        s.update_from_ipif(data)
        assert s.id == 'abc'


def test_to_ipif(db, data1):
    Statement = db.entities['Statement']
    with orm.db_session:
        data = data1['factoids'][0]['statements'][0]
        s = Statement.create_from_ipif(data)
        s_ipif = s.to_ipif()
        assert s_ipif['@id'] == data['@id']
        assert s_ipif['createdBy'] == data['createdBy']
        assert s_ipif['createdWhen'] == data['createdWhen']
        assert s_ipif['modifiedBy'] == data.get('modifiedBy', '')
        #assert s_ipif['modifiedWhen'] == data['modifiedWhen']
        assert s_ipif['name'] == data['name']
        assert s_ipif['statementContent'] == data['statementContent']
        assert s_ipif['date']['label'] == data['date']['label']
        assert s_ipif['date']['sortDate'] == data['date']['sortDate']
        assert s_ipif['role']['uri'] == data['role']['uri']
        assert s_ipif['role']['label'] == data['role']['label']
        assert s_ipif['statementType']['uri'] == data['statementType']['uri']
        assert s_ipif['statementType']['label'] == data['statementType']['label']
        assert s_ipif['memberOf']['uri'] == data['memberOf']['uri']
        assert s_ipif['memberOf']['label'] == data['memberOf']['label']
        assert len(s_ipif['relatesToPersons']) == len(data['relatesToPersons'])
        assert sorted(s_ipif['relatesToPersons'], key=lambda rp: rp['label']) == \
            sorted(data['relatesToPersons'], key=lambda rp: rp['label'])
        assert len(s_ipif['places']) == len(data['places'])
        assert sorted(s_ipif['places'], key=lambda p: p['label']) == \
            sorted(data['places'], key=lambda p: p['label'])
        assert len(s_ipif['uris']) == len(data['uris'])
        assert sorted(s_ipif['uris']) == sorted(data['uris'])

def test_deep_delete(db, data1):
    Statement = db.entities['Statement']
    with orm.db_session:
        Date = db.entities['Date']
        Role = db.entities['Role']
        StatementType = db.entities['StatementType']
        MemberGroup = db.entities['MemberGroup']
        RelatesToPerson = db.entities['RelatesToPerson']
        Place = db.entities['Place']
        StatementURI = db.entities['StatementURI']

        data = data1['factoids'][0]['statements'][0]
        stmt = Statement.create_from_ipif(data)
        stmt.deep_delete()
        # After deleting the only factoid, the database must be empty
        assert orm.select(s for s in Statement).count() == 0
        assert orm.select(d for d in Date).count() == 0
        assert orm.select(r for r in Role).count() == 0
        assert orm.select(s for s in StatementType).count() == 0
        assert orm.select(m for m in MemberGroup).count() == 0
        assert orm.select(r for r in RelatesToPerson).count() == 0
        assert orm.select(p for p in Place).count() == 0
        assert orm.select(u for u in StatementURI).count() == 0

def test_ipif_refs(db200final):
    """Test the factoid-refs specific part of to_ipif().
    This can only be tested with full factoids."""
    Statement = db200final.entities['Statement']
    with orm.db_session:
        s = Statement['Stmt00002']
        refs = s.to_ipif()['factoid-refs']
        assert len(refs) == 1

        assert refs[0]['@id'] == 'F00001'
        assert refs[0]['source-ref']['@id'] == 'S00002'
        assert refs[0]['person-ref']['@id'] == 'P00002'
        assert refs[0]['statement-refs'][0]['@id'] == 'Stmt00001'