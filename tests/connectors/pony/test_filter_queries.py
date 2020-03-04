"""Tests for the filter_queries module.
"""
import datetime

from pony import orm

from papilotte.connectors.pony import filter_queries


@orm.db_session
def test_source_query_empty(db200final):
    "If no filters are set query must contain all sources."
    query = filter_queries.source_query(db200final)
    assert query.count() == 100


@orm.db_session
def test_person_query_empty(db200final):
    "If no filters are set query must contain all persons."
    query = filter_queries.person_query(db200final)
    assert query.count() == 75


@orm.db_session
def test_statement_query_empty(db200final):
    "If no filters are set query must contain all statements."
    query = filter_queries.statement_query(db200final)
    assert query.count() == 600


@orm.db_session
def test_factoid_query_empty(db200final):
    "If no filters are set query must contain all statements."
    query = filter_queries.factoid_query(db200final)
    assert query.count() == 200


@orm.db_session
def test_source_query_source_id(db200final):
    "Test search paramter sourceId=."
    # ids are unique
    query = filter_queries.source_query(db200final, sourceId="S00057")
    assert query.count() == 1

    # sourceId search case sensitive
    query = filter_queries.source_query(db200final, sourceId="s00057")
    assert query.count() == 0

    # non existing id
    query = filter_queries.source_query(db200final, sourceId="S00057foofoo")
    assert query.count() == 0


@orm.db_session
def test_source_query_label(db200final):
    "Test search parameter label=."

    # search for exact match
    query = filter_queries.source_query(db200final, label="Source 00058")
    assert query.count() == 1

    # label searches are case insensitive
    query = filter_queries.source_query(db200final, label="source 00058")
    assert query.count() == 1

    # label searches for substring
    query = filter_queries.source_query(db200final, label="ource 0003")
    assert query.count() == 8


@orm.db_session
def test_source_query_fulltext(db200final):
    "Test search parameter s=."

    # exact case sensitive id
    query = filter_queries.source_query(db200final, s="S00058")
    assert query.count() == 1

    # exact case insensitive id
    query = filter_queries.source_query(db200final, s="s00058")
    assert query.count() == 1

    # substring of id
    query = filter_queries.source_query(db200final, s="s0005")
    assert query.count() == 10

    # exact, case sensitive label
    query = filter_queries.source_query(db200final, s="Source 00057")
    assert query.count() == 1

    # exact, case insensitive label
    query = filter_queries.source_query(db200final, s="source 00057")
    assert query.count() == 1

    # substring of label
    query = filter_queries.source_query(db200final, s="source 0005")
    assert query.count() == 8

    # uris are searched case sensitiv for exact matches
    query = filter_queries.source_query(db200final, s="https://example.com/sources/56a")
    assert query.count() == 1

    # bad case
    query = filter_queries.source_query(db200final, s="https://example.com/Sources/56a")
    assert query.count() == 0

    # substring must not match
    query = filter_queries.source_query(db200final, s="https://example.com/Sources")
    assert query.count() == 0


@orm.db_session
def test_person_query_person_id(db200final):
    "Test search parameter personId="
    # ids are unique
    query = filter_queries.person_query(db200final, personId="P00054")
    assert query.count() == 1

    # sourceId search case sensitive
    query = filter_queries.person_query(db200final, personId="p00054")
    assert query.count() == 0

    # non existing id
    query = filter_queries.person_query(db200final, personId="P00057foofoo")
    assert query.count() == 0


@orm.db_session
def test_person_query_fulltext(db200final):
    "Test search parameter p=."

    # exact case sensitive id
    query = filter_queries.person_query(db200final, p="P00058")
    assert query.count() == 1

    # exact case insensitive id
    query = filter_queries.person_query(db200final, p="p00058")
    assert query.count() == 1

    # substring of id
    query = filter_queries.person_query(db200final, p="p0005")
    assert query.count() == 10

    # uris are searched case sensitiv for exact matches
    query = filter_queries.person_query(db200final, p="https://example.com/persons/57a")
    assert query.count() == 1

    # bad case
    query = filter_queries.person_query(db200final, p="https://example.com/Persons/57a")
    assert query.count() == 0

    # substring must not match
    query = filter_queries.person_query(db200final, p="https://example.com/Persons")
    assert query.count() == 0


@orm.db_session
def test_factoid_query_factoid_id(db200final):
    "Test search parameter factoidId="
    # ids are unique
    query = filter_queries.factoid_query(db200final, factoidId="F00052")
    assert query.count() == 1

    # sourceId search case sensitive
    query = filter_queries.factoid_query(db200final, factoidId="f00052")
    assert query.count() == 0

    # non existing id
    query = filter_queries.factoid_query(db200final, factoidId="FFP00057foofoo")
    assert query.count() == 0


@orm.db_session
def test_factoid_query_fulltext(db200final):
    "Test search parameter f=."

    # exact case sensitive id
    query = filter_queries.factoid_query(db200final, f="F00058")
    assert query.count() == 1

    # exact case insensitive id
    query = filter_queries.factoid_query(db200final, f="f00058")
    assert query.count() == 1

    # substring of id
    query = filter_queries.factoid_query(db200final, f="f0005")
    assert query.count() == 10


def test_statement_query_stmt_id(db200final):
    "Test search parameter statementId="
    # ids are unique
    with orm.db_session:
        query = filter_queries.statement_query(db200final, statementId="Stmt00048")
        assert query.count() == 1

        # sourceId search case sensitive
        query = filter_queries.statement_query(db200final, statementId="stmt00051")
        assert query.count() == 0

        # non existing id
        query = filter_queries.statement_query(db200final, statementId="St00057foofoo")
        assert query.count() == 0


@orm.db_session
def test_statement_query_member_of(db200final):
    "Test search parameter memberOf="
    # search for full entry in label
    query = filter_queries.statement_query(db200final, memberOf="Group 00051")
    assert query.count() == 6
    # search for partial entry in label
    query = filter_queries.statement_query(db200final, memberOf="oup 00051")
    assert query.count() == 6
    # searching in label is case insensitive
    query = filter_queries.statement_query(db200final, memberOf="group 00051")
    assert query.count() == 6

    # searching in uri is case sensitive and only matches full matches
    query = filter_queries.statement_query(
        db200final, memberOf="https://example.com/groups/00053"
    )
    assert query.count() == 6
    # Upercase 'G' should not be found
    query = filter_queries.statement_query(
        db200final, memberOf="https://example.com/Groups/00053"
    )
    assert query.count() == 0
    # part of url should not be found
    query = filter_queries.statement_query(
        db200final, memberOf="https://example.com/groups/0005"
    )
    assert query.count() == 0


@orm.db_session
def test_stmt_uri_query(db200final):
    "Test the sub-query to find 'needle' in statement.uris."
    query = filter_queries.statement_uri_query(
        db200final, "https://example.com/statements/61a"
    )
    assert query.count() == 1


@orm.db_session
def test_stmt_place_query(db200final):
    "Test the sub-query to find 'needle' in statement.places."
    # exact
    query = filter_queries.statement_place_query(db200final, "Place 00053")
    assert query.count() == 12 
    # case insensive
    query = filter_queries.statement_place_query(db200final, "place 00053")
    assert query.count() == 12
    # substring
    query = filter_queries.statement_place_query(db200final, "ace 00053")
    assert query.count() == 12

    query = filter_queries.statement_place_query(
        db200final, "https://example.com/places/00053"
    )
    assert query.count() == 6
    # case insensitive
    query = filter_queries.statement_place_query(
        db200final, "https://example.com/Places/00053"
    )
    assert query.count() == 0
    # substring
    query = filter_queries.statement_place_query(
        db200final, "https://example.com/Places/00"
    )
    assert query.count() == 0


@orm.db_session
def test_stmt_relpers_query(db200final):
    "Test the sub-query to find 'needle' in statement.relatesToPerson."
    # exact
    query = filter_queries.statement_relpers_query(db200final, "Related person 00056")
    assert query.count() == 6
    # case insensive
    query = filter_queries.statement_relpers_query(db200final, "related person 00056")
    assert query.count() == 6
    # substring
    query = filter_queries.statement_relpers_query(db200final, "ted person 00056")
    assert query.count() == 6

    query = filter_queries.statement_relpers_query(
        db200final, "https://example.com/relatedpersons/00058"
    )
    assert query.count() == 3
    # case insensitive
    query = filter_queries.statement_relpers_query(
        db200final, "https://example.com/RELatedpersons/00058"
    )
    assert query.count() == 0
    # substring
    query = filter_queries.statement_relpers_query(
        db200final, "https://example.com/relatedpersons/00"
    )
    assert query.count() == 0


@orm.db_session
def test_statement_query_place(db200final):
    "Test search parameter place="
    # search for full entry in label
    query = filter_queries.statement_query(db200final, place="Place 00051")
    assert query.count() == 12
    # search for partial entry in label
    query = filter_queries.statement_query(db200final, place="lace 00051")
    assert query.count() == 12
    # searching in label is case insensitive
    query = filter_queries.statement_query(db200final, place="place 00051")
    assert query.count() == 12

    # searching in uri is case sensitive and only matches full matches
    query = filter_queries.statement_query(
        db200final, place="https://example.com/places/00053"
    )
    assert query.count() == 6
    # Upercase 'P' should not be found
    query = filter_queries.statement_query(
        db200final, place="https://example.com/Places/00053"
    )
    assert query.count() == 0
    # part of url should not be found
    query = filter_queries.statement_query(
        db200final, place="https://example.com/places/0005"
    )
    assert query.count() == 0


@orm.db_session
def test_statement_query_relpers(db200final):
    "Test search parameter relatesToPerson="
    # search for full entry in label
    query = filter_queries.statement_query(
        db200final, relatesToPerson="Related person 00056"
    )
    assert query.count() == 6
    # search for partial entry in label
    query = filter_queries.statement_query(db200final, relatesToPerson="ted person 00056")
    assert query.count() == 6
    # searching in label is case insensitive
    query = filter_queries.statement_query(
        db200final, relatesToPerson="related person 00056"
    )
    assert query.count() == 6

    # searching in uri is case sensitive and only matches full matches
    query = filter_queries.statement_query(
        db200final, relatesToPerson="https://example.com/relatedpersons/00058"
    )
    assert query.count() == 3
    # Upercase 'REL' should not be found
    query = filter_queries.statement_query(
        db200final, relatesToPerson="https://example.com/RELatedpersons/00058"
    )
    assert query.count() == 0
    # part of url should not be found
    query = filter_queries.statement_query(
        db200final, relatesToPerson="https://example.com/relatedpersons/"
    )
    assert query.count() == 0


@orm.db_session
def test_statement_query_role(db200final):
    "Test search parameter role="
    # search for full entry in label
    query = filter_queries.statement_query(db200final, role="Role 00051")
    assert query.count() == 6
    # search for partial entry in label
    query = filter_queries.statement_query(db200final, role="ole 00051")
    assert query.count() == 6
    # searching in label is case insensitive
    query = filter_queries.statement_query(db200final, role="role 00051")
    assert query.count() == 6

    # searching in uri is case sensitive and only matches full matches
    query = filter_queries.statement_query(
        db200final, role="https://example.com/roles/00053"
    )
    assert query.count() == 6
    # Upercase 'R' should not be found
    query = filter_queries.statement_query(
        db200final, role="https://example.com/Roles/00053"
    )
    assert query.count() == 0
    # part of url should not be found
    query = filter_queries.statement_query(
        db200final, role="https://example.com/roles/0005"
    )
    assert query.count() == 0


@orm.db_session
def test_statement_query_stmttype(db200final):
    "Test search parameter statementType="
    # search for full entry in label
    query = filter_queries.statement_query(db200final, statementType="Statement type 00061")
    assert query.count() == 6
    # search for partial entry in label
    query = filter_queries.statement_query(db200final, statementType="tatement type 00061")
    assert query.count() == 6
    # searching in label is case insensitive
    query = filter_queries.statement_query(db200final, statementType="statement type 00061")
    assert query.count() == 6

    # searching in uri is case sensitive and only matches full matches
    query = filter_queries.statement_query(
        db200final, statementType="https://example.com/statementtypes/00022"
    )
    assert query.count() == 12
    # Upercase 'ST' should not be found
    query = filter_queries.statement_query(
        db200final, statementType="https://example.com/STatementtypes/00022"
    )
    assert query.count() == 0
    # part of url should not be found
    query = filter_queries.statement_query(
        db200final, statementType="https://example.com/statementtypes/000"
    )
    assert query.count() == 0


@orm.db_session
def test_query_from(db200final):
    "Test search parameter from="
    query = filter_queries.statement_query(db200final, from_=datetime.date(1803, 3, 30))
    assert query.count() == 18


@orm.db_session
def test_query_to(db200final):
    "Test search parameter to="
    query = filter_queries.statement_query(db200final, to=datetime.date(1800, 6, 1))
    assert query.count() == 15


@orm.db_session
def test_query_from_to(db200final):
    "Test search parameter from= together with to="
    query = filter_queries.statement_query(
        db200final, from_=datetime.date(1800, 6, 1), to=datetime.date(1800, 7, 1)
    )
    assert query.count() == 21


@orm.db_session
def test_query_from_st(db200final):
    "Test search parameter st="
    # id
    query = filter_queries.statement_query(db200final, st="Stmt00048")
    assert query.count() == 1
    # date.label
    query = filter_queries.statement_query(db200final, st="Historical Date 00061")
    assert query.count() == 2
    query = filter_queries.statement_query(db200final, st="historical date 00061")
    assert query.count() == 2
    query = filter_queries.statement_query(db200final, st="torical date 00061")
    assert query.count() == 2
    # memberOf.label
    query = filter_queries.statement_query(db200final, st="Group 00061")
    assert query.count() == 6
    query = filter_queries.statement_query(db200final, st="group 0006")
    assert query.count() == 48
    query = filter_queries.statement_query(db200final, st="oup 0006")
    assert query.count() == 48
    # memberOf.uri
    query = filter_queries.statement_query(
        db200final, st="https://example.com/groups/00061"
    )
    assert query.count() == 3
    # name
    query = filter_queries.statement_query(db200final, st="Statement 00048")
    assert query.count() == 1
    query = filter_queries.statement_query(db200final, st="statement 00048")
    assert query.count() == 1
    query = filter_queries.statement_query(db200final, st="tement 00048")
    assert query.count() == 1
    # role.label
    query = filter_queries.statement_query(db200final, st="Role 00061")
    assert query.count() == 6
    query = filter_queries.statement_query(db200final, st="role 0006")
    assert query.count() == 48
    query = filter_queries.statement_query(db200final, st="le 00061")
    assert query.count() == 6
    # statementContent
    query = filter_queries.statement_query(db200final, st="Statement content 00061")
    assert query.count() == 3
    query = filter_queries.statement_query(db200final, st="statement CONTENT 00061")
    assert query.count() == 3
    query = filter_queries.statement_query(db200final, st="ment content 00061")
    assert query.count() == 3
    # statementtype.label
    query = filter_queries.statement_query(db200final, st="Statement type 00061")
    assert query.count() == 6
    query = filter_queries.statement_query(db200final, st="statement TYPE 00061")
    assert query.count() == 6
    query = filter_queries.statement_query(db200final, st="ement type 00061")
    assert query.count() == 6
    # statementType.uri
    query = filter_queries.statement_query(
        db200final, st="https://example.com/statementtypes/00021"
    )
    assert query.count() == 9
    # places.label
    query = filter_queries.statement_query(db200final, st="Place 00051")
    assert query.count() == 12
    query = filter_queries.statement_query(db200final, st="lace 00051")
    assert query.count() == 12
    query = filter_queries.statement_query(db200final, st="place 00051")
    assert query.count() == 12
    # places.uri
    query = filter_queries.statement_query(
        db200final, st="https://example.com/places/00053"
    )
    assert query.count() == 6
    # relatesToPersons.label
    query = filter_queries.statement_query(db200final, st="Related person 00056")
    assert query.count() == 6
    query = filter_queries.statement_query(db200final, st="ted person 00056")
    assert query.count() == 6
    query = filter_queries.statement_query(db200final, st="related person 00056")
    assert query.count() == 6
    # relatesToPersons.uri
    query = filter_queries.statement_query(
        db200final, st="https://example.com/relatedpersons/00058"
    )
    assert query.count() == 3
    # uris
    query = filter_queries.statement_query(
        db200final, st="https://example.com/statements/61a"
    )
    assert query.count() == 1
