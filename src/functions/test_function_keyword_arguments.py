"""Keyword Arguments

@see: https://docs.python.org/3/tutorial/controlflow.html#keyword-arguments

Functions can be called using keyword arguments of the form kwarg=value.
"""

import pytest


def parrot(voltage, state='a stiff', action='voom', parrot_type='Norwegian Blue'):
    """Example of multi-argument function

    This function accepts one required argument (voltage) and three optional arguments
    (state, action, and type).
    """

    message = 'This parrot wouldn\'t ' + action + ' '
    message += 'if you put ' + str(voltage) + ' volts through it. '
    message += 'Lovely plumage, the ' + parrot_type + '. '
    message += 'It\'s ' + state + '!'

    return message


def test_function_keyword_arguments():
    """Test calling function with specifying keyword arguments.

    Contract for parrot(voltage, state='a stiff', action='voom', parrot_type='Norwegian Blue'):
      - Input:   voltage (required, positional-or-keyword); state, action, parrot_type (optional)
      - Output:  str — "This parrot wouldn't {action} if you put {voltage} volts through it.
                         Lovely plumage, the {parrot_type}. It's {state}!"
      - Pure function: no mutation, no external state; identical calls always return identical str.
      - Keyword arguments may be supplied in any order after the required positional argument.

    Boundary table (source contract):
    ┌──────────────────────────────────────────────────────┬──────────────────┬─────────────────┐
    │ Call form                                            │ Partition        │ Expected        │
    ├──────────────────────────────────────────────────────┼──────────────────┼─────────────────┤
    │ parrot(1000)         — 1 positional          ANCHOR  │ valid interior   │ str (voom/1000) │
    │ parrot(voltage=1000) — 1 keyword             ANCHOR  │ valid boundary   │ str (voom/1000) │
    │ parrot(voltage=1000000, action='VOOOOOM')    ANCHOR  │ valid interior   │ str (VOOOOOM)   │
    │ parrot(action='VOOOOOM', voltage=1000000)            │ valid interior   │ str (VOOOOOM)   │
    │ parrot(1000000, 'bereft of life', 'jump')            │ valid interior   │ str (jump)      │
    │ parrot(1000, state='pushing up the daisies')         │ valid interior   │ str (daisies)   │
    │ parrot(0)            — voltage boundary (0)          │ valid boundary   │ str (0 volts)   │
    │ parrot(voltage=0, state='dead', action='run',        │                  │                 │
    │        parrot_type='Macaw') — all 4 kwargs           │ valid boundary   │ str (all kwarg) │
    ├──────────────────────────────────────────────────────┼──────────────────┼─────────────────┤
    │ parrot()             — voltage missing               │ UNSUPPORTED      │ TypeError       │
    │ parrot(110, voltage=220) — duplicate keyword arg     │ UNSUPPORTED      │ TypeError       │
    │ parrot(actor='John Cleese') — unknown keyword arg    │ UNSUPPORTED      │ TypeError       │
    │ f(0, number=0)       — dup kwarg in 1-arg function   │ UNSUPPORTED      │ TypeError       │
    └──────────────────────────────────────────────────────┴──────────────────┴─────────────────┘
    """

    # The parrot function accepts one required argument (voltage) and three optional arguments
    # (state, action, and type). This function can be called in any of the following ways:

    message = (
        "This parrot wouldn't voom if you put 1000 volts through it. "
        "Lovely plumage, the Norwegian Blue. "
        "It's a stiff!"
    )
    # 1 positional argument  [anchor — valid interior]
    assert parrot(1000) == message
    # 1 keyword argument  [anchor — valid boundary: minimum required arg supplied as keyword]
    assert parrot(voltage=1000) == message

    message = (
        "This parrot wouldn't VOOOOOM if you put 1000000 volts through it. "
        "Lovely plumage, the Norwegian Blue. "
        "It's a stiff!"
    )
    # 2 keyword arguments  [anchor — valid interior]
    assert parrot(voltage=1000000, action='VOOOOOM') == message
    # 2 keyword arguments  [valid interior: keyword argument order is irrelevant]
    assert parrot(action='VOOOOOM', voltage=1000000) == message

    # 3 positional arguments  [valid interior]
    message = (
        "This parrot wouldn't jump if you put 1000000 volts through it. "
        "Lovely plumage, the Norwegian Blue. "
        "It's bereft of life!"
    )
    assert parrot(1000000, 'bereft of life', 'jump') == message

    # 1 positional, 1 keyword  [valid interior]
    message = (
        "This parrot wouldn't voom if you put 1000 volts through it. "
        "Lovely plumage, the Norwegian Blue. "
        "It's pushing up the daisies!"
    )
    assert parrot(1000, state='pushing up the daisies') == message

    # --- Boundary regression tests ---

    # Valid boundary: voltage=0 — neighboring minimum value on the integer number line.
    # Pre-calculated: "This parrot wouldn't voom if you put 0 volts through it.
    #                  Lovely plumage, the Norwegian Blue. It's a stiff!"
    assert parrot(0) == (
        "This parrot wouldn't voom if you put 0 volts through it. "
        "Lovely plumage, the Norwegian Blue. "
        "It's a stiff!"
    )

    # Valid boundary: all four keyword arguments supplied explicitly (fully-keyword call form).
    # Pre-calculated: "This parrot wouldn't run if you put 0 volts through it.
    #                  Lovely plumage, the Macaw. It's dead!"
    assert parrot(voltage=0, state='dead', action='run', parrot_type='Macaw') == (
        "This parrot wouldn't run if you put 0 volts through it. "
        "Lovely plumage, the Macaw. "
        "It's dead!"
    )

    # But all the following calls would be invalid.

    with pytest.raises(TypeError):
        # Required argument missing — Python raises TypeError for missing positional.
        # pylint: disable=no-value-for-parameter
        parrot()  # type: ignore[call-arg]  # pyrefly: ignore

    # Non-keyword argument after a keyword argument (syntax error — left as comment):
    # parrot(voltage=5.0, 'dead')

    with pytest.raises(TypeError):
        # Duplicate keyword argument: voltage supplied both positionally and as keyword.
        # pylint: disable=redundant-keyword-arg
        parrot(110, voltage=220)  # type: ignore[misc]  # pyrefly: ignore

    with pytest.raises(TypeError):
        # Unknown keyword argument — Python raises TypeError for unexpected kwarg.
        # pylint: disable=unexpected-keyword-arg,no-value-for-parameter
        parrot(actor='John Cleese')  # type: ignore[call-arg]  # pyrefly: ignore

    # In a function call, keyword arguments must follow positional arguments. All the keyword
    # arguments passed must match one of the arguments accepted by the function (e.g. actor is not
    # a valid argument for the parrot function), and their order is not important. This also
    # includes non-optional arguments (e.g. parrot(voltage=1000) is valid too). No argument may
    # receive a value more than once. Here's an example that fails due to this restriction:
    def function_with_one_argument(number):
        return number

    with pytest.raises(TypeError):
        # pylint: disable=redundant-keyword-arg
        function_with_one_argument(0, number=0)  # type: ignore[misc]  # pyrefly: ignore

    # When a final formal parameter of the form **name is present, it receives a dictionary
    # containing all keyword arguments except for those corresponding to a formal parameter.
    # This may be combined with a formal parameter of the form *name which receives a tuple
    # containing the positional arguments beyond the formal parameter list.
    # (*name must occur before **name.) For example, if we define a function like this:
    def test_function(first_param, *arguments, **keywords):
        """This function accepts its arguments through "arguments" tuple and keywords dictionary."""
        assert first_param == 'first param'
        assert arguments == ('second param', 'third param')
        assert keywords == {
            'fourth_param_name': 'fourth named param',
            'fifth_param_name': 'fifth named param'
        }

    test_function(
        'first param',
        'second param',
        'third param',
        fourth_param_name='fourth named param',
        fifth_param_name='fifth named param',
    )
