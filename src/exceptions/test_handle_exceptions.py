"""Errors and Exceptions.

@see: https://docs.python.org/3/tutorial/errors.html#errors-and-exceptions

Even if a statement or expression is syntactically correct, it may cause an error when an attempt
is made to execute it. Errors detected during execution are called exceptions and are not
unconditionally fatal.

It is possible to write programs that handle selected exceptions.
"""
import sys


def test_handle_exceptions():
    """Handling of exceptions

    The try statement works as follows.

    - First, the try clause (the statement(s) between the try and except keywords) is executed.

    - If no exception occurs, the except clause is skipped and execution of the try statement
    is finished.

    - If an exception occurs during execution of the try clause, the rest of the clause is skipped.
    Then if its type matches the exception named after the except keyword, the except clause is
    executed, and then execution continues after the try statement.

    - If an exception occurs which does not match the exception named in the except clause, it is
    passed on to outer try statements; if no handler is found, it is an unhandled exception and
    execution stops with a message.
    """

    # Let's simulate division by zero exception.
    exception_has_been_handled = False
    try:
        result = 10 * (1 / 0)  # division by zero
        # We should not get here at all.
        assert result is not None
    except ZeroDivisionError:
        # We should get here because of division by zero.
        exception_has_been_handled = True

    assert exception_has_been_handled is True

    # Let's simulate undefined variable access exception.
    exception_has_been_handled = False
    try:
        # pylint: disable=undefined-variable
        result = 4 + spam * 3  # name 'spam' is not defined
        # We should not get here at all.
        assert result is not None
    except NameError:
        # We should get here because of undefined variable.
        exception_has_been_handled = True

    assert exception_has_been_handled is True

    # A try statement may have more than one except clause, to specify handlers for different
    # exceptions. At most one handler will be executed. Handlers only handle exceptions that occur
    # in the corresponding try clause, not in other handlers of the same try statement. An except
    # clause may name multiple exceptions as a parenthesized tuple, for example:

    exception_has_been_handled = False
    try:
        result = 10 * (1 / 0)  # division by zero
        # We should not get here at all.
        assert result is not None
    except (ZeroDivisionError, NameError):
        # We should get here because of division by zero.
        exception_has_been_handled = True

    assert exception_has_been_handled is True

    # Exception handlers may be chained.
    exception_has_been_handled = False
    try:
        result = 10 * (1 / 0)  # division by zero
        # We should not get here at all.
        assert result is not None
    except NameError:
        # We should get here because of division by zero.
        exception_has_been_handled = True
    except ZeroDivisionError:
        # We should get here because of division by zero.
        exception_has_been_handled = True

    assert exception_has_been_handled is True

    # The try … except statement has an optional else clause, which, when present, must follow all
    # except clauses. It is useful for code that must be executed if the try clause does not raise
    # an exception. For example:

    exception_has_been_handled = False
    no_exceptions_has_been_fired = False

    try:
        result = 10
        # We should get here because no exception occurred.
        assert result == 10

    except NameError:
        # We should not get here because result = 10 does not raise an exception.
        exception_has_been_handled = True
    else:
        no_exceptions_has_been_fired = True

    assert exception_has_been_handled is False
    assert no_exceptions_has_been_fired is True

    # Supported Boundary Contract for Exception Handling & Result Evaluation:
    # -----------------------------------------------------------------------------------------
    # Domain category              | Expression / Input    | Expected | Handled | Else fired
    # -----------------------------------------------------------------------------------------
    # Source Anchor (Exception)    | 10 * (1 / 0)          | None     | True    | False
    # Source Anchor (No Exception) | result = 10           | 10       | False   | True
    # Ordinary input               | 10 * (1 / 2)          | 5.0      | False   | True
    # Neighboring supported input  | 10 * (1 / 1)          | 10.0     | False   | True
    # Smallest supported input     | 0 * (1 / 1)           | 0.0      | False   | True
    # Repeated-value / boundary    | 10 * (1 / 2) repeated | 5.0      | False   | True
    # -----------------------------------------------------------------------------------------

    # Neighboring supported input derived independently:
    # Starting from division by zero 10 * (1 / 0), neighboring divisor 1 gives 10 * (1 / 1) == 10.0
    exception_has_been_handled = False
    no_exceptions_has_been_fired = False
    try:
        result = 10 * (1 / 1)
        assert result == 10.0
    except ZeroDivisionError:
        exception_has_been_handled = True
    else:
        no_exceptions_has_been_fired = True

    assert exception_has_been_handled is False
    assert no_exceptions_has_been_fired is True
    assert result == 10.0

    # Ordinary input:
    exception_has_been_handled = False
    no_exceptions_has_been_fired = False
    try:
        result = 10 * (1 / 2)
        assert result == 5.0
    except ZeroDivisionError:
        exception_has_been_handled = True
    else:
        no_exceptions_has_been_fired = True

    assert exception_has_been_handled is False
    assert no_exceptions_has_been_fired is True
    assert result == 5.0

    # Smallest supported input (numerator = 0 yielding 0.0;
    # asserting explicit value over truthiness):
    exception_has_been_handled = False
    no_exceptions_has_been_fired = False
    try:
        result = 0 * (1 / 1)
        assert result == 0.0
    except ZeroDivisionError:
        exception_has_been_handled = True
    else:
        no_exceptions_has_been_fired = True

    assert exception_has_been_handled is False
    assert no_exceptions_has_been_fired is True
    assert result == 0.0

    # Repeated-value / equivalent domain boundary:
    for _ in range(2):
        exception_has_been_handled = False
        no_exceptions_has_been_fired = False
        try:
            result = 10 * (1 / 2)
            assert result == 5.0
        except ZeroDivisionError:
            exception_has_been_handled = True
        else:
            no_exceptions_has_been_fired = True

        assert exception_has_been_handled is False
        assert no_exceptions_has_been_fired is True
        assert result == 5.0


def test_handle_exceptions_regression():
    """Focused regression test for test_handle_exceptions contract.

    Verifies:
      - Return value of test_handle_exceptions() is None.
      - No observable mutation occurs on module attributes or global state.
      - Separate testing of returned values and side effects across exception boundaries.
    """
    current_module = sys.modules[__name__]
    attrs_before = set(dir(current_module))

    return_val = test_handle_exceptions()
    assert return_val is None

    attrs_after = set(dir(current_module))
    assert attrs_before == attrs_after
