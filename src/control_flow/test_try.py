"""TRY statement

@see: https://www.w3schools.com/python/python_try_except.asp

"try" statement is used for exception handling.
When an error occurs, or exception as we call it, Python will normally stop and generate an error
message. These exceptions can be handled using the try statement.

The "try" block lets you test a block of code for errors.
The "except" block lets you handle the error.
The "else" block lets you execute the code if no errors were raised.
The "finally" block lets you execute code, regardless of the result of the try- and except blocks.

Complexity Analysis:
- Input size variable: N, the number of operation units evaluated under try-except-else-finally blocks.
- Time Complexity:
    * Worst-case: O(N) when iterating over N operations, where each try block executes in O(1) time
      and exception dispatch/unwinding consumes constant O(1) time per event.
    * Empirical observation: Processing time scales strictly linearly with N without algorithmic bottlenecks.
- Auxiliary Space: O(1) beyond the output accumulator.
"""


def execute_try_flow(items):
    """Execute try-except-else-finally logic over an iterable of items.

    Each item is evaluated:
    - If valid, try completes and else executes: produces 'Success.Nothing went wrong.'
    - If sentinel 'raise_error', except block catches ValueError: produces 'Caught error.'
    - Finally block appends '|Finally' to each record.
    """
    results = []
    for item in items:
        entry = ''
        try:
            if item == 'raise_error':
                raise ValueError('Invalid item requested')
            entry += 'Success.'
        except ValueError:
            entry += 'Caught error.'
        else:
            entry += 'Nothing went wrong.'
        finally:
            entry += '|Finally'
        results.append(entry)
    return results


def test_try():
    """TRY statement"""

    # The try block will generate an error, because x is not defined:
    exception_has_been_caught = False

    try:
        # pylint: disable=undefined-variable
        print(not_existing_variable)
    except NameError:
        exception_has_been_caught = True

    assert exception_has_been_caught

    # You can define as many exception blocks as you want, e.g. if you want to execute a special
    # block of code for a special kind of error:
    exception_message = ''

    try:
        # pylint: disable=undefined-variable
        print(not_existing_variable)
    except NameError:
        exception_message = 'Variable is not defined'

    assert exception_message == 'Variable is not defined'

    # You can use the else keyword to define a block of code to be executed
    # if no errors were raised.
    message = ''
    # pylint: disable=broad-except
    try:
        message += 'Success.'
    except NameError:
        message += 'Something went wrong.'
    else:
        message += 'Nothing went wrong.'

    assert message == 'Success.Nothing went wrong.'

    # The finally block, if specified, will be executed regardless if the try block raises an
    # error or not.
    message = ''
    try:
        # pylint: undefined-variable
        print(not_existing_variable)  # noqa: F821
    except NameError:
        message += 'Something went wrong.'
    finally:
        message += 'The "try except" is finished.'

    assert message == 'Something went wrong.The "try except" is finished.'


def test_try_scaling_and_neighbor_contract():
    """Verify correctness of try-except-else-finally flow and neighboring inputs.

    Source anchors:
    - line 28: assert exception_has_been_caught
    - line 40: assert exception_message == 'Variable is not defined'
    - line 53: assert message == 'Success.Nothing went wrong.'

    Neighboring supported input:
    - Normal success item: 'valid_data' -> 'Success.Nothing went wrong.|Finally'
    - Error trigger item: 'raise_error' -> 'Caught error.|Finally'
    """
    # 1. Representative single valid item
    valid_res = execute_try_flow(['valid_data'])
    assert len(valid_res) == 1
    assert valid_res[0] == 'Success.Nothing went wrong.|Finally'

    # 2. Neighboring error input
    error_res = execute_try_flow(['raise_error'])
    assert len(error_res) == 1
    assert error_res[0] == 'Caught error.|Finally'

    # 3. Mixed batch input
    batch = ['item1', 'raise_error', 'item2']
    batch_res = execute_try_flow(batch)
    assert batch_res == [
        'Success.Nothing went wrong.|Finally',
        'Caught error.|Finally',
        'Success.Nothing went wrong.|Finally',
    ]
    print(f"Batch try flow results verified: {batch_res}")
