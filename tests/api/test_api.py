"""Unit tests for functions in api.

Most of the api functions are tested via system tests, 
so here mostly utility function
"""
import copy
import pytest

from papilotte.api import is_valid_id, split_sortby, parse_search_date, fix_ids
from papilotte.exceptions import InvalidIdError

from datetime import date

def test_is_valid_id():
    "Return True if id_ only contains allowed characters."
    assert is_valid_id('') 
    assert is_valid_id(r"\abC01239_.-~") 
    assert is_valid_id('@') is False
    assert is_valid_id('&') is False
    assert is_valid_id('#') is False
    assert is_valid_id('illurk%3AP_Accone-1')


def test_split_sortby():
    "Test split_sortby from api.__init__.py."
    assert split_sortby('foo') == ('foo', 'ASC')
    assert split_sortby('fooASC') == ('foo', 'ASC')
    assert split_sortby('fooasc') == ('foo', 'ASC')
    assert split_sortby('fooDESC') == ('foo', 'DESC')
    assert split_sortby('foodesc') == ('foo', 'DESC')


def test_parse_search_date():
    "Test conversion from (incomplete) date strings to date objects."    

    # terminus postquem
    assert parse_search_date('1800-05-06') == '1800-05-06'
    assert parse_search_date('1800-5-6') == '1800-05-06'
    assert parse_search_date('1800-05') == '1800-05-01'
    assert parse_search_date('1800-5') == '1800-05-01'
    assert parse_search_date('1800') == '1800-01-01'

    assert parse_search_date('-333') == '-333-01-01'
    assert parse_search_date('-4004') == '-4004-01-01'

    # terminus antequem
    assert parse_search_date('1800-05-06', False) == '1800-05-06'
    assert parse_search_date('1800-05', False) == '1800-05-31'
    assert parse_search_date('1800', False) == '1800-12-31'

    assert parse_search_date('1804-02', False) == '1804-02-29'

    assert parse_search_date('-333', False) == '-333-12-31'
    assert parse_search_date('-4-02', False) == '-004-02-29'

    with pytest.raises(ValueError):
        parse_search_date('1800-13-21')

    with pytest.raises(ValueError):
        parse_search_date('1800--1-21')

    with pytest.raises(ValueError):
        parse_search_date('1800-01-32')

    with pytest.raises(ValueError):
        parse_search_date('1803-02-29')

    with pytest.raises(ValueError):
        parse_search_date('-333-02-29')

def test_fix_ids_person_source_statement():
    "Test fix_ids with a single person, source, or statement."
    result = fix_ids({'id': 'P1'})
    assert result['@id'] == 'P1'
    assert 'id' not in result

def test_fix_ids_factoid():
    "Test fix_ids with a full factoid."
    # full factoid
    input = {
        'id': 'F1', 
        'person': {'id': 'P1'},
        'source': {'id': 'S1'},
        'statements': [
            {'id': 'Stmt1a'},
            {'id': 'Stmt1b'},
            {'id': 'Stmt1c'},
        ]
    }
    result = fix_ids(copy.deepcopy(input))
    assert result['@id'] == 'F1'
    assert 'id' not in result
    assert result['person']['@id'] == 'P1'
    assert 'id' not in result['person']
    assert result['source']['@id'] == 'S1'
    assert 'id' not in result['source']
    assert result['statements'][0]['@id'] == 'Stmt1a'
    assert 'id' not in result['statements'][0]
    assert result['statements'][1]['@id'] == 'Stmt1b'
    assert 'id' not in result['statements'][1]
    assert result['statements'][2]['@id'] == 'Stmt1c'
    assert 'id' not in result['statements'][2]
