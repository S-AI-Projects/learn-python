"""Lambda Expressions

@see: https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions

Small anonymous functions can be created with the lambda keyword. Lambda functions can be used
wherever function objects are required. They are syntactically restricted to a single expression.
Semantically, they are just syntactic sugar for a normal function definition. Like nested function
definitions, lambda functions can reference variables from the containing scope.
"""
import sys


def test_lambda_expressions():
    """Lambda Expressions"""

    # This function returns the sum of its two arguments: lambda a, b: a+b
    # Like nested function definitions, lambda functions can reference variables from the
    # containing scope.

    def make_increment_function(delta):
        """This example uses a lambda expression to return a function"""
        return lambda number: number + delta

    increment_function = make_increment_function(42)

    # Executable source anchors:
    assert increment_function(0) == 42
    assert increment_function(1) == 43
    assert increment_function(2) == 44

    # Supported Boundary Contract:
    # -----------------------------------------------------------------------------------------
    # Domain category              | Input `number` | Expected Output / Behavior
    # -----------------------------------------------------------------------------------------
    # Source Anchor (boundary 0)   | 0              | 42 (0 + 42)
    # Source Anchor (interior 1)   | 1              | 43 (1 + 42)
    # Source Anchor (interior 2)   | 2              | 44 (2 + 42)
    # Neighboring supported input  | 3              | 45 (3 + 42)
    # Valid boundary (negative)    | -1             | 41 (-1 + 42)
    # Valid boundary (zero-sum)    | -42            | 0 (-42 + 42)
    # Explicitly unsupported       | 'invalid'      | raises TypeError (str + int unsupported)
    # Explicitly unsupported       | None           | raises TypeError (NoneType + int unsupported)
    # -----------------------------------------------------------------------------------------

    # Neighboring supported input (independently derived: 3 + 42 == 45):
    assert increment_function(3) == 45

    # Valid boundary inputs:
    assert increment_function(-1) == 41
    assert increment_function(-42) == 0

    # Explicitly unsupported values on the boundary
    # (raises TypeError natively without custom guards):
    type_error_caught = False
    try:
        increment_function('invalid')
    except TypeError:
        type_error_caught = True
    assert type_error_caught is True

    type_error_caught = False
    try:
        increment_function(None)
    except TypeError:
        type_error_caught = True
    assert type_error_caught is True

    # Another use of lambda is to pass a small function as an argument.
    pairs = [(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')]
    # Sort pairs by text key.
    pairs.sort(key=lambda pair: pair[1])

    assert pairs == [(4, 'four'), (1, 'one'), (3, 'three'), (2, 'two')]


def test_lambda_expressions_regression():
    """Focused regression test for test_lambda_expressions contract.

    Verifies:
      - Return value of test_lambda_expressions() is None.
      - Zero observable mutation on module attributes or global state.
      - Preserves public interface while enforcing explicit boundary contracts.
    """
    current_module = sys.modules[__name__]
    attrs_before = set(dir(current_module))

    return_val = test_lambda_expressions()
    assert return_val is None

    attrs_after = set(dir(current_module))
    assert attrs_before == attrs_after
