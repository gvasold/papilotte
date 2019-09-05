"""
tests.connectors.dateutil
~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from papilotte.connectors.dateutil import parse_single_date, from_to_date


def test_parse_single_date_full():
    "Test parse_single_date with full date (YYYY-MM-DD)."
    assert parse_single_date("2015-01-01") == "2015-01-01"
    assert parse_single_date("-15-03-11") == "-15-03-11"
    assert parse_single_date("2015-3-1") == "2015-03-01"


def test_parse_single_date_year_only():
    "Test parse_single_date with missing month and day."
    assert parse_single_date("866") == "866-01-01"
    assert parse_single_date("866-") == "866-01-01"


def test_parse_single_date_year_month_only():
    "Test parse_single_date with missing day."
    assert parse_single_date("1024-02") == "1024-02-01"
    assert parse_single_date("1024-02-") == "1024-02-01"
    assert parse_single_date("1024-2") == "1024-02-01"
    assert parse_single_date("1024-2-") == "1024-02-01"


def test_parse_single_date_year_postquem():
    "Test test_parse_single_date with postquem flag set to False."
    assert parse_single_date("2011", False) == "2011-12-31"
    assert parse_single_date("2011-01", False) == "2011-01-31"
    assert parse_single_date("2011-02", False) == "2011-02-28"
    # test leap year
    assert parse_single_date("2012-02", False) == "2012-02-29"
    assert parse_single_date("2011-03", False) == "2011-03-31"
    assert parse_single_date("2011-04", False) == "2011-04-30"
    assert parse_single_date("2011-05", False) == "2011-05-31"
    assert parse_single_date("2011-06", False) == "2011-06-30"
    assert parse_single_date("2011-07", False) == "2011-07-31"
    assert parse_single_date("2011-08", False) == "2011-08-31"
    assert parse_single_date("2011-09", False) == "2011-09-30"
    assert parse_single_date("2011-10", False) == "2011-10-31"
    assert parse_single_date("2011-11", False) == "2011-11-30"
    assert parse_single_date("2011-12", False) == "2011-12-31"


def test_from_to_date():
    "Basic tests for dateutil.from_to_date()."
    assert from_to_date(None, None) == (None, None)
    assert from_to_date("2012-02-03", "2012-02-03") == ("2012-02-03", "2012-02-03")


def test_from_to_date_incomplete_to():
    "Test if to_ is an incomplete date."
    assert from_to_date("2012-02-03", "2012-02") == ("2012-02-03", "2012-02-29")
    assert from_to_date("2012-02-03", "2012") == ("2012-02-03", "2012-12-31")


def test_from_to_date_incomplete_from():
    "Test if from_ is an incomplete date."
    assert from_to_date("2012-02", "2012-02-03") == ("2012-02-01", "2012-02-03")
    assert from_to_date("2012", "2012-02-03") == ("2012-01-01", "2012-02-03")


def test_from_to_date_both_incomplete():
    "Test if from_ and to_ are an incomplete dates."
    assert from_to_date("2012", "2012-02") == ("2012-01-01", "2012-02-29")
    assert from_to_date("2012", "2017") == ("2012-01-01", "2017-12-31")


def test_from_to_date_missing_to():
    "Test if to_ is set to None"
    assert from_to_date("2012-01-01", None) == ("2012-01-01", "2012-01-01")
    assert from_to_date("2012-01", None) == ("2012-01-01", "2012-01-31")
    assert from_to_date("2012", None) == ("2012-01-01", "2012-12-31")


def test_from_to_date_missing_from():
    "Test if from_ is set to None"
    assert from_to_date(None, "2012-01-01") == ("2012-01-01", "2012-01-01")
    assert from_to_date(None, "2012-01") == ("2012-01-01", "2012-01-31")
    assert from_to_date(None, "2012") == ("2012-01-01", "2012-12-31")
    