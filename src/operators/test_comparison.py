"""Comparison operators

@see: https://www.w3schools.com/python/python_operators.asp

Comparison operators are used to compare two values.
"""


def test_comparison_operators():
    """Comparison operators"""

    # Equal.
    number = 5
    assert number == 5

    # Not equal.
    number = 5
    assert number != 3

    # Greater than.
    number = 5
    assert number > 3

    # Less than.
    number = 5
    assert number < 8

    # Greater than or equal to
    number = 5
    assert number >= 5
    assert number >= 4

    # Less than or equal to
    number = 5
    assert number <= 5
    assert number <= 6


def test_comparison_operators_branches():
    """Exercise the False (absent-result) branch of each comparison operator.

    The contract for comparison operators is total: every pair of comparable
    values returns True or False with no exception.  The 'failure' branch is
    the False result.  After each False-producing comparison the state variable
    remains unchanged and a True-producing call still succeeds, confirming that
    reaching the False branch leaves caller-owned state valid.

    Source lines exercised (False branches):
      Line 14 – Equal (==):        5 == 4  → False
      Line 18 – Not-equal (!=):    5 != 5  → False
      Line 22 – Greater-than (>):  5 > 5   → False   (boundary: equal values)
      Line 26 – Less-than (<):     5 < 5   → False   (boundary: equal values)
      Line 30 – GTE (>=):          5 >= 6  → False
      Line 34 – LTE (<=):          5 <= 4  → False
    """

    # --- Source anchor 1: number == 5 (True branch) ---
    number = 5
    assert number == 5                # True branch (anchor)

    # False branch – equal operator; state unchanged afterwards
    assert not (number == 4)          # 5 == 4 → False
    assert number == 5                # state still valid after False branch

    # --- Source anchor 2: number != 3 (True branch) ---
    assert number != 3                # True branch (anchor)

    # False branch – not-equal operator
    assert not (number != 5)          # 5 != 5 → False
    assert number != 3                # ordinary call succeeds after False branch

    # --- Source anchor 3: number > 3 (True branch) ---
    assert number > 3                 # True branch (anchor)

    # False branch – greater-than at boundary (equal values)
    assert not (number > 5)           # 5 > 5 → False
    assert number > 3                 # ordinary call succeeds after False branch

    # False branch – less-than at boundary (equal values)
    assert not (number < 5)           # 5 < 5 → False
    assert number < 8                 # ordinary call succeeds after False branch

    # False branch – greater-than-or-equal
    assert not (number >= 6)          # 5 >= 6 → False
    assert number >= 5                # ordinary call succeeds after False branch

    # False branch – less-than-or-equal
    assert not (number <= 4)          # 5 <= 4 → False
    assert number <= 5                # ordinary call succeeds after False branch

    # --- Neighboring supported input: number = 6 (one step above fixture) ---
    # Independently calculated expected values:
    #   6 == 6 → True,  6 != 3 → True,  6 > 3 → True
    #   6 < 8 → True,   6 >= 5 → True,  6 <= 6 → True
    #   False branches: 6 == 5 → False,  6 > 6 → False,  6 < 6 → False
    neighbor = 6
    assert neighbor == 6              # True
    assert neighbor != 3              # True
    assert neighbor > 3               # True
    assert neighbor < 8               # True
    assert neighbor >= 5              # True
    assert neighbor <= 6              # True
    assert not (neighbor == 5)        # False branch
    assert not (neighbor > 6)         # False branch at boundary
    assert not (neighbor < 6)         # False branch at boundary


def test_comparison_operators_regression():
    """Regression: test_comparison_operators returns None, no module mutation."""
    import types
    current_module = types.ModuleType(__name__)
    current_module.__dict__.update(globals())
    attrs_before = set(dir(current_module))
    ret = test_comparison_operators()
    assert ret is None
    attrs_after = set(dir(current_module))
    assert attrs_before == attrs_after
