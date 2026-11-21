"""Arithmetic operators

@see: https://www.w3schools.com/python/python_operators.asp

Arithmetic operators are used with numeric values to perform common mathematical operations
"""


def test_arithmetic_operators():
    """Arithmetic operators with a shared basic operand pair."""

    left_operand = 5
    right_operand = 3
    # Addition.
    assert left_operand + right_operand == 8

    # Subtraction.
    assert left_operand - right_operand == 2

    # Multiplication.
    assert left_operand * right_operand == 15
    assert isinstance(left_operand * right_operand, int)

    # Division.
    # Result of division is float number.
    assert 5 / 3 == 1.6666666666666667
    assert 8 / 4 == 2
    assert isinstance(5 / 3, float)
    assert isinstance(8 / 4, float)

    # Modulus.
    assert 5 % 3 == 2

    # Exponentiation.
    assert 5 ** 3 == 125
    assert 2 ** 3 == 8
    assert 2 ** 4 == 16
    assert 2 ** 5 == 32
    assert isinstance(5 ** 3, int)

    # Floor division.
    assert 5 // 3 == 1
    assert 6 // 3 == 2
    assert 7 // 3 == 2
    assert 9 // 3 == 3
    assert isinstance(5 // 3, int)


def test_basic_arithmetic_fixture_and_neighbor():
    """Lock down basic arithmetic results for integer operands."""
    cases = (
        (5, 3, (8, 2, 15)),
        (6, 3, (9, 3, 18)),
    )

    for left_operand, right_operand, expected in cases:
        actual = (
            left_operand + right_operand,
            left_operand - right_operand,
            left_operand * right_operand,
        )
        print(
            'operands=({}, {}): expected={!r}, actual={!r}'.format(
                left_operand,
                right_operand,
                expected,
                actual,
            )
        )
        assert actual == expected
