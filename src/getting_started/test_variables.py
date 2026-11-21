"""Variables

@see: https://docs.python.org/3/tutorial/introduction.html
@see: https://www.w3schools.com/python/python_variables.asp
@see: https://www.learnpython.org/en/Variables_and_Types

Python is completely object oriented, and not "statically typed".
You do not need to declare variables before using them, or declare
their type. Every variable in Python is an object.

Unlike other programming languages, Python has no command for
declaring a variable. A variable is created the moment you first assign
a value to it.

A variable can have a short name (like x and y) or a more descriptive name
(age, carname, total_volume).

Rules for Python variables:
- A variable name must start with a letter or the underscore character.
- A variable name cannot start with a number.
- A variable name can only contain alpha-numeric characters and underscores (A-z, 0-9, and _ ).
- Variable names are case-sensitive (age, Age and AGE are three different variables).
"""


def test_variables():
    """Test variables"""

    integer_variable = 5
    string_variable = 'John'

    assert integer_variable == 5
    assert string_variable == 'John'

    variable_with_changed_type = 4  # x is of type int
    variable_with_changed_type = 'Sally'  # x is now of type str

    assert variable_with_changed_type == 'Sally'


def test_variables_oracle_cross_check():
    """Cross-check dynamic variable assignments against an independent environment oracle.

    Source Anchors:
    - line 32: assert integer_variable == 5
    - line 33: assert string_variable == 'John'
    - line 38: assert variable_with_changed_type == 'Sally'

    Neighboring supported inputs:
    - integer_variable neighbor: 6 (integer increment)
    - string_variable neighbor: 'Johnny' (string extension)
    - variable_with_changed_type neighbor: 5 -> 'Sally Anne'

    Representative result explained:
    When assigning variable 'x' first to integer 4, then reassigning to string 'Sally',
    Python's dynamic typing re-binds name 'x' to the new string object, leaving the
    variable holding 'Sally' of type str.
    """
    assignment_sequences = [
        ('a', [5], 5, int),
        ('b', ['John'], 'John', str),
        ('c', [4, 'Sally'], 'Sally', str),
        ('d', [6], 6, int),
        ('e', ['Johnny'], 'Johnny', str),
        ('f', [5, 'Sally Anne'], 'Sally Anne', str),
        ('g', [0], 0, int),
        ('h', [-1], -1, int),
        ('i', [''], '', str),
        ('j', [100, 200], 200, int),
        ('k', ['hello', 'world'], 'world', str),
        ('l', [True, False], False, bool),
        ('m', [1.5, 2.5], 2.5, float),
        ('n', [1, 2.0], 2.0, float),
        ('o', ['a', 1], 1, int),
        ('p', [None, 'value'], 'value', str),
        ('q', [[1, 2], [3, 4]], [3, 4], list),
        ('r', [(1,), (2, 3)], (2, 3), tuple),
        ('s', [{1: 2}, {3: 4}], {3: 4}, dict),
        ('t', [10, 'ten', 10.0], 10.0, float),
        ('u', [0, False, 'zero'], 'zero', str),
        ('v', ['init', None], None, type(None)),
    ]

    def environment_oracle(values):
        """Independent oracle: evaluates final bound value and type from assignment history."""
        return values[-1], type(values[-1])

    for var_name, seq, expected_val, expected_type in assignment_sequences:
        val = None
        for item in seq:
            val = item

        oracle_val, oracle_type = environment_oracle(seq)
        assert oracle_val == expected_val
        assert oracle_type is expected_type
        assert val == oracle_val
        assert type(val) is oracle_type
        print(f"cross-check {var_name}: seq={seq!r}, val={val!r}, type={type(val).__name__}")
