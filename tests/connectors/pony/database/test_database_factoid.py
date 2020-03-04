"""Tests for connectors.pony.database.Factoid
"""
from pony import orm
#from papilotte.connectors.pony import database
import pytest
import datetime
import copy            

def test_create_from_ipif(db, data1):
    Factoid = db.entities['Factoid']
    data = data1['factoids'][0]
    data['derivedFrom'] = "999"
    with orm.db_session:
        f = Factoid.create_from_ipif(data)
        assert f.createdBy == data['createdBy']
        assert f.createdWhen == datetime.datetime.fromisoformat(data['createdWhen'])
        assert f.modifiedBy == data.get('modifiedBy', '')
        assert f.modifiedWhen == None  # datetime.datetime.fromisoformat(f_data.get('modifiedWhen', ''))
        assert f.derivedFrom == data['derivedFrom']
        assert f.person.id == data['person']['@id']
        assert f.source.id == data['source']['@id']
        sorted_statements = sorted(f.statements, key=lambda s: s.id)
        assert sorted_statements[0].id == data['statements'][0]['@id']


        

def test_create_from_ipif_with_existing_children(db, data1):
    """Test factoid creation, when person and source have been create before.
    
    Hint: Statements are weak entities, so they cannot exist in before.
    Factoid only contains the ids for person, source.
    """
    Factoid = db.entities['Factoid']
    Person = db.entities['Person']
    Source = db.entities['Source']
    Statement = db.entities['Statement']
    data = data1['factoids'][0]
    data['derivedFrom'] = "999"
    # replace full child elements by '@ids' only
    person_data = data.pop('person')
    data['person'] = {'@id': person_data['@id']}
    source_data = data.pop('source')
    data['source'] = {'@id': source_data['@id']}
    #statement_data = data.pop('statements')
    #data['statements'] = [{'@id': s['@id']} for s in statement_data]
    with orm.db_session:
        # Create person, source and statements, so that they already exist when creating
        # the whole factoid
        p = Person.create_from_ipif(person_data)
        s = Source.create_from_ipif(source_data)
        #for stmt in statement_data:
        #    st = Statement.create_from_ipif(stmt)
        # create the factoid (person, source and statements should be recycled)
        f = Factoid.create_from_ipif(data)
        assert f.createdBy == data['createdBy']
        assert f.createdWhen == datetime.datetime.fromisoformat(data['createdWhen'])
        assert f.modifiedBy == data.get('modifiedBy', '')
        assert f.modifiedWhen == None  # datetime.datetime.fromisoformat(f_data.get('modifiedWhen', ''))
        assert f.derivedFrom == data['derivedFrom']
        assert f.person.id == data['person']['@id']
        assert f.person.createdBy == p.createdBy
        assert f.person.uris == p.uris
        assert f.source.id == data['source']['@id']
        assert f.source.label == s.label
        assert f.source.uris == s.uris
        sorted_statements = sorted(f.statements, key=lambda s: s.id)
        assert sorted_statements[0].id == data['statements'][0]['@id']
        assert sorted_statements[0].role.label == data['statements'][0]['role']['label']
        

def test_create_from_ipif_without_id(db, data1):
    "Create a Factoid with auto generated id."
    Factoid = db.entities['Factoid']
    data = data1['factoids'][0]
    data.pop('@id')
    with orm.db_session:
        f = Factoid.create_from_ipif(data)
        assert f.id

def test_create_from_ipif_double_id(db, data1):
    "Creating a Factoid with an existing id should result in exception."
    Factoid = db.entities['Factoid']
    data = data1['factoids'][0]
    with orm.db_session:
        Factoid.create_from_ipif(data)
        with pytest.raises(orm.CacheIndexError):
            Factoid.create_from_ipif(data)
    
def test_deep_delete(db, data1):
    """Test .safe_delete().
    
    safe_delete() not only deletes the statement, but also the 
    related memberOf if it would be orphaned after deleting the Statement.
    """
    Factoid = db.entities['Factoid']
    Person = db.entities['Person']
    Source = db.entities['Source']
    Statement = db.entities['Statement']
    with orm.db_session:
        f1_data = data1['factoids'][0]
        
        # basic: only 1 factoid. All related entries should be gone after
        # deleting the factoid
        f1 = Factoid.create_from_ipif(f1_data)
        f1.deep_delete()
        assert orm.select(f for f in Factoid).count() == 0
        assert orm.select(p for p in Person).count() == 0
        assert orm.select(s for s in Source).count() == 0
        assert orm.select(s for s in Statement).count() == 0

        # 2 Factoids sharing source and person. Source and person must not be deleteda
        # make second factoid with changed ids 
        f2_data = copy.deepcopy(f1_data)
        f2_data['@id'] = 'foo2'
        for stmt in f2_data['statements']:
            stmt['@id'] = stmt['@id'] + 'a'
        f1 = Factoid.create_from_ipif(f1_data)
        # create the second factoid (factoid.id and statements are different)
        Factoid.create_from_ipif(f2_data)
        f1.deep_delete()
        assert orm.select(f for f in Factoid).count() == 1
        assert orm.select(p for p in Person).count() == 1
        assert orm.select(s for s in Source).count() == 1
        assert orm.select(s for s in Statement).count() == 2

def test_make_id(db, data1):
    "Test if make_id generates unique ids."
    Factoid = db.entities['Factoid']
    data = data1['factoids'][0]
    data.pop('@id')
    # we create a Factoid from data, so id is taken
    with orm.db_session:
        f1 = Factoid.create_from_ipif(data)

        # Calling make_id with the same data should result in different id
        new_id = Factoid.make_id(data)
        assert new_id != f1.id

def test_update_from_ipif(db, data1):
    "A simple update on an existing object"
    Factoid = db.entities['Factoid']

    data = data1['factoids'][0]
    data['derivedFrom'] = "999"

    with orm.db_session:
        f = Factoid.create_from_ipif(data)

        # Change simple values. Are they reflected in db?
        data['derivedFrom'] = 'xxx'
        data['createdBy'] = 'foo foo bar'
        data['createdWhen'] = datetime.datetime.now().isoformat()
        data['person']['createdBy'] = 'foooooooo'
        data['source']['createdBy'] = 'baaaaaaar'
        data['statements'][0]['createdBy'] = 'foooobaaaar'
    
        f.update_from_ipif(data)
        assert f.id == data['@id']
        assert f.createdBy == data['createdBy']
        assert f.createdWhen == datetime.datetime.fromisoformat(data['createdWhen'])
        assert f.person.id == data['person']['@id']
        assert f.person.createdBy == data['person']['createdBy']
        assert f.source.id == data['source']['@id']
        assert f.source.createdBy == data['source']['createdBy']
        sorted_statements = sorted(f.statements, key=lambda s: s.id)
        assert sorted_statements[0].id == data['statements'][0]['@id']
        assert sorted_statements[0].createdBy == data['statements'][0]['createdBy']

def test_update_from_ipif_with_different_id(db, data1):
    "Make sure '@id' is ignored when updating."
    Factoid = db.entities['Factoid']
    initial_data = copy.deepcopy(data1['factoids'][0])
    data = data1['factoids'][0]
    initial_data['@id'] = 'abc'
    with orm.db_session:
        f = Factoid.create_from_ipif(initial_data)
        f.update_from_ipif(data)
        assert f.id == 'abc'

def test_to_ipif(db, data1):
    Factoid = db.entities['Factoid']
    data = data1['factoids'][0]
    data['derivedFrom'] = '9999'
    with orm.db_session:
        f = Factoid.create_from_ipif(data)
        
        f_ipif = f.to_ipif()
        assert f_ipif['@id'] == data['@id']
        assert f_ipif['createdBy'] == data['createdBy']
        assert f_ipif['createdWhen'] == data['createdWhen']
        assert f_ipif['modifiedBy'] == ''
        assert f_ipif['modifiedWhen'] == ""
        assert f_ipif['derivedFrom'] == data['derivedFrom']
        assert f_ipif['person']['@id'] == data['person']['@id']
        assert f_ipif['source']['@id'] == data['source']['@id']
        sorted_statements = sorted(f_ipif['statements'], key=lambda s: s['@id'])
        assert sorted_statements[0]['@id'] == data['statements'][0]['@id']
        assert f_ipif['person-ref']['@id'] == data['person']['@id']
        assert f_ipif['source-ref']['@id'] == data['source']['@id']
        assert f_ipif['statement-refs'][0]['@id'] == data['statements'][0]['@id']

