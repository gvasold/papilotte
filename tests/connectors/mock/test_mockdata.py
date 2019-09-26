"""Test creation of mock data.
"""


import datetime

from papilotte.connectors.mock import mockdata


def test_generate_person():
    "Make sure generate_person() doesn not create more than 15 different persons."
    num_of_different_objects = 15
    generator = mockdata.generate_person(num_of_different_objects)
    objects = {}
    for _ in range(num_of_different_objects * 10):
        obj = next(generator)
        buf = objects.get(obj["@id"], [])
        buf.append(obj)
        objects[obj["@id"]] = buf
    for pid in objects:
        assert len(objects[pid]) == 10

    # make sure persons with same pid contain same data
    for pid, objlist in objects.items():
        last_obj = None
        for obj in objlist:
            if last_obj is None:
                last_obj = obj
            else:
                assert last_obj == obj


def test_generate_source():
    "Make sure generate_source() does not create more than 15 different sources."
    num_of_different_objects = 25
    generator = mockdata.generate_source(num_of_different_objects)
    objects = {}

    for _ in range(num_of_different_objects * 10):
        obj = next(generator)
        buf = objects.get(obj["@id"], [])
        buf.append(obj)
        objects[obj["@id"]] = buf
    for pid in objects:
        assert len(objects[pid]) == 10

    # make sure sources with sam pid contain same data
    for pid, objlist in objects.items():
        last_obj = None
        for obj in objlist:
            if last_obj is None:
                last_obj = obj
            else:
                assert last_obj == obj


def test_generate_statement():
    "Make sure generate_statement() works as expected."
    factoid = {
        "@id": "Factoid 1",
        "createdWhen": "2019-07-21",
        "createdBy": "User 1",
        "modifiedWhen": "2019-10-12",
        "modifiedBy": "User 2",
    }
    generator = mockdata.generate_statement(factoid, 1)
    for i in range(5):
        stmt = next(generator)
        assert stmt["@id"] == "F1S%d" % (i + 1)
        assert stmt["createdBy"] == factoid["createdBy"]
        assert stmt["createdWhen"] == factoid["createdWhen"]
        assert stmt["modifiedBy"] == factoid["modifiedBy"]
        assert stmt["modifiedWhen"] == factoid["modifiedWhen"]


def test_generate_factoid():
    """Test the factoid generator.
    """
    generator = mockdata.generate_factoid()
    for i in range(100):
        factoid = next(generator)
        assert factoid["@id"] == "Factoid %03d" % (i + 1)
        assert "Person" in factoid["person"]["@id"]
        assert "Source" in factoid["source"]["@id"]
        assert 'statement' in factoid
        assert factoid["statement"]["@id"] == "F%dS1" % (i + 1)


def test_make_label_objects():
    "Make sure simple object consisting of a label and an uri or created as expected."
    for counter in (1, 4):
        objects = mockdata.make_label_objects(3, "xxx", counter)
        for i, obj in enumerate(objects):
            assert obj["label"] == "Xxx %d_%d" % (counter, i + 1)
            assert obj["uri"] == "http://example.com/xxx/%d/%d" % (counter, i + 1)


def test_make_date():
    "Make date generates a dict consisting of a date-label and a date string."
    # make_date might return an empty dict
    assert mockdata.make_date(0) is None
    assert mockdata.make_date(1) == {"label": "1801", "sortdate": "1801"}
    assert mockdata.make_date(2) == {"label": "February 1802", "sortdate": "1802-02"}
    assert mockdata.make_date(3) == {"label": "3 March 1803", "sortdate": "1803-03-03"}
    assert mockdata.make_date(5) is None
    assert mockdata.make_date(6) == {"label": "1806", "sortdate": "1806"}
    assert mockdata.make_date(7) == {"label": "July 1807", "sortdate": "1807-07"}
    assert mockdata.make_date(8) == {
        "label": "8 August 1808",
        "sortdate": "1808-08-08",
    }
    assert mockdata.make_date(9) == {}


def test_make_date_distribution():
    "Check if dates are equally distributed in mockdata."
    counter = {}
    for i in range(1000):
        data = mockdata.make_date(i)
        if data is None:
            counter["None"] = counter.get("None", 0) + 1
        elif data == {}:
            counter["empty"] = counter.get("empty", 0) + 1
        elif data["sortdate"].count("-") == 0:
            counter["yyyy"] = counter.get("yyyy", 0) + 1
        elif data["sortdate"].count("-") == 1:
            counter["yyyy-mm"] = counter.get("yyyy-mm", 0) + 1
        elif data["sortdate"].count("-") == 2:
            counter["yyyy-mm-dd"] = counter.get("yyyy-mm-dd", 0) + 1
    assert counter["None"] == counter["empty"]
    assert counter["None"] == counter["yyyy"]
    assert counter["None"] == counter["yyyy-mm"]
    assert counter["None"] == counter["yyyy-mm-dd"]


def test_uris():
    "Test the mockdata get_uri function."
    assert mockdata.get_uris(1) == ["http://example.com/1", "http://example.com/2"]
    assert mockdata.get_uris(2) == [
        "http://example.com/1",
        "http://example.com/2",
        "http://example.com/3",
        "http://example.com/4",
        "http://example.com/5",
        "http://example.com/6",
    ]
    assert mockdata.get_uris(3) == [
        "http://example.com/1",
        "http://example.com/2",
        "http://example.com/3",
        "http://example.com/4",
    ]


def test_get_modifier_distribution():
    """Check if distribution of modifier names is close to equal and if
    there are exactly 3 modifiers.
    """
    counter = {}
    for i in range(999):
        modifier = mockdata.get_modifier(i)
        counter[modifier] = counter.get(modifier, 0) + 1
    assert counter["Modifier 1"] == counter["Modifier 2"]
    assert counter["Modifier 1"] == counter["Modifier 3"]


def test_get_modifer():
    "Test creation order of get_modifier()."
    assert mockdata.get_modifier(1) == "Modifier 3"
    assert mockdata.get_modifier(2) == "Modifier 1"
    assert mockdata.get_modifier(3) == "Modifier 2"
    assert mockdata.get_modifier(4) == "Modifier 3"
    assert mockdata.get_modifier(5) == "Modifier 1"
    assert mockdata.get_modifier(6) == "Modifier 2"


def test_get_creator_distribution():
    """Check if distribution of creator names is close to equal and if
    there are exactly 3 creators.
    """
    counter = {}
    for i in range(1000):
        modifier = mockdata.get_creator(i)
        counter[modifier] = counter.get(modifier, 0) + 1
    assert counter["Creator 1"] == counter["Creator 2"]
    assert counter["Creator 1"] == counter["Creator 3"]
    assert counter["Creator 1"] == counter["Creator 4"]
    assert counter["Creator 1"] == counter["Creator 5"]


def test_get_creator():
    "Test creation order of get_creator()."
    for i in range(1, 6):
        assert mockdata.get_creator(i) == "Creator %d" % i


def test_get_datetime():
    "Test the mockdata get_date function."
    expected = [
        "2000-01-01T00:00:00+02:00",
        "2000-01-02T10:17:36+02:00",
        "2000-01-03T20:35:12+02:00",
        "2000-01-05T06:52:48+02:00",
        "2000-01-06T17:10:24+02:00",
        "2000-01-08T03:28:00+02:00",
        "2000-01-09T13:45:36+02:00",
        "2000-01-11T00:03:12+02:00",
        "2000-01-12T10:20:48+02:00",
        "2000-01-13T20:38:24+02:00"
    ]
    base_date = datetime.datetime(2000, 1, 1)
    for i in range(10):
        assert mockdata.get_datetime(base_date, i) == expected[i]


def test_get_datetime_with_offset():
    "Test if getting a date with offset works."
    expected = [
        "2000-01-01T00:00:00+02:00",
        "2000-01-03T08:30:56+02:00",
        "2000-01-07T13:28:32+02:00",
        "2000-01-13T14:52:48+02:00",
        "2000-01-21T12:43:44+02:00",
        "2000-01-08T03:28:00+02:00",
        "2000-01-15T03:05:36+02:00",
        "2000-01-23T23:09:52+02:00",
        "2000-02-03T15:40:48+02:00",
        "2000-02-16T04:38:24+02:00",
        "2000-01-15T06:56:00+02:00",
        "2000-01-26T21:40:16+02:00",
        "2000-02-09T08:51:12+02:00",
        "2000-02-24T16:28:48+02:00",
        "2000-03-12T20:33:04+02:00",
        "2000-01-22T10:24:00+02:00",
        "2000-02-07T16:14:56+02:00",
        "2000-02-25T18:32:32+02:00",
        "2000-03-16T17:16:48+02:00",
        "2000-04-07T12:27:44+02:00"
    ]
    base_date = datetime.datetime(2000, 1, 1)
    for i in range(20):
        assert mockdata.get_datetime(base_date, i, True) == expected[i]


def test_mod_time_after_creation_time():
    "Assert modification cannot be earlier than creation"
    base_date = datetime.datetime(2000, 1, 1)
    for i in range(1000):
        creation_time = mockdata.get_datetime(base_date, i)
        modification_time = mockdata.get_datetime(base_date, i, True)
        assert creation_time <= modification_time


def test_idempotence():
    "Generate a mock data set multiple times and make sure they are identical"

    def make_factoids(num):
        generated_factoids = []
        generator = mockdata.generate_factoid()
        for _ in range(num):
            generated_factoids.append(next(generator))
        return generated_factoids

    data_to_compare = make_factoids(250)
    for _ in range(10):
        assert data_to_compare == make_factoids(250)


def test_make_factoids():
    "make_factoids is a convenience function to create test data."
    assert len(mockdata.make_factoids(15)) == 15
