"""Packages.

@see: https://docs.python.org/3/tutorial/modules.html#packages

Packages are a way of structuring Python’s module namespace by using “dotted module names”. For
example, the module name A.B designates a submodule named B in a package named A. Just like the
use of modules saves the authors of different modules from having to worry about each other’s
global variable names, the use of dotted module names saves the authors of multi-module packages
like NumPy or Pillow from having to worry about each other’s module names.

The __init__.py files are required to make Python treat the directories as containing packages;
this is done to prevent directories with a common name, such as string, from unintentionally hiding
valid modules that occur later on the module search path. In the simplest case, __init__.py can
just be an empty file, but it can also execute initialization code for the package or set the
__all__ variable, described later.

When the interpreter executes the import statement, it searches for module in a list of
directories assembled from the following sources:

- The directory from which the input script was run or the current directory if the interpreter is
being run interactively
- The list of directories contained in the PYTHONPATH environment variable, if it is set. (The
format for PYTHONPATH is OS-dependent but should mimic the PATH environment variable.)
- An installation-dependent list of directories configured at the time Python is installed

The resulting search path is accessible in the Python variable sys.path, which is obtained from a
module named sys:

>>> import sys
>>> sys.path

@see: https://realpython.com/python-modules-packages/
"""

import sys

# Users of the package can import individual modules from the package, for example.
import sound_package.effects.echo

# An alternative way of importing the submodule is:

# pylint: disable=reimported
from sound_package.effects import echo

# Yet another variation is to import the desired function or variable directly:
from sound_package.effects.echo import echo_function

# Neighboring effect module import for contract comparison:
import sound_package.effects.reverse
from sound_package.effects.reverse import reverse_function


def get_echo_effect_results():
    """Retrieve echo function output across all three supported package import pathways.

    Refactored to separate invocation retrieval from test assertions, improving clarity
    when verifying fully-qualified, submodule, and direct import bindings.
    """
    return (
        sound_package.effects.echo.echo_function(),
        echo.echo_function(),
        echo_function(),
    )


def test_packages():
    """Packages."""
    # Verify module search path anchor
    assert isinstance(sys.path, list)

    fully_qualified, submodule_imported, directly_imported = get_echo_effect_results()
    assert fully_qualified == 'Do echo effect'
    assert submodule_imported == 'Do echo effect'
    assert directly_imported == 'Do echo effect'


def test_packages_neighboring_effect_contract():
    """Verify neighboring effect submodule (reverse) following the same import pattern.

    Source anchors:
    - line 29: >>> import sys
    - line 30: >>> sys.path
    - line 59: assert sound_package.effects.echo.echo_function() == 'Do echo effect'

    Neighboring supported input / function:
    - sound_package.effects.reverse.reverse_function() -> 'Do reverse effect'
    """
    expected_reverse = 'Do reverse effect'
    actual_qualified = sound_package.effects.reverse.reverse_function()
    actual_direct = reverse_function()

    assert actual_qualified == expected_reverse
    assert actual_direct == expected_reverse
    print(f"neighbor reverse effect: expected={expected_reverse!r}, actual={actual_qualified!r}")
