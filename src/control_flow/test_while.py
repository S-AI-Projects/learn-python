"""WHILE statement

@see: https://docs.python.org/3/tutorial/controlflow.html
@see: https://docs.python.org/3/reference/compound_stmts.html#the-while-statement

The while loop executes as long as the condition remains true. In Python, like in C, any
non-zero integer value is true; zero is false. The condition may also be a string or list
value, in fact any sequence; anything with a non-zero length is true, empty sequences are
false.

The test used in the example is a simple comparison. The standard comparison operators are
written the same as in C: < (less than), > (greater than), == (equal to), <= (less than or
equal to), >= (greater than or equal to) and != (not equal to).
"""


def compute_power_while(base, exponent):
    """Raise base to exponent using a standard while loop.

    Preconditions & Contract:
      - base (int): Base operand.
      - exponent (int): Non-negative integer power.
      - Condition: 'while power > 0' executes exactly exponent times.
      - Returns: base ** exponent.
    """
    accum = 1
    power = exponent
    while power > 0:
        accum *= base
        power -= 1
    return accum


def assert_power_while_contract(base, exponent, expected):
    """Named assertion helper verifying while-loop power computation against expected output."""
    actual = compute_power_while(base, exponent)
    assert actual == expected, (
        f"While-loop contract violated for {base}^{exponent}: "
        f"expected {expected}, got {actual}"
    )


def test_while_statement():
    """WHILE statement"""

    # Let's raise the number to certain power using while loop.
    number = 2
    power = 5

    result = 1

    while power > 0:
        result *= number
        power -= 1

    # 2^5 = 32
    assert result == 32

    # --- Strengthened Contract Verifications & Named Regression Assertions ---
    # 1. Source anchor verification: 2^5 == 32
    assert_power_while_contract(2, 5, 32)

    # 2. Derived neighboring supported inputs (independently calculated expected outputs):
    # 2^4 = 16 (neighboring smaller power)
    assert_power_while_contract(2, 4, 16)
    # 2^6 = 64 (neighboring larger power)
    assert_power_while_contract(2, 6, 64)
    # 3^3 = 27 (different base)
    assert_power_while_contract(3, 3, 27)

    # 3. Minimal boundary-sensitive inputs (detects off-by-one mutants such as '>= 0' or '> 1'):
    # 2^0 = 1 (zero iterations: detects 'while power >= 0' mutant which yields 2)
    assert_power_while_contract(2, 0, 1)
    # 2^1 = 2 (single iteration: detects 'while power > 1' mutant which yields 1)
    assert_power_while_contract(2, 1, 2)

    # 4. Repeatability: repeated runs with fresh equivalent inputs yield identical results
    for _ in range(5):
        assert_power_while_contract(2, 5, 32)
        assert_power_while_contract(2, 0, 1)
        assert_power_while_contract(2, 4, 16)
