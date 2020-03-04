"""A set of reusable query makers. 
These queries can be used as subqueries in the individual filter() methods 
of Connector objects
"""
import datetime

from pony import orm


def source_query(db, sourceId="", label="", s="", **other_filters):
    """Construct a (sub)query based on named filters.

    Returns a pony.query object containing all filters if they are set.
    The returned query can be used as variable within an other query.
    """
    Source = db.entities["Source"]
    query = orm.select(s for s in Source)
    if sourceId:
        query = query.filter(lambda source: source.id == sourceId)
    if label:
        query = query.filter(lambda source: label.lower() in source.label.lower())
    if s:  # fulltext search
        query = query.filter(
            lambda source: (
                s.lower() in source.id.lower()
                or s.lower() in source.label.lower()
                or s in source.uris.uri
            )
        )
    return query


def person_query(db, personId="", p="", **other_filters):
    """Construct a (sub)query based on named filters.

    Returns a pony.query object containing all filters if they are set.
    The returned query can be used as variable within an other query.
    """
    Person = db.entities["Person"]
    query = orm.select(p for p in Person)
    if personId:
        query = query.filter(lambda person: person.id == personId)
    if p:
        query = query.filter(
            lambda person: (p.lower() in person.id.lower() or p in person.uris.uri)
        )
    return query


def factoid_query(db, factoidId="", f="", **other_filters):
    """Construct a (sub)query based on named filters

    Returns a pon.query object countaing all filters if they are set.
    The returned query can be used as variable within an other query.
    """
    Factoid = db.entities["Factoid"]
    query = orm.select(f for f in Factoid)
    if factoidId:
        query = query.filter(lambda factoid: factoid.id == factoidId)
    if f:  # TODO: Possibly f should search in all child elements?
        query = query.filter(lambda factoid: f.lower() in factoid.id.lower())
    return query


def statement_uri_query(db, needle):
    """Filter Statements by searching for mathich uris.

    Return value can be used as subquery.
    """
    Statement = db.entities["Statement"]
    query = orm.select(st for st in Statement for uri in st.uris if uri.uri == needle)
    return query


def statement_place_query(db, needle):
    """Filter Statements by searching in statement.places for needle. 

    `needle` is searched case insensitive as substring in label and
    case sensitive as full string in uri.

    Returns a pony.query object which can be as sub query.
    """
    Statement = db.entities["Statement"]
    query = orm.select(st for st in Statement
        for p in st.places
        if needle.lower() in p.label.lower() or p.uri == needle
    )
    return query


def statement_relpers_query(db, needle):
    """Filter Statements by searching in statement.relatesToPerson for needle. 

    `needle` is searched case insensitive as substring in label and
    case sensitive as full string in uri.

    Returns a pony.query object which can be as sub query.
    """
    Statement = db.entities["Statement"]
    query = orm.select(
        st
        for st in Statement
        for rp in st.relatesToPersons
        if needle.lower() in rp.label.lower() or rp.uri == needle
    )
    return query


def statement_query(
    db,
    statementId="",
    st="",
    from_="",
    memberOf="",
    name="",
    place="",
    relatesToPerson="",
    role="",
    statementContent="",
    statementType="",
    to="",
    **other_filters
):
    """Construct a (sub)query based on named filters

    Returns a pony.query object countaing all filters if they are set.
    The returned query can be used as variable within an other query.
    """
    Statement = db.entities["Statement"]
    query = orm.select(st for st in Statement)
    if statementId:
        query = query.filter(lambda stmt: stmt.id == statementId)
    if st:
        subquery_places = statement_place_query(db, st)
        subquery_relpers = statement_relpers_query(db, st)
        subquery_uris = statement_uri_query(db, st)
        query = query.filter(
            lambda stmt: st.lower() in stmt.id.lower()
            or st.lower() in stmt.date.label.lower()
            or st.lower() in stmt.memberOf.label.lower()
            or stmt.memberOf.uri == st
            or st.lower() in stmt.name.lower()
            or st.lower() in stmt.role.label.lower()
            or stmt.role.uri == st
            or st.lower() in stmt.statementContent.lower()
            or st.lower() in stmt.statementType.label.lower()
            or stmt.statementType.uri == st
            or stmt in subquery_places
            or stmt in subquery_relpers
            or stmt in subquery_uris
        )
    if from_:
        query = query.filter(lambda stmt: stmt.date.sortDate >= from_)
    if memberOf:
        query = query.filter(
            lambda stmt: memberOf.lower() in stmt.memberOf.label.lower()
            or stmt.memberOf.uri == memberOf
        )
    if name:
        query = query.filter(lambda stmt: name.lower() in stmt.name.lower())
    if place:
        subquery = statement_place_query(db, place)
        query = query.filter(lambda stmt: stmt in subquery)
    if relatesToPerson:
        subquery = statement_relpers_query(db, relatesToPerson)
        query = query.filter(lambda stmt: stmt in subquery)
    if role:
        query = query.filter(
            lambda stmt: role.lower() in stmt.role.label.lower()
            or stmt.role.uri == role
        )
    if statementContent:
        query = query.filter(
            lambda stmt: statementContent.lower() in stmt.statementContent.lower()
        )
    if statementType:
        query = query.filter(
            lambda stmt: statementType.lower() in stmt.statementType.label.lower()
            or stmt.statementType.uri == statementType
        )
    if to:
        query = query.filter(lambda stmt: stmt.date.sortDate <= to)
    return query
