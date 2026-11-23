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

import random


def test_variables():
    """Test variables and verify variable-binding and dynamic-reassignment invariants.

    Invariant Contract:
      1. Binding Precision: Assigning a value to a variable binds its exact value and runtime type.
      2. Variable Isolation: Assigning or rebinding one variable does not alter or mutate
         distinct existing variable bindings in the active scope.
      3. Dynamic Rebinding: A variable may be rebound to a new value and a completely
         different type; the binding updates to the new value and new type with no residual
         state from previous assignments.
      4. Deterministic Repeatability: Repeated execution with fresh equivalent inputs produces
         identical values, runtime types, and isolation guarantees.
    """

    # --- Source Anchors ---
    integer_variable = 5
    string_variable = 'John'

    assert integer_variable == 5
    assert string_variable == 'John'

    variable_with_changed_type = 4  # x is of type int
    variable_with_changed_type = 'Sally'  # x is now of type str

    assert variable_with_changed_type == 'Sally'

    # --- Derived Neighboring Inputs ---
    # Neighboring integer input around 5 (neighbor: 6) and string input ('Alice'):
    neighbor_integer = 6
    neighbor_string = 'Alice'
    assert neighbor_integer == 6
    assert isinstance(neighbor_integer, int)
    assert neighbor_string == 'Alice'
    assert isinstance(neighbor_string, str)
    # Isolation: original anchors remain unchanged
    assert integer_variable == 5
    assert string_variable == 'John'

    # Neighboring dynamic rebinding (int -> str):
    neighbor_rebound = 42
    assert neighbor_rebound == 42
    assert isinstance(neighbor_rebound, int)
    neighbor_rebound = 'Bob'
    assert neighbor_rebound == 'Bob'
    assert isinstance(neighbor_rebound, str)
    # Isolation: distinct variables were not affected by rebinding
    assert neighbor_integer == 6
    assert neighbor_string == 'Alice'

    # --- Readable Small Example Case with Explicit Expected Values ---
    example_int = 100
    example_str = 'Charlie'
    assert example_int == 100
    assert type(example_int) is int
    assert example_str == 'Charlie'
    assert type(example_str) is str

    example_rebound = 1
    assert example_rebound == 1
    assert type(example_rebound) is int
    example_rebound = 'Delta'
    assert example_rebound == 'Delta'
    assert type(example_rebound) is str
    assert example_int == 100
    assert example_str == 'Charlie'

    # --- Deterministic 100-Case Property Invariant Test (Fixed Seed: 42) ---
    rng = random.Random(42)
    names = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta']

    for case_index in range(100):
        # Generate bounded valid inputs
        val_int = rng.randint(-10000, 10000)
        val_str = f"{rng.choice(names)}_{case_index}"
        val_init = rng.randint(0, 500)
        val_rebound = f"rebound_{case_index}"

        # 1. Assignment binds exact value and type
        dyn_int = val_int
        dyn_str = val_str
        assert dyn_int == val_int
        assert type(dyn_int) is int
        assert dyn_str == val_str
        assert type(dyn_str) is str

        # 2. Dynamic rebinding updates target to new value and new type
        dyn_rebound = val_init
        assert dyn_rebound == val_init
        assert type(dyn_rebound) is int

        dyn_rebound = val_rebound
        assert dyn_rebound == val_rebound
        assert type(dyn_rebound) is str

        # 3. Variable isolation: distinct variables remain unaltered
        assert dyn_int == val_int
        assert dyn_str == val_str

        # 4. Repeatability: fresh equivalent inputs yield identical outcomes
        fresh_int = int(str(val_int))
        fresh_str = str(val_str)
        fresh_rebound = str(val_rebound)

        rep_int = fresh_int
        rep_str = fresh_str
        rep_rebound = fresh_rebound

        assert rep_int == dyn_int == val_int
        assert rep_str == dyn_str == val_str
        assert rep_rebound == dyn_rebound == val_rebound
