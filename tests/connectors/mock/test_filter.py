"""Test the filter module.

The filter module simulates the filter functionality for
all filter paramaters.
"""
# pylint: disable=len-as-condition
from papilotte.connectors.mock.filter import (
    date_contains_str,
    date_is_equal_or_after,
    date_is_equal_or_before,
    labeled_uri_contains,
    labeled_uri_list_contains,
    person_contains,
    source_contains,
)
from papilotte.connectors.mock.mockdate import MockDate


def test_filter_with_empty_filters(mockdata, qfilter):
    """If not filter params a used, make sure that all factoids are returned.
    """
    assert len(qfilter.filter(mockdata)) == 100


def test_filter_by_factoid_id(mockdata, qfilter):
    "Test if filtering by factoidId= works"
    assert len(qfilter.filter(mockdata, factoidId="Factoid 001")) == 1
    assert len(qfilter.filter(mockdata, factoidId="Factoid")) == 0


def test_filter_by_person_id(mockdata, qfilter):
    "Test if filtering by personId= works"
    assert len(qfilter.filter(mockdata, personId="Person 001")) == 7
    assert len(qfilter.filter(mockdata, personId="Person")) == 0


def test_filter_by_statement_id(mockdata, qfilter):
    "Test if filtering by statementId= works"
    assert len(qfilter.filter(mockdata, statementId="F1S1")) == 1
    assert len(qfilter.filter(mockdata, statementId="S1")) == 0


def test_filter_by_source_id(mockdata, qfilter):
    "Test if filtering by sourceId= works"
    assert len(qfilter.filter(mockdata, sourceId="Source 010")) == 4
    assert len(qfilter.filter(mockdata, sourceId="Source")) == 0


def test_filter_by_person(mockdata, qfilter):
    "Test case insensitive fulltext search on most elements of person."
    res = qfilter.filter(mockdata, p="Person 001")
    assert len(res) == 7
    res = qfilter.filter(mockdata, p="Person 01")
    # This kind of search should find substrings in @id. So if searching for
    # "Person 1" brings up "Person 10", this works
    assert "Person 010" in [factoid["person"]["@id"] for factoid in res]

    # is search case insensitive?
    assert len(qfilter.filter(mockdata, p="person 001")) == 7

    # Are uris found?
    assert len(qfilter.filter(mockdata, p="http://example.com/5")) == 86
    # no substring search in uris!
    assert len(qfilter.filter(mockdata, p="http://example.com/")) == 0


def test_by_person_mininimal_data(minimal_mockdata, qfilter):
    """Test filtering by p= if factoid only contains required properties.
    
    This will bring up potential KeyErrors.
    """
    res = qfilter.filter(minimal_mockdata, p='p1')
    assert len(res) == 1
    res = qfilter.filter(minimal_mockdata, p='xxxxxx')
    assert not res


def test_filter_by_source(mockdata, qfilter):
    "Test case insensitive fulltext search on most elements of source."
    # find in @id
    res = qfilter.filter(mockdata, s="Source 01")
    assert len(res) == 40
    # This kind of search should find substrings in @id. So if searching for
    # "Source 1" brings up "Source 10", this works
    assert "Source 010" in [factoid["source"]["@id"] for factoid in res]

    # is search case insensitive?
    assert len(qfilter.filter(mockdata, s="source 001")) == 4

    # find in label
    res = qfilter.filter(mockdata, s="Label Source 01")
    assert len(res) == 40
    # if 'Label Source 10' in res, search for substring works
    assert "Label Source 010" in [factoid["source"]["label"] for factoid in res]

    # is search case insensitive?
    assert len(qfilter.filter(mockdata, s="source 001")) == 4

    # find in uris
    assert len(qfilter.filter(mockdata, s="http://example.com/5")) == 92
    # no substring search in uris!
    assert len(qfilter.filter(mockdata, s="http://example.com/")) == 0


def test_by_source_mininimal_data(minimal_mockdata, qfilter):
    """Test filtering by s= if factoid only contains required properties.
    
    This will bring up potential KeyErrors.
    """
    res = qfilter.filter(minimal_mockdata, s='s1')
    assert len(res) == 1
    res = qfilter.filter(minimal_mockdata, s='xxxxxx')
    assert not res

def test_filter_by_statement_statement(mockdata, qfilter):
    "Test filter by  statement: @id."
    assert len(qfilter.filter(mockdata, st="F8S1")) == 1
    assert len(qfilter.filter(mockdata, st="f8s1")) == 1
    assert len(qfilter.filter(mockdata, st="f8")) == 11


def test_by_statement_mininimal_data(minimal_mockdata, qfilter):
    """Test filtering by st= if factoid only contains required properties.
    
    This will bring up potential KeyErrors.
    """
    res = qfilter.filter(minimal_mockdata, st='st1')
    assert len(res) == 1
    res = qfilter.filter(minimal_mockdata, st='xxx2')
    assert not res == 0


def test_filter_by_statement_uri(mockdata, qfilter):
    "Test filter by  statement: uri."
    assert (
        len(qfilter.filter(mockdata, st="http://example.com/statements/8"))
        == 97 
    )
    # no substring search in uri
    assert (
        len(qfilter.filter(mockdata, st="http://example.com/statements/"))
        == 0
    )

def test_filter_by_statement_label(mockdata, qfilter):
    "Test filter by  statement: statementType."
    # search statementType label
    assert len(qfilter.filter(mockdata, st="Statement type 5_1")) == 5
    assert len(qfilter.filter(mockdata, st="Statement type xy")) == 0

    # filter by statementType uri
    assert (
        len(qfilter.filter(mockdata, st="http://example.com/statement_type/5/1")) == 5
    )

def test_filter_by_statement_name(mockdata, qfilter):
    "Test filter by statement: name."
    assert len(qfilter.filter(mockdata, st="Name 5")) == 10
    assert len(qfilter.filter(mockdata, st="ame 5")) == 10
    assert len(qfilter.filter(mockdata, st="name 5")) == 10
    assert len(qfilter.filter(mockdata, st="nam 5")) == 0

def test_filter_by_statement_role(mockdata, qfilter):
    "Test filter by statement: role."
    # search in role label
    assert len(qfilter.filter(mockdata, st="Role 4_1")) == 7
    assert len(qfilter.filter(mockdata, st="role 4_1")) == 7
    assert len(qfilter.filter(mockdata, st="ole 4_1")) == 7
    assert len(qfilter.filter(mockdata, st="Role xxx1_1")) == 0

    # search in role uri
    assert len(qfilter.filter(mockdata, st="http://example.com/role/4/1")) == 7
    assert len(qfilter.filter(mockdata, st="http://example.com/role/4/")) == 0
    assert len(qfilter.filter(mockdata, st="http://example.com/Role/4/1")) == 0

def test_filter_by_statement_date(mockdata, qfilter):
    "Test filter by statement: date."
    assert len(qfilter.filter(mockdata, st="3 March 1803")) == 1
    assert len(qfilter.filter(mockdata, st="1803")) == 2
    assert len(qfilter.filter(mockdata, st="march")) == 4
    assert len(qfilter.filter(mockdata, st="1803-03-03")) == 1

def test_filter_by_statement_places(mockdata, qfilter):
    "Test filter by statement: places."
    assert len(qfilter.filter(mockdata, st="Place 4_1")) == 2
    assert len(qfilter.filter(mockdata, st="4_1")) == 27
    assert len(qfilter.filter(mockdata, st="http://example.com/place/4/1")) == 2
    assert len(qfilter.filter(mockdata, st="http://example.com/place/4/")) == 0

def test_filter_by_statement_relates_to_persons(mockdata, qfilter):
    "Test filter by statement: relatesToPersons."
    assert len(qfilter.filter(mockdata, st="Related Person 4_1")) == 3
    assert len(qfilter.filter(mockdata, st="Related Person 4")) == 13
    assert len(qfilter.filter(mockdata, st="4")) == 50
    assert (
        len(qfilter.filter(mockdata, st="http://example.com/related_person/4/1")) == 3
    )
    assert len(qfilter.filter(mockdata, st="http://example.com/related_person/4/")) == 0

def test_filter_by_statement_member_of(mockdata, qfilter):
    "Test filter by statement: memberOf."
    assert len(qfilter.filter(mockdata, st="Member of 16_1")) == 3
    assert len(qfilter.filter(mockdata, st="2_1")) == 27
    assert len(qfilter.filter(mockdata, st="http://example.com/member_of/16/1")) == 3
    assert len(qfilter.filter(mockdata, st="http://example.com/member_of/16/")) == 0

def test_filter_by_statement_statement_content(mockdata, qfilter):
    "Test filter by statement: statementContent."
    assert len(qfilter.filter(mockdata, st="Statement Content 25")) == 4
    assert len(qfilter.filter(mockdata, st="statement content 25")) == 4
    res = qfilter.filter(mockdata, st="Statement Content 2")
    assert len(res) == 28
    statement_contents = []
    for factoid in res:
        stmt = factoid['statement']
        if 'statementContent' in stmt:
            statement_contents.append(stmt['statementContent'])
    assert "Statement content 25" in statement_contents


def test_filter_by_factoid(mockdata, qfilter):
    "Test fulltext search in all of factoid."
    assert len(qfilter.filter(mockdata, f="Factoid 029")) == 1
    assert len(qfilter.filter(mockdata, f="F3S1")) == 1
    assert len(qfilter.filter(mockdata, f="Factoid 00")) == 9


def test_filter_by_statement_content(mockdata, qfilter):
    "Test searching in statement statement.statementContent."
    assert len(qfilter.filter(mockdata, statementContent="Statement content 8")) == 4
    assert len(qfilter.filter(mockdata, statementContent="statement content 8")) == 4
    assert len(qfilter.filter(mockdata, statementContent="content 8")) == 4


def test_relates_to_person(mockdata, qfilter):
    "Test searching in statement.relatesToPerson."
    assert len(qfilter.filter(mockdata, relatesToPerson="Related person 18_1")) == 2
    assert len(qfilter.filter(mockdata, relatesToPerson="related person 18_1")) == 2
    assert len(qfilter.filter(mockdata, relatesToPerson="person 18_1")) == 2
    assert len(qfilter.filter(mockdata, relatesToPerson="person 18_x")) == 0

    assert (
        len(
            qfilter.filter(
                mockdata, relatesToPerson="http://example.com/related_person/18/1"
            )
        )
        == 2
    )
    assert (
        len(
            qfilter.filter(
                mockdata, relatesToPerson="http://example.com/related_person/18/"
            )
        )
        == 0
    )


def test_filter_by_member_of(mockdata, qfilter):
    "Test searching in statement.memberOf"
    assert len(qfilter.filter(mockdata, memberOf="Member of 20_1")) == 3
    assert len(qfilter.filter(mockdata, memberOf="MEMBER OF 20_1")) == 3
    assert len(qfilter.filter(mockdata, memberOf="of 20_1")) == 3
    assert len(qfilter.filter(mockdata, memberOf="of 20_x")) == 0

    assert (
        len(qfilter.filter(mockdata, memberOf="http://example.com/member_of/20/1"))
        == 3
    )
    assert (
        len(qfilter.filter(mockdata, memberOf="http://example.com/member_of/20/")) == 0
    )


def test_filter_by_role(mockdata, qfilter):
    "Test searching in statement.role."
    assert len(qfilter.filter(mockdata, role="Role 14_1")) == 6
    assert len(qfilter.filter(mockdata, role="role 14_1")) == 6
    assert len(qfilter.filter(mockdata, role="le 14_1")) == 6
    assert len(qfilter.filter(mockdata, role="le 14_x")) == 0
    assert len(qfilter.filter(mockdata, role="http://example.com/role/14/1")) == 6
    assert len(qfilter.filter(mockdata, role="http://example.com/role/14/")) == 0


def test_filter_by_name(mockdata, qfilter):
    "Test searching in statement.name."
    assert len(qfilter.filter(mockdata, name="Name 9")) == 10
    assert len(qfilter.filter(mockdata, name="name 9")) == 10
    assert len(qfilter.filter(mockdata, name="me 9")) == 10
    assert len(qfilter.filter(mockdata, name="me xyz")) == 0


def test_filter_by_place(mockdata, qfilter):
    "Test  searching in statement.place."
    assert len(qfilter.filter(mockdata, place="Place 47_1")) == 2
    assert len(qfilter.filter(mockdata, place="place 47_1")) == 2
    assert len(qfilter.filter(mockdata, place="ace 47_1")) == 2
    assert len(qfilter.filter(mockdata, place="Place 47_73737")) == 0

    assert len(qfilter.filter(mockdata, place="http://example.com/place/47/1")) == 2
    assert len(qfilter.filter(mockdata, place="http://example.com/place/47/")) == 0


def test_filter_by_from(mockdata, qfilter):
    "Test filter_by_from."
    assert len(qfilter.filter(mockdata, from_="1848-06-12")) == 1


def test_filter_by_to(mockdata, qfilter):
    "Test filter_by_to"
    assert len(qfilter.filter(mockdata, to_="1802-12-31")) == 4


def test_filter_by_multiple_filters(mockdata, qfilter):
    "Test if using multiple filters works."
    res = qfilter.filter(mockdata, p="http://example.com/6", sourceId="Source 011")
    assert len(res) == 3

    res = qfilter.filter(
        mockdata,
        p="http://example.com/6",
        sourceId="Source 011",
        statementId="F86S1",
    )
    assert len(res) == 1
    assert res[0]["@id"] == "Factoid 086"


def test_labeled_uri_contains():
    "Test the helper function labeled_uri_contains."
    data = {"label": "The Label String", "uri": "http://example.com/1/2/3"}
    # search full label
    assert labeled_uri_contains(data, "The Label String")
    # search substring
    assert labeled_uri_contains(data, "Label")
    # search in label is case insensitive
    assert labeled_uri_contains(data, "label")

    # search uri
    assert labeled_uri_contains(data, "http://example.com/1/2/3")
    # no substring search in uri
    assert not labeled_uri_contains(data, "http://example.com/1/2")
    # no case insensitive search in uri
    assert not labeled_uri_contains(data, "http://Example.com/1/2/3")

    # missing properties
    data = {"label": "The Label String"}
    assert labeled_uri_contains(data, "The Label String")
    data = {"uri": "http://example.com/1/2/3"}
    assert labeled_uri_contains(data, "http://example.com/1/2/3")

    # empty data
    data = {}
    assert not labeled_uri_contains(data, "The Label String")
    assert not labeled_uri_contains(data, "http://example.com/1/2/3")

    # None
    data = None
    assert not labeled_uri_contains(data, "The Label String")
    assert not labeled_uri_contains(data, "http://example.com/1/2/3")


def test_date_contains_str():
    "Test the date_contains function."
    data = {"label": "2 January 1645", "sortdate": "1645-01-02"}
    assert date_contains_str(data, "2 January 1645")
    assert date_contains_str(data, "2 january 1645")
    assert date_contains_str(data, "january")

    assert date_contains_str(data, "1645-01-02")
    assert date_contains_str(data, "1645-01")
    assert date_contains_str(data, "1645")
    assert date_contains_str(data, "1")


def test_date_is_equal_or_after():
    "Test if sortdate is equal or after a given date."
    data = {"sortdate": "1655-01-01"}
    assert date_is_equal_or_after(data, MockDate("1655-01-01"))
    assert not date_is_equal_or_after(data, MockDate("1655-01-02"))
    assert date_is_equal_or_after(data, MockDate("1654-01-02"))

    data = {"sortdate": "-300-01-01"}
    assert date_is_equal_or_after(data, MockDate("-301-01-01"))
    assert not date_is_equal_or_after(data, MockDate("-299-01-01"))

    data = {}
    assert not date_is_equal_or_after(data, MockDate("1654-01-02"))


def test_date_is_equal_or_before():
    "Test if sortdate is equal or before a specific date"
    data = {"sortdate": "1655-01-01"}
    assert date_is_equal_or_before(data, MockDate("1655-01-01"))
    assert date_is_equal_or_before(data, MockDate("1655-01-02"))
    assert not date_is_equal_or_before(data, MockDate("1654-01-02"))


def test_person_contains():
    """Test function person_contains."""
    person = {
        "@id": "Person 2",
        "uris": ["http://example.com/1", "http://example.com/2"],
    }
    assert person_contains(person, "Person 2")
    assert person_contains(person, "Person")
    assert person_contains(person, "person")
    assert not person_contains(person, "person 99")
    assert person_contains(person, "http://example.com/2")
    assert not person_contains(person, "http://example.com/")


def test_source_contains():
    "Test fulltext source against a single source"
    source = {
        "@id": "Source 2345",
        "label": "Label Source 2345",
        "uris": ["http://example.com/1/2/3", "http://example.com/2/4/5"],
    }
    assert source_contains(source, "Source 2345")
    assert source_contains(source, "source 2345")
    assert source_contains(source, "2345")
    assert not source_contains(source, "xyz")

    assert source_contains(source, "Label Source 2345")
    assert source_contains(source, "label source 2345")
    assert source_contains(source, "Label")

    assert source_contains(source, "http://example.com/1/2/3")
    assert not source_contains(source, "http://example.com/1/2/")


def test_labeled_uri_list_contains():
    """Test dictionaries which contain a label property an a uris property
       which is a list of uris
    """
    data = [
        {"label": "Label for 123", "uri": "http://example.com/1/2/3"},
        {"label": "Label for 124"},
    ]
    assert labeled_uri_list_contains(data, "Label for 123")
    assert labeled_uri_list_contains(data, "Label for 124")
    assert labeled_uri_list_contains(data, "Label for ")
    assert labeled_uri_list_contains(data, "http://example.com/1/2/3")
    assert not labeled_uri_list_contains(data, "http://example.com/1/2/")
