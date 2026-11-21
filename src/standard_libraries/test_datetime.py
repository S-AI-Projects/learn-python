"""Dates and Times.

@see: https://docs.python.org/3/tutorial/stdlib.html#dates-and-times

The datetime module supplies classes for manipulating dates and times in both simple and complex
ways. While date and time arithmetic is supported, the focus of the implementation is on efficient
member extraction for output formatting and manipulation. The module also supports objects that
are timezone aware.
"""

from datetime import date, timedelta
import random


def test_datetime():
    """Dates and Times"""

    real_now = date.today()
    assert real_now

    fake_now = date(2018, 8, 29)

    assert fake_now.day == 29
    assert fake_now.month == 8
    assert fake_now.year == 2018
    assert fake_now.ctime() == 'Wed Aug 29 00:00:00 2018'
    assert fake_now.strftime(
        '%m-%d-%y. %d %b %Y is a %A on the %d day of %B.'
    ) == '08-29-18. 29 Aug 2018 is a Wednesday on the 29 day of August.'

    # Dates support calendar arithmetic.
    birthday = date(1964, 7, 31)
    age = fake_now - birthday

    assert age.days == 19752


def test_datetime_neighbor_contract():
    """Verify explicit source anchors and neighboring supported input.

    Source anchors:
    - line 18: assert real_now
    - line 22: assert fake_now.day == 29
    - line 23: assert fake_now.month == 8
    - line 34: assert age.days == 19752 (with birthday 1964-07-31)

    Neighboring supported input:
    - fake_now + 1 day = date(2018, 8, 30)
    - age.days becomes 19753 (independently calculated: 19752 + 1)
    """
    birthday = date(1964, 7, 31)
    fake_now = date(2018, 8, 29)
    neighbor_now = date(2018, 8, 30)

    assert fake_now.day == 29
    assert fake_now.month == 8
    assert (fake_now - birthday).days == 19752

    assert neighbor_now.day == 30
    assert neighbor_now.month == 8
    assert neighbor_now.year == 2018
    assert (neighbor_now - birthday).days == 19753
    print("neighbor contract: date(2018, 8, 30) -> age.days == 19753")


def test_datetime_invariants_property():
    """Property test for datetime arithmetic and serialization invariants.

    Invariants:
    1. Member extraction: date(y, m, d).day == d, .month == m, .year == y.
    2. Arithmetic identity: (D + timedelta(days=k)) - D == timedelta(days=k).
    3. Antisymmetry: (D1 - D2).days == -((D2 - D1).days).
    4. ISO serialization round-trip: date.fromisoformat(D.isoformat()) == D.
    """
    rng = random.Random(42)
    # Generate 100 bounded valid dates between 1900 and 2100
    base_anchor = date(1964, 7, 31)
    tested_count = 0

    for _ in range(100):
        year = rng.randint(1900, 2099)
        month = rng.randint(1, 12)
        # determine valid days in month
        if month in (1, 3, 5, 7, 8, 10, 12):
            max_day = 31
        elif month in (4, 6, 9, 11):
            max_day = 30
        else:
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
            max_day = 29 if is_leap else 28

        day = rng.randint(1, max_day)
        d = date(year, month, day)

        # Invariant 1: extraction
        assert d.year == year
        assert d.month == month
        assert d.day == day

        # Invariant 2: ISO round trip
        assert date.fromisoformat(d.isoformat()) == d

        # Invariant 3: Arithmetic addition round-trip
        offset = rng.randint(-1000, 1000)
        offset_delta = timedelta(days=offset)
        d_shifted = d + offset_delta
        assert (d_shifted - d).days == offset

        # Invariant 4: Antisymmetry relative to base anchor
        diff_forward = (d - base_anchor).days
        diff_backward = (base_anchor - d).days
        assert diff_forward == -diff_backward

        tested_count += 1

    assert tested_count == 100
    print(f"Verified 100 bounded valid date cases with fixed seed 42")
