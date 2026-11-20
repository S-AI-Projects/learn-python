"""Arbitrary Argument Lists

@see: https://docs.python.org/3/tutorial/controlflow.html#arbitrary-argument-lists

Function can be called with an arbitrary number of arguments. These arguments will be wrapped up in
a tuple. Before the variable number of arguments, zero or more normal arguments may occur.
"""


def test_function_arbitrary_arguments():
    """Arbitrary Argument Lists"""

    def test_function(first_param, *arguments):
        """This function accepts its arguments through "arguments" tuple"""
        assert first_param == 'first param'
        assert arguments == ('second param', 'third param')

    test_function('first param', 'second param', 'third param')

    # Readability improvement: Named the separator joining operation explicitly.
    # Before: return sep.join(args)   -- the purpose of sep.join was implicit
    # After:  joined = sep.join(args) followed by return joined
    #         -- the intermediate variable `joined` names the state being computed:
    #            the separator-joined concatenation of all positional arguments.
    def concat(*args, sep='/'):
        """Return all positional args joined by sep (default '/')."""
        joined = sep.join(args)
        return joined

    # Source anchor 1
    assert concat('earth', 'mars', 'venus') == 'earth/mars/venus'
    # Source anchor 2
    assert concat('earth', 'mars', 'venus', sep='.') == 'earth.mars.venus'
    # Neighboring supported input: concat('a', 'b', 'c') -> 'a/b/c'
    assert concat('a', 'b', 'c') == 'a/b/c'
    # Single argument boundary
    assert concat('earth') == 'earth'
    # Two arguments
    assert concat('earth', 'mars') == 'earth/mars'
    # Empty separator
    assert concat('earth', 'mars', 'venus', sep='') == 'earthmarsvenus'
    # Multi-char separator
    assert concat('earth', 'mars', sep=' and ') == 'earth and mars'

    # Verify first_param and arguments tuple from anchors
    captured_first = None
    captured_args = None

    def recording_function(first_param, *arguments):
        """Records both first_param and arguments for independent verification."""
        nonlocal captured_first, captured_args
        captured_first = first_param
        captured_args = arguments

    recording_function('first param', 'second param', 'third param')
    assert captured_first == 'first param'
    assert captured_args == ('second param', 'third param')


def test_function_arbitrary_arguments_regression():
    """Focused regression test for test_function_arbitrary_arguments contract."""
    import types
    current_module = types.ModuleType(__name__)
    current_module.__dict__.update(globals())
    attrs_before = set(dir(current_module))
    ret = test_function_arbitrary_arguments()
    assert ret is None
    attrs_after = set(dir(current_module))
    assert attrs_before == attrs_after
