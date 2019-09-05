"""MockDate is a special date implementation for mock filtering.
"""
# As we are testing operators, we cannot trust in notmal boolean logic
# pylint: disable=unneeded-not
from papilotte.connectors.mock.mockdate import MockDate

def test_mockdate_equal_dates():
    "Both dates are equal."
    date1 = MockDate("2000-01-01")
    date2 = MockDate("2000-01-01")
    assert date1 == date2
    assert not date1 != date2
    assert not date1 < date2
    assert date1 <= date2
    assert not date1 > date2
    assert date1 >= date2


def test_mockdate_date2_greater():
    "Test d1 < d2 in different variants"
    date1 = MockDate("2000-01-01")
    date2 = MockDate("2000-01-02")
    assert not date1 == date2
    assert date1 != date2
    assert date1 < date2
    assert date1 <= date2
    assert not date1 > date2
    assert not date1 >= date2

    date2 = MockDate("2000-02-01")
    assert not date1 == date2
    assert date1 != date2
    assert date1 <= date2
    assert date1 < date2
    assert not date1 > date2
    assert not date1 >= date2

    date2 = MockDate("2001-01-01")
    assert not date1 == date2
    assert date1 != date2
    assert date1 < date2
    assert date1 <= date2
    assert not date1 > date2
    assert not date1 >= date2


def test_mockdate_date2_less():
    "d1 > d2 in different variants"
    date1 = MockDate("2000-12-31")
    date2 = MockDate("2000-12-30")
    assert not date1 == date2
    assert date1 != date2
    assert not date1 < date2
    assert not date1 <= date2
    assert date1 > date2
    assert date1 >= date2

    date2 = MockDate("2000-11-31")
    assert not date1 == date2
    assert date1 != date2
    assert not date1 < date2
    assert not date1 <= date2
    assert date1 > date2
    assert date1 >= date2

    date2 = MockDate("1999-12-31")
    assert not date1 == date2
    assert date1 != date2
    assert not date1 < date2
    assert not date1 <= date2
    assert date1 > date2
    assert date1 >= date2


def test_mockdate_negative_years():
    "Run some test with dates bc."
    date1 = MockDate("-300-01-01")
    date2 = MockDate("-300-01-01")
    assert date1 == date2

    date2 = MockDate("-301-01-01")
    assert date1 > date2

    date2 = MockDate("-299-01-01")
    assert date1 < date2

    date2 = MockDate("5-01-01")
    assert date1 < date2
