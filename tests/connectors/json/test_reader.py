"""Unit tests for the reader module of connector.json
"""
import json
import os
import tempfile

from papilotte.connectors.json.reader import (fix_metadata, fix_metadata_date,
                                              read_json_file, get_cache_file_name)
from papilotte.connectors.mock.mockdata import make_factoids


def test_fix_metadata_date_keep_correct_data():
    "Chec if function does not make changes to a correct date."
    res = fix_metadata_date("2015-02-25", "2020-01-01")
    assert res == "2015-02-25"


def test_fix_metadata_date_missing_date():
    "Check if missing date is replaced by default_date"
    res = fix_metadata_date(None, "2020-01-01")
    assert res == "2020-01-01"


def test_fix_metadata_date_timestamp():
    "Chec if a full timestamp is replaced by a data."
    res = fix_metadata_date("2015-02-25T14:22:132.185+02:00", "2020-01-01")
    assert res == "2015-02-25"


def test_fix_metadata_minimal_data():
    "Test if metadata for a single factoid is repaired."
    factoid = {
        "createdWhen": "2015-03-17",
        "createdBy": "foo",
        "source": {},
        "person": {},
        "statement": {},
    }
    res = fix_metadata(factoid, "user@example.com", "1999-02-02")
    assert res["createdWhen"] == "2015-03-17"
    assert res["createdBy"] == "foo"
    assert res["modifiedWhen"] == "2015-03-17"
    assert res["modifiedBy"] == "foo"
    stmt = res["statement"]
    assert stmt["createdWhen"] == "2015-03-17"
    assert stmt["createdBy"] == "foo"
    assert stmt["modifiedWhen"] == "2015-03-17"
    assert stmt["modifiedBy"] == "foo"
    src = res["source"]
    assert src["createdWhen"] == "2015-03-17"
    assert src["createdBy"] == "foo"
    assert src["modifiedWhen"] == "2015-03-17"
    assert src["modifiedBy"] == "foo"
    pers = res["person"]
    assert pers["createdWhen"] == "2015-03-17"
    assert pers["createdBy"] == "foo"
    assert pers["modifiedWhen"] == "2015-03-17"
    assert pers["modifiedBy"] == "foo"


def test_fix_metadata_missing_data():
    "Test if metadata for a single factoid is repaired if no metadata was provided."
    factoid = {"source": {}, "person": {}, "statement": {}}
    res = fix_metadata(factoid, "user@example.com", "1999-02-02")
    assert res["createdWhen"] == "1999-02-02"
    assert res["createdBy"] == "user@example.com"
    assert res["modifiedWhen"] == "1999-02-02"
    assert res["modifiedBy"] == "user@example.com"


def test_fix_metadata_mixed_data():
    "Test if metadata for a single factoid is repaired if only some data is missing."
    factoid = {
        "createdWhen": "2015-03-17",
        "createdBy": "foo",
        "source": {"createdWhen": "2015-03-18", "createdBy": "bar"},
        "person": {
            "createdWhen": "2015-03-19",
            "createdBy": "foobar",
            "modifiedWhen": "2015-04-19",
            "modifiedBy": "foobarfoo",
        },
        "statement": {"createdWhen": "1915-03-19T12:12:44.156+3:00"},
    }
    res = fix_metadata(factoid, "user@example.com", "1999-02-02")
    assert res["createdWhen"] == "2015-03-17"
    assert res["createdBy"] == "foo"
    assert res["modifiedWhen"] == "2015-03-17"
    assert res["modifiedBy"] == "foo"
    stmt = res["statement"]
    assert stmt["createdWhen"] == "1915-03-19"
    assert stmt["createdBy"] == "foo"
    assert stmt["modifiedWhen"] == "1915-03-19"
    assert stmt["modifiedBy"] == "foo"
    src = res["source"]
    assert src["createdWhen"] == "2015-03-18"
    assert src["createdBy"] == "bar"
    assert src["modifiedWhen"] == "2015-03-18"
    assert src["modifiedBy"] == "bar"
    pers = res["person"]
    assert pers["createdWhen"] == "2015-03-19"
    assert pers["createdBy"] == "foobar"
    assert pers["modifiedWhen"] == "2015-04-19"
    assert pers["modifiedBy"] == "foobarfoo"


def test_get_cache_file_name():
    """Should be the same for subjequent calls for same path
    but different for different paths
    """
    # same jsonfile should result in same cache file
    jsonfile = '/a/b/c/d/data.json'
    cfile1 = get_cache_file_name(jsonfile)
    cfile2 = get_cache_file_name(jsonfile)
    assert cfile1 == cfile2

    #  jsonfile on different path must result in different cache file
    jsonfile = '/z/b/c/d/data.json'
    cfile2 = get_cache_file_name(jsonfile)
    assert cfile1 != cfile2


def test_load_data():
    "Test loading of json data."
    # make sure cache file does not exist
    origfile = os.path.join(tempfile.gettempdir(), 'orig.json')
    cache_file = get_cache_file_name(origfile)
    if os.path.exists(cache_file):
        os.unlink(cache_file)
    # generate original file
    factoids = make_factoids(20)
    # save original file
    with open(origfile, 'w') as file_:
        json.dump({'factoids': factoids}, file_)

    # read (now: original file)
    data = read_json_file(origfile, 'foo')
    assert len(data) == 20

    # cache file should exist now
    assert os.path.exists(cache_file)

    # change cache_file data to test if next read uses cache file
    data[0]['@id'] = 'cached'
    with open(cache_file, 'w') as file_:
        json.dump(data, file_)
    data = read_json_file(origfile, 'foo')
    assert data[0]['@id'] == 'cached'

    # re-create orig-file: next read_json_file() should load orig_file again.
    factoids = make_factoids(20)
    with open(origfile, 'w') as file_:
        json.dump({'factoids': factoids}, file_)
    data = read_json_file(origfile, 'foo')
    assert data[0]['@id'] != 'cached'
