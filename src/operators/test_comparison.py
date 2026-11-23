"""Comparison operators

@see: https://www.w3schools.com/python/python_operators.asp

Comparison operators are used to compare two values.

Representative Result Explanation:
Evaluating `5 > 3` yields `True`.
In relational semantics, `a > b` holds when `a` is strictly greater than `b`.
Via arithmetic difference, `lhs - rhs = 5 - 3 = +2`. Because `+2 > 0` (positive sign),
the left operand strictly exceeds the right operand, independently confirming that `5 > 3`
must evaluate to `True`.
"""


# Independent reference oracle: evaluates comparisons via numeric difference sign (lhs - rhs).
# Does NOT call test_comparison_operators.
def evaluate_by_difference(lhs, rhs, op):
    """Evaluate relational outcome via difference sign (lhs - rhs)."""
    diff = lhs - rhs
    if op == '==':
        return diff == 0
    if op == '!=':
        return diff != 0
    if op == '>':
        return diff > 0
    if op == '<':
        return diff < 0
    if op == '>=':
        return diff >= 0
    if op == '<=':
        return diff <= 0
    raise ValueError(f"Unsupported operator: {op}")


def apply_comparison(lhs, rhs, op):
    """Direct comparison operator evaluation."""
    if op == '==':
        return lhs == rhs
    if op == '!=':
        return lhs != rhs
    if op == '>':
        return lhs > rhs
    if op == '<':
        return lhs < rhs
    if op == '>=':
        return lhs >= rhs
    if op == '<=':
        return lhs <= rhs
    raise ValueError(f"Unsupported operator: {op}")


# Reviewed explicit expected-result table for comparison operators (30 valid inputs >= 20).
# Format: (lhs, rhs, operator, expected_result, description)
COMPARISON_CASES = (
    # Source anchors:
    (5, 5, '==', True, 'Anchor: 5 == 5 (diff 0)'),
    (5, 3, '!=', True, 'Anchor: 5 != 3 (diff +2)'),
    (5, 3, '>', True, 'Anchor: 5 > 3 (diff +2)'),
    (5, 8, '<', True, 'Anchor: 5 < 8 (diff -3)'),
    (5, 5, '>=', True, 'Anchor: 5 >= 5 (diff 0)'),
    (5, 4, '>=', True, 'Anchor: 5 >= 4 (diff +1)'),
    (5, 5, '<=', True, 'Anchor: 5 <= 5 (diff 0)'),
    (5, 6, '<=', True, 'Anchor: 5 <= 6 (diff -1)'),

    # Derived neighboring inputs around 3 and 5 (boundary values 3, 4, 5):
    (5, 4, '>', True, 'Neighbor: 5 > 4 (diff +1)'),
    (4, 5, '<', True, 'Neighbor: 4 < 5 (diff -1)'),
    (4, 4, '==', True, 'Neighbor: 4 == 4 (diff 0)'),
    (4, 3, '>', True, 'Neighbor: 4 > 3 (diff +1)'),
    (3, 4, '<', True, 'Neighbor: 3 < 4 (diff -1)'),
    (3, 3, '==', True, 'Neighbor boundary: 3 == 3 (diff 0)'),
    (3, 5, '<', True, 'Neighbor boundary: 3 < 5 (diff -2)'),
    (4, 4, '>=', True, 'Boundary: 4 >= 4 (diff 0)'),
    (4, 4, '<=', True, 'Boundary: 4 <= 4 (diff 0)'),

    # Smallest supported / zero / negative domain boundaries:
    (0, 0, '==', True, 'Zero boundary: 0 == 0 (diff 0)'),
    (0, 1, '<', True, 'Zero neighbor: 0 < 1 (diff -1)'),
    (1, 0, '>', True, 'Positive vs zero: 1 > 0 (diff +1)'),
    (-1, 0, '<', True, 'Negative vs zero: -1 < 0 (diff -1)'),
    (0, -1, '>', True, 'Zero vs negative: 0 > -1 (diff +1)'),
    (-1, -1, '==', True, 'Negative equality: -1 == -1 (diff 0)'),
    (-2, -1, '<', True, 'Negative ordering: -2 < -1 (diff -1)'),

    # False-outcome cross-checks:
    (5, 5, '!=', False, 'False case: 5 != 5 (diff 0)'),
    (5, 3, '==', False, 'False case: 5 == 3 (diff +2)'),
    (3, 5, '>', False, 'False case: 3 > 5 (diff -2)'),
    (5, 3, '<', False, 'False case: 5 < 3 (diff +2)'),
    (3, 5, '>=', False, 'False case: 3 >= 5 (diff -2)'),
    (5, 3, '<=', False, 'False case: 5 <= 3 (diff +2)'),
)


def test_comparison_operators():
    """Comparison operators.

    Representative Result Explanation:
      Evaluating `5 > 3` yields `True`.
      In relational semantics, `a > b` holds when `a` is strictly greater than `b`.
      Via arithmetic difference, `lhs - rhs = 5 - 3 = +2`. Because `+2 > 0` (positive sign),
      the left operand strictly exceeds the right operand, independently confirming that `5 > 3`
      must evaluate to `True`.
    """

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

    # --- Neighboring supported inputs around 3 and 5 ---
    # Boundary value 4 between 3 and 5:
    assert (number > 4) is True
    assert (number == 4) is False
    neighbor = 4
    assert neighbor < 5
    assert neighbor > 3
    assert neighbor == 4
    # Boundary value 3:
    boundary = 3
    assert boundary < 5
    assert boundary == 3
    assert boundary <= 3
    assert boundary >= 3

    # --- Reference-comparison regression tests (30 cases >= 20) ---
    for lhs, rhs, op, expected, _ in COMPARISON_CASES:
        # 1. Exact value assertion against explicit expected value
        actual = apply_comparison(lhs, rhs, op)
        assert actual == expected

        # 2. Cross-check against independent difference oracle
        oracle_result = evaluate_by_difference(lhs, rhs, op)
        assert actual == oracle_result

        # 3. Repeated run with fresh equivalent inputs produces identical results
        fresh_lhs = int(str(lhs))
        fresh_rhs = int(str(rhs))
        repeat_actual = apply_comparison(fresh_lhs, fresh_rhs, op)
        assert repeat_actual == actual == expected
