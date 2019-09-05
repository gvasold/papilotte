"""A special date class for mocking.

This class is only useful for comparing date strings.
"""


class MockDate:
    """A naive date class which can handle negative dates.
    Only usable for comparing.
    """

    def __init__(self, date_str):
        if date_str[0] == "-":
            year, month, day = [int(x) for x in date_str[1:].split("-")]
            year = year * -1
        else:
            year, month, day = [int(x) for x in date_str.split("-")]
        self.year = year
        self.month = month
        self.day = day

    def __eq__(self, other):
        if ((self.year == other.year) and (self.month == other.month) and \
            (self.day == other.day)):
            return True
        return False

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        if self.year > other.year:
            greater_than = True
        elif self.year == other.year:
            if self.month > other.month:
                greater_than = True
            elif self.month == other.month:
                greater_than = self.day > other.day
            else:
                greater_than = False
        else:
            greater_than = False
        return greater_than

    def __ge__(self, other):
        return self == other or self > other

    def __lt__(self, other):
        if self.year < other.year:
            less_than = True
        elif self.year == other.year:
            if self.month < other.month:
                less_than = True
            elif self.year == other.year:
                less_than = self.day < other.day
            else:
                less_than = False
        else:
            less_than = False
        return less_than

    def __le__(self, other):
        return self == other or self < other

    def __str__(self):
        return "%d-%d-%d" % (self.year, self.month, self.day)
