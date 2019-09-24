"""Unit tests for the reader module of connector.json
"""
import json
import os
import tempfile

from papilotte.connectors.json.reader import (read_json_file, get_cache_file_name, get_stmt_metadata)
from papilotte.connectors.mock.mockdata import make_factoids


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
    # generate original file data
    factoids = make_factoids(20)
    # save original file
    with open(origfile, 'w') as file_:
        json.dump({'factoids': factoids}, file_)

    # read (now: original file)
    data = read_json_file(origfile)
    assert len(data) == 20

    # cache file should exist now
    assert os.path.exists(cache_file)

    # change cache_file data to test if next read uses cache file
    data[0]['@id'] = 'cached'
    with open(cache_file, 'w') as file_:
        json.dump(data, file_)
        file_.flush()
    data = read_json_file(origfile)
    assert data[0]['@id'] == 'cached'

    # re-create orig-file: next read_json_file() should load orig_file again.
    factoids = make_factoids(20)
    with open(origfile, 'w') as file_:
        json.dump({'factoids': factoids}, file_)
        file_.flush()
    data = read_json_file(origfile)
    assert data[0]['@id'] != 'cached'


def test_get_stmt_metadata_keep_values():
    "Test if metadata is left untouched."
    factoid = {
                '@id': 1,
                'createdBy': 'foo',
                'createdWhen': '2019-01-01',
                'modifiedBy': 'bar',
                'modifiedWhen': '2019-01-02',
                'statement': {
                    '@id': 2,
                    'createdBy': 'foofoo',
                    'createdWhen': '2019-02-01',
                    'modifiedBy': 'barbar',
                    'modifiedWhen': '2019-02-02'
                }
        }
    assert get_stmt_metadata(factoid, 'createdBy') == 'foofoo'
    assert get_stmt_metadata(factoid, 'createdWhen') == '2019-02-01'
    assert get_stmt_metadata(factoid, 'modifiedBy') == 'barbar'
    assert get_stmt_metadata(factoid, 'modifiedWhen') == '2019-02-02'

    
def test_get_stmt_metadata_add_values():
    "Test if metadata is taken from factoid if missing."
    factoid = {
                '@id': 1,
                'createdBy': 'foo',
                'createdWhen': '2019-01-01',
                'modifiedBy': 'bar',
                'modifiedWhen': '2019-01-02',
                'statement': {
                    '@id': 2,
                }
        }
    assert get_stmt_metadata(factoid, 'createdBy') == 'foo'
    assert get_stmt_metadata(factoid, 'createdWhen') == '2019-01-01'
    assert get_stmt_metadata(factoid, 'modifiedBy') == 'bar'
    assert get_stmt_metadata(factoid, 'modifiedWhen') == '2019-01-02'


def test_get_stmt_metadata_add_values_but_modified():
    "Test if metadata is taken from factoid if missing, but not if modified is missing."
    factoid = {
                '@id': 1,
                'createdBy': 'foo',
                'createdWhen': '2019-01-01',
                'statement': {
                    '@id': 2,
                }
        }
    assert get_stmt_metadata(factoid, 'createdBy') == 'foo'
    assert get_stmt_metadata(factoid, 'createdWhen') == '2019-01-01'
    assert get_stmt_metadata(factoid, 'modifiedBy') is None
    assert get_stmt_metadata(factoid, 'modifiedWhen') is None
