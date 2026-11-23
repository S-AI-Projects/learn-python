"""Default Argument Values

@see: https://docs.python.org/3/tutorial/controlflow.html#default-argument-values

The most useful form is to specify a default value for one or more arguments. This creates a
function that can be called with fewer arguments than it is defined to allow.
"""


def power_of(number, power=2):
    """ Raises number to specific power.

    You may notice that by default the function raises number to the power of two.
    """
    return number ** power


def test_default_function_arguments():
    """Test default function arguments.

    Contract for power_of(number, power=2):
      - Input:  number (numeric), power (numeric, default=2)
      - Output: number ** power  (a numeric value; no mutation of inputs or external state)
      - Default power: when omitted, power=2, so power_of(n) == n ** 2
      - Pure function: repeated calls with the same arguments always return the same value.
    """

    # This function power_of can be called in several ways because it has default value for
    # the second argument. First we may call it omitting the second argument at all.
    assert power_of(3) == 9
    # We may also want to override the second argument by using the following function calls.
    assert power_of(3, 2) == 9
    assert power_of(3, 3) == 27

    # --- Regression tests: one per distinct behaviour ---

    # (a) Ordinary input – neighbouring base: 2 ** 2 = 4
    assert power_of(2) == 4

    # (b) Smallest supported input – base 0: 0 ** 2 = 0
    assert power_of(0) == 0

    # (b) Exponent boundary – exponent 0: any number ** 0 == 1
    assert power_of(3, 0) == 1

    # (c) Equal base/exponent boundary: 2 ** 2 = 4
    assert power_of(2, 2) == 4

    # (c) Repeated calls – verify no hidden state / mutation between invocations
    first_call = power_of(3)
    second_call = power_of(3)
    assert first_call == second_call == 9
