"""Function Annotations.

@see: https://docs.python.org/3/tutorial/controlflow.html#function-annotations

Function annotations are completely optional metadata information about the types used
by user-defined functions.

Annotations are stored in the __annotations__ attribute of the function as a dictionary and have no
effect on any other part of the function. Parameter annotations are defined by a colon after the
parameter name, followed by an expression evaluating to the value of the annotation. Return
annotations are defined by a literal ->, followed by an expression, between the parameter list and
the colon denoting the end of the def statement.
"""


def breakfast(ham: str, eggs: str = 'eggs') -> str:
    """Breakfast creator.

    This function has a positional argument, a keyword argument, and the return value annotated.
    """
    return ham + ' and ' + eggs


def test_function_annotations():
    """Function Annotations."""

    assert breakfast.__annotations__ == {'eggs': str, 'ham': str, 'return': str}

    # Neighboring supported input derived independently:
    assert breakfast('toast', 'butter') == 'toast and butter'
    assert breakfast('spam') == 'spam and eggs'


def test_function_annotations_mutation_resistance():
    """Mutation-resistant verification for function annotations and return contracts.

    Protected conditions:
      1. Annotation structure: must map 'ham' -> str, 'eggs' -> str, 'return' -> str.
      2. Return formatting invariant: f"{ham} and {eggs}".
      3. Type preservation: return value must be of type str as annotated.
    """
    # Verify return type matches return annotation
    res = breakfast('ham')
    assert isinstance(res, breakfast.__annotations__['return'])
    assert res == 'ham and eggs'

    # Verify custom parameter substitution matches specification
    custom_res = breakfast('bacon', 'sausage')
    assert custom_res == 'bacon and sausage'

