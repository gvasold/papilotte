"""General tests for connectors.pony.database
"""
from pony import orm
from papilotte.connectors.pony import database
import pytest
import datetime


def test_make_db(db):
    "Test if we get a working orm."
    assert 'Factoid' in db.entities
    with orm.db_session:
        assert db.get('select count(*) from Factoid') == 0


def test_date(db):
    Date = db.entities['Date']
    date1 = datetime.date(1875, 1, 2)
    with orm.db_session:
        d1 = Date(sortDate=date1, label='foobar')
        assert d1.label == 'foobar'
        assert d1.sortDate == date1

        # Pony also support a string as date value
        d1 = Date(sortDate='1875-01-02', label='foobar')
        assert d1.label == 'foobar'
        assert d1.sortDate == date1

def test_date_get_or_create(db):
    "Test get_or_create for Person."
    Date = db.entities['Date']
    date1 =  datetime.date(1875, 1, 1)
    date2 =  datetime.date(1875, 1, 2)
    with orm.db_session:
        d1 = Date(label='foo', sortDate=date1)
        # same values as for d1 must result in same ids
        d2 = Date.get_or_create(label='foo', sortDate=date1)
        assert d1.id == d2.id

        ## label is different to r1
        d2 = Date.get_or_create(label='bar', sortDate=date1)
        assert d1.id != d2.id

        ## sortDate is different to r1
        d2 = Date.get_or_create(label='foo', sortDate=date2)
        assert d1.id != d2.id

        ## both values are different
        d2 = Date.get_or_create(label='bar', sortDate=date2)
        assert d1.id != d2.id

        # an empty string in sortDate must become None
        d = Date.get_or_create(label='bar', sortDate='')
        assert d.sortDate is None

def test_role(db):
    Role = db.entities['Role']
    with orm.db_session:
        r1 = Role(uri='foo', label='foobar')
        assert r1.label == 'foobar'
        assert r1.uri == 'foo'


def test_role_get_or_create(db):
    "Test get_or_create for Person."
    with orm.db_session:
        Role = db.entities['Role']
        r1 = Role(uri='foo', label='foobar')
        # same values as r1 must result in same ids
        r2 = Role.get_or_create(uri='foo', label='foobar')
        assert r1.id == r2.id

        ## uri is different to r1
        r2 = Role.get_or_create(uri='bar', label='foobar')
        assert r1.id != r2.id

        ## label is different to r1
        r2 = Role.get_or_create(uri='foo', label='barfoo')
        assert r1.id != r2.id

        ## both values are different
        r2 = Role.get_or_create(uri='bar', label='barfoo')
        assert r1.id != r2.id

def test_member_group(db):
    MemberGroup = db.entities['MemberGroup']
    with orm.db_session:
        g1 = MemberGroup(uri='foo', label='foobar')
        assert g1.label == 'foobar'
        assert g1.uri == 'foo'


def test_member_group_get_or_create(db):
    "Test get_or_create for Person."
    MemberGroup = db.entities['MemberGroup']
    with orm.db_session:
        g1 = MemberGroup(uri='foo', label='foobar')
        # same values as r1 must result in same ids
        g2 = MemberGroup.get_or_create(uri='foo', label='foobar')
        assert g1.id == g2.id

        ## uri is different to r1
        g2 = MemberGroup.get_or_create(uri='bar', label='foobar')
        assert g1.id != g2.id

        ## label is different to r1
        g2 = MemberGroup.get_or_create(uri='foo', label='barfoo')
        assert g1.id != g2.id

        ## both values are different
        g2 = MemberGroup.get_or_create(uri='bar', label='barfoo')
        assert g1.id != g2.id



def test_statement_type(db):
    StatementType = db.entities['StatementType']
    with orm.db_session:
        s1 = StatementType(uri='foo', label='foobar')
        assert s1.label == 'foobar'
        assert s1.uri == 'foo'


def test_statement_type_get_or_create(db):
    "Test get_or_create for Person."
    StatementType = db.entities['StatementType']
    with orm.db_session:
        s1 = StatementType(uri='foo', label='foobar')
        # same values as r1 must result in same ids
        s2 = StatementType.get_or_create(uri='foo', label='foobar')
        assert s1.id == s2.id

        ## uri is different to r1
        s2 = StatementType.get_or_create(uri='bar', label='foobar')
        assert s1.id != s2.id

        ## label is different to r1
        s2 = StatementType.get_or_create(uri='foo', label='barfoo')
        assert s1.id != s2.id

        ## both values are different
        s2 = StatementType.get_or_create(uri='bar', label='barfoo')
        assert s1.id != s2.id

def test_place(db):
    Place = db.entities['Place']
    with orm.db_session:
        p1 = Place(uri='foo', label='foobar')
        assert p1.label == 'foobar'
        assert p1.uri == 'foo'


def test_place_get_or_create(db):
    "Test get_or_create for Person."
    with orm.db_session:
        Place = db.entities['Place']
        p1 = Place(uri='foo', label='foobar')
        # same values as r1 must result in same ids
        p2 = Place.get_or_create(uri='foo', label='foobar')
        assert p1.id == p2.id

        ## uri is different to r1
        p2 = Place.get_or_create(uri='bar', label='foobar')
        assert p1.id != p2.id

        ## label is different to r1
        p2 = Place.get_or_create(uri='foo', label='barfoo')
        assert p1.id != p2.id

        ## both values are different
        p2 = Place.get_or_create(uri='bar', label='barfoo')
        assert p1.id != p2.id


def test_relates_to_person(db):
    RelatesToPerson = db.entities['RelatesToPerson']
    with orm.db_session:
        r1 = RelatesToPerson(uri='foo', label='foobar')
        assert r1.label == 'foobar'
        assert r1.uri == 'foo'


def test_relates_to_person_get_or_create(db):
    "Test get_or_create for RelatesToPerson."
    RelatesToPerson = db.entities['RelatesToPerson']
    with orm.db_session:
        r1 = RelatesToPerson(uri='foo', label='foobar')
        # same values as r1 must result in same ids
        r2 = RelatesToPerson.get_or_create(uri='foo', label='foobar')
        assert r1.id == r2.id

        ## uri is different to r1
        r2 = RelatesToPerson.get_or_create(uri='bar', label='foobar')
        assert r1.id != r2.id

        ## label is different to r1
        r2 = RelatesToPerson.get_or_create(uri='foo', label='barfoo')
        assert r1.id != r2.id

        ## both values are different
        r2 = RelatesToPerson.get_or_create(uri='bar', label='barfoo')
        assert r1.id != r2.id


def test_person_uri(db):
    PersonURI = db.entities['PersonURI']
    with orm.db_session:
        p1 = PersonURI(uri='foo')
        assert db.get('select count(*) from PersonURI') == 1
        assert p1.uri == 'foo'

def test_source_uri(db):
    SourceURI = db.entities['SourceURI']
    with orm.db_session:
        s1 = SourceURI(uri='foo')
        SourceURI(uri='bar')
        assert db.get('select count(*) from SourceURI') == 2
        assert s1.uri == 'foo'


def test_statement_uri(db):
    StatementURI = db.entities['StatementURI']
    with orm.db_session:
        s1 = StatementURI(uri='foo')
        StatementURI(uri='bar')
        assert db.get('select count(*) from StatementURI') == 2
        assert s1.uri == 'foo'


def test_referential_integrity(db, data1):
    "Persons and sources must not be deleted if used in any factoids."
    Factoid = db.entities['Factoid']
    with orm.db_session:
        data = data1['factoids'][0]

        # Create factoid and check if person exists as expected
        factoid = Factoid.create_from_ipif(data)
        p = factoid.person
        with pytest.raises(orm.ConstraintError):
            p.delete()
        s = factoid.source
        with pytest.raises(orm.ConstraintError):
            s.delete()

def _test_ro(db200final):
    "Make sure database db200final is read only."
    Factoid = db200final.entities['Factoid']
    with orm.db_session:
        f1 = Factoid['F00001']
        f1.createdBy = 'ffo'
        with pytest.raises(orm.OperationalError):
            db200final.commit()

def test_fix_datetime():
    assert database.fix_datetime("2015-08-25T18:30:29.181+02:00") == "2015-08-25T18:30:29"