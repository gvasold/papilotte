import json

from papilotte import mockdata
import datetime

def test_make_metadate():
    "Test generation of a date base on a counter."
    d1 = mockdata.make_metadate(1)
    assert d1 == '2003-02-15T00:03:00'
    # same id must lead to same date
    assert mockdata.make_metadate(1) == d1

    # a higher id must lead to a later date
    assert mockdata.make_metadate(2) > d1

    # setting is_modification_date to True must leas to a later date
    d1a = mockdata.make_metadate(1, True)
    assert d1a > d1

def test_make_uris():
    "The make_uris function returns a list of uris."
    assert len(mockdata.make_uris(1, 'foo')) == 1
    assert mockdata.make_uris(1, 'foo')[0].startswith('https://example.com/foo')
    assert len(mockdata.make_uris(2, 'foo')) == 2
    assert len(mockdata.make_uris(6, 'foo')) == 1

def test_make_historical_date():
    assert mockdata.make_historical_date(1) == '1801-11-20'
    # every 20th has no date
    assert mockdata.make_historical_date(20) == ''
    # test the after= paramter
    after_date = datetime.date(1855, 1, 1)
    assert mockdata.make_historical_date(1, after=after_date) > after_date.isoformat()

def test_make_labeled_uri():
    assert mockdata.make_labeled_uri(1, 'foo', 'bar', 7) == {
        'uri': 'https://example.com/foo/00001',
        'label': 'bar 00001'
    }
    
    # every third has no uri
    u = mockdata.make_labeled_uri(3, 'foo', 'bar', 7)
    assert 'uri' not in u

    # every third has no label
    u = mockdata.make_labeled_uri(5, 'foo', 'bar', 7)
    assert 'label' not in u

def test_make_person():
    p7 = mockdata.make_person(7)
    assert p7['@id'] == 'P00007'
    assert p7['uris'] == ['https://example.com/persons/7a', 'https://example.com/persons/7b']
    assert p7['createdBy'] == 'Creator 00001'
    assert p7['createdWhen'] == '2003-02-15T00:21:00'
    assert p7['modifiedBy'] == 'Modifier 00001'
    assert p7['modifiedWhen'] == '2003-02-15T00:42:00'

    # every third has no modified data
    p3 = mockdata.make_person(3)
    assert 'modifiedBy' not in p3
    assert 'modifiedWhen' not in p3

    # every 6th has no created data
    p6 = mockdata.make_person(6)
    assert 'createdBy' not in p6
    assert 'createdWhen' not in p6



def test_make_source():
    s7 = mockdata.make_source(7)
    assert s7['@id'] == 'S00007'
    assert s7['label'] == 'Source 00007'
    assert s7['uris'] == ['https://example.com/sources/7a', 'https://example.com/sources/7b']
    assert s7['createdBy'] == 'Creator 00001'
    assert s7['createdWhen'] == '2003-02-15T00:21:00'
    assert s7['modifiedBy'] == 'Modifier 00001'
    assert s7['modifiedWhen'] == '2003-02-15T00:42:00'

    # every third has no modified data
    s3 = mockdata.make_person(3)
    assert 'modifiedBy' not in s3
    assert 'modifiedWhen' not in s3

    # every 6th has no created data
    s6 = mockdata.make_person(6)
    assert 'createdBy' not in s6
    assert 'createdWhen' not in s6


def test_make_statement():
    st1 = mockdata.make_statement(1, 1)
    assert st1['@id'] ==  'Stmt00001'
    assert st1['createdBy'] == 'Creator 00001'
    assert st1['createdWhen'] == '2003-02-15T00:03:00'
    assert st1['uris'] == ['https://example.com/statements/1a']
    assert st1['name'] == 'Statement 00001' 
    assert st1['date'] ==  {'sortDate': '1802-04-22', 'label': 'Historical Date 00003'}
    assert st1['memberOf'] == {'uri': 'https://example.com/groups/00002', 'label': 'Group 00002'}
    assert st1['places'] == [
        {'uri': 'https://example.com/places/00002', 'label': 'Place 00002'}, 
        {'label': 'Place 00003'}]
    assert st1['relatesToPersons'] == [
        {'uri': 'https://example.com/relatedpersons/00002', 
         'label': 'Related person 00002'}, 
        {'label': 'Related person 00003'}]
    assert st1['role'] ==  {'uri': 'https://example.com/roles/00002', 
                        'label': 'Role 00002'} 
    assert st1['statementContent'] == 'Statement content 00002'
    assert st1['statementType'] == {'uri': 'https://example.com/statementtypes/00002', 
                                    'label': 'Statement type 00002'}


def test_make_factoid():
    f1 = mockdata.make_factoid(1)
    assert f1['@id'] == 'F00001'
    assert f1['createdBy'] == 'Creator 00001'
    assert f1['createdWhen'] == '2003-02-15T00:03:00'
    assert f1['person']['@id'] == 'P00002'
    assert f1['source']['@id'] == 'S00002'
    assert f1['statements'][0]['@id'] == 'Stmt00002'
    assert f1['statements'][1]['@id'] == 'Stmt00003'

    # every 75th factoid has the same person
    f76 = mockdata.make_factoid(76)
    assert f76['person']['@id'] == f1['person']['@id']
    
    # every 100th factoid has the same source
    f101 = mockdata.make_factoid(101)
    assert f101['source']['@id'] == f1['source']['@id']

    # the number of statements depends on factoid num
    assert len(mockdata.make_factoid(1)['statements']) == 2
    assert len(mockdata.make_factoid(2)['statements']) == 3
    assert len(mockdata.make_factoid(3)['statements']) == 4
    assert len(mockdata.make_factoid(4)['statements']) == 5
    assert len(mockdata.make_factoid(5)['statements']) == 1
    assert len(mockdata.make_factoid(6)['statements']) == 2

    # every 7th (after 10) has a derivedFrom element
    f70 = mockdata.make_factoid(70)
    assert 'derivedFrom' in f70
    assert f70['derivedFrom'] == 'http://localhost:5000/api/factoids/7'

    # every 5th has a modified entry
    f5 = mockdata.make_factoid(5)
    assert 'modifiedWhen' in f5
    assert 'modifiedBy' in f5

def test_make_factoids():
    len([f for f in mockdata.make_factoids(5)]) == 5

def test_make_factoid_consistency():
    """Make sure all referenced persons, source and factoids are identical
    if they have the same id.
    """
    # collect data from 1000 facrtoids
    persons = {}
    sources = {}
    statements = {}
    for f in mockdata.make_factoids(1000):
        p_id = f['person']['@id']
        p_set = persons.get(p_id, set())
        p_set.add(json.dumps(f['person']))
        persons[p_id] = p_set

        s_id = f['source']['@id']
        s_set = sources.get(s_id, set())
        s_set.add(json.dumps(f['source']))
        sources[s_id] = s_set

        for stmt in f['statements']:
            st_id = stmt['@id']
            st_set = statements.get(st_id, set())
            st_set.add(json.dumps(stmt))
            statements[st_id] =st_set
