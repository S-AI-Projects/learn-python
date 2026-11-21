"""Documentation Strings.

@see: https://docs.python.org/3/tutorial/controlflow.html#documentation-strings

Here are some conventions about the content and formatting of documentation strings.

The first line should always be a short, concise summary of the object’s purpose. For brevity,
it should not explicitly state the object’s name or type, since these are available by other means
(except if the name happens to be a verb describing a function’s operation). This line should begin
with a capital letter and end with a period.

If there are more lines in the documentation string, the second line should be blank, visually
separating the summary from the rest of the description. The following lines should be one or more
paragraphs describing the object’s calling conventions, its side effects, etc.
"""

import inspect
import random


def do_nothing():
    """Do nothing, but document it.

    No, really, it doesn't do anything.

    Returns None and has no side effects.
    """
    pass


def test_function_documentation_string():
    """Test documentation string."""

    # cleandoc normalizes indentation consistently across Python versions.
    expected_docstring = (
        'Do nothing, but document it.\n\n'
        "No, really, it doesn't do anything.\n\n"
        'Returns None and has no side effects.'
    )
    actual_docstring = inspect.cleandoc(do_nothing.__doc__)
    print(
        'docstring: expected={!r}, actual={!r}'.format(
            expected_docstring, actual_docstring
        )
    )
    assert actual_docstring == expected_docstring


def test_do_nothing_returns_none_without_mutating_attributes():
    """A readable zero-argument call returns None and leaves state alone."""
    expected_result = None
    expected_attributes = do_nothing.__dict__.copy()
    actual_result = do_nothing()
    actual_attributes = do_nothing.__dict__.copy()
    print(
        'single call: expected return={!r}, actual return={!r}; '
        'expected attributes={!r}, actual attributes={!r}'.format(
            expected_result,
            actual_result,
            expected_attributes,
            actual_attributes,
        )
    )
    assert actual_result is expected_result
    assert actual_attributes == expected_attributes


def test_do_nothing_invariant_for_seeded_empty_input_domain():
    """One hundred seeded calls cover the only valid input: no arguments."""
    seed = 44045
    generator = random.Random(seed)
    valid_input_domain = ((),)
    cases = [generator.choice(valid_input_domain) for _ in range(100)]
    expected_results = [None] * 100
    expected_attributes = do_nothing.__dict__.copy()

    actual_results = []
    actual_attributes = []
    for args in cases:
        actual_results.append(do_nothing(*args))
        actual_attributes.append(do_nothing.__dict__.copy())

    print(
        'seed={!r}, input domain=((),), expected count=100, '
        'actual={!r}'.format(seed, len(cases))
    )
    print(
        'property results: expected={!r}, actual={!r}'.format(
            expected_results, actual_results
        )
    )
    print(
        'attribute state: expected={!r} for each call, actual={!r}'.format(
            expected_attributes, actual_attributes
        )
    )
    assert len(cases) == 100
    assert actual_results == expected_results
    assert all(
        attributes == expected_attributes
        for attributes in actual_attributes
    )
