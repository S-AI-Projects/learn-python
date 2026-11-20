"""Errors and Exceptions.

@see: https://docs.python.org/3/tutorial/errors.html#errors-and-exceptions

Even if a statement or expression is syntactically correct, it may cause an error when an attempt
is made to execute it. Errors detected during execution are called exceptions and are not
unconditionally fatal.

It is possible to write programs that handle selected exceptions.
"""
import sys


def test_handle_exceptions(env=None):
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

    External Dependency Analysis:
    - This item has NO external observable dependencies: no network, file, database,
      system clock, randomness, or GUI dependencies are used.
    - Any introduced dependency parameter (env) defaults to None, preserving existing callers.
    """
    _ = env  # Preserves caller interface while permitting dependency injection

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


def test_handle_exceptions_state_isolation():
    """State isolation and repeated call test for test_handle_exceptions.

    Verifies:
      - Item has no external state dependencies.
      - Running fixture twice in fresh isolated state produces identical results.
      - Running after another valid input does not alter later fixture results.
      - Return value is None with zero observable mutation on module attributes.
    """
    # Run 1: Fresh isolated state
    ret_1 = test_handle_exceptions()
    assert ret_1 is None

    # Run 2: Fresh isolated state
    ret_2 = test_handle_exceptions()
    assert ret_2 is None

    # Run after another valid input (neighboring supported input)
    other_handled = False
    other_else = False
    try:
        other_result = 10 * (1 / 1)
        assert other_result == 10.0
    except ZeroDivisionError:
        other_handled = True
    else:
        other_else = True

    assert other_handled is False
    assert other_else is True

    # Run 3: Verify earlier runs cannot alter later fixture result
    ret_3 = test_handle_exceptions()
    assert ret_3 is None

    # Verify zero module mutation
    current_module = sys.modules[__name__]
    attrs_before = set(dir(current_module))
    test_handle_exceptions()
    attrs_after = set(dir(current_module))
    assert attrs_before == attrs_after
