"""IF statement

@see: https://docs.python.org/3/tutorial/controlflow.html

There can be zero or more elif parts, and the else part is optional. The keyword ‘elif’ is
short for ‘else if’, and is useful to avoid excessive indentation.

An if … elif … elif … sequence is a substitute for the switch or case statements found
in other languages.
"""


def evaluate_if_statement(number):
    """Evaluate the if-elif-else contract defined in test_if_statement.

    Input/Output Contract:
    - number < 0: 'Number is less than zero'
    - number == 0: 'Number equals to zero'
    - 0 < number < 1: 'Number is greater than zero but less than one'
    - number >= 1: 'Number bigger than or equal to one'

    Pure function; performs no mutation and has no external dependencies.
    """
    conclusion = ''
    if number < 0:
        conclusion = 'Number is less than zero'
    elif number == 0:
        conclusion = 'Number equals to zero'
    elif number < 1:
        conclusion = 'Number is greater than zero but less than one'
    else:
        conclusion = 'Number bigger than or equal to one'
    return conclusion


def test_if_statement():
    """IF statement"""

    number = 15
    conclusion = ''

    if number < 0:
        conclusion = 'Number is less than zero'
    elif number == 0:
        conclusion = 'Number equals to zero'
    elif number < 1:
        conclusion = 'Number is greater than zero but less than one'
    else:
        conclusion = 'Number bigger than or equal to one'

    assert conclusion == 'Number bigger than or equal to one'


def test_if_statement_contract_boundaries():
    """Regression test covering ordinary inputs, boundaries, and neighbors.

    Source anchor: assert conclusion == 'Number bigger than or equal to one'
    Neighboring supported input: number = 0.5 -> 'Number is greater than zero but less than one'
    """
    cases = [
        (-100, 'Number is less than zero', 'smallest/negative input'),
        (-1, 'Number is less than zero', 'negative boundary'),
        (0, 'Number equals to zero', 'zero boundary'),
        (0.5, 'Number is greater than zero but less than one', 'neighboring supported input'),
        (1, 'Number bigger than or equal to one', 'boundary at one'),
        (15, 'Number bigger than or equal to one', 'ordinary input anchor'),
        (42, 'Number bigger than or equal to one', 'repeated equivalent domain value'),
    ]

    for num, expected, label in cases:
        actual = evaluate_if_statement(num)
        print('{}: input={!r}, expected={!r}, actual={!r}'.format(label, num, expected, actual))
        assert actual == expected
