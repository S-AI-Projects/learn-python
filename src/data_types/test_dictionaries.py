"""Dictionaries.

@see: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
@see: https://www.w3schools.com/python/python_dictionaries.asp

A dictionary is a collection which is unordered, changeable and indexed. In Python dictionaries are
written with curly brackets, and they have keys and values.

Dictionaries are sometimes found in other languages as “associative memories” or “associative
arrays”. Unlike sequences, which are indexed by a range of numbers, dictionaries are indexed by
keys, which can be any immutable type; strings and numbers can always be keys. Tuples can be used
as keys if they contain only strings, numbers, or tuples; if a tuple contains any mutable object
either directly or indirectly, it cannot be used as a key. You can’t use lists as keys, since
lists can be modified in place using index assignments, slice assignments, or methods like append()
and extend().

It is best to think of a dictionary as a set of key: value pairs, with the requirement that the
keys are unique (within one dictionary). A pair of braces creates an empty dictionary: {}.
Placing a comma-separated list of key:value pairs within the braces adds initial key:value pairs
to the dictionary; this is also the way dictionaries are written on output.
"""

import pytest


def test_dictionary():
    """Dictionary contract, failure paths, and state-preservation guarantees.

    Documented Source Lines & Contract:
      1. Failure Path (lines 38-40, 61): Indexing an absent key (fruits_dictionary['missing'])
         or deleting an absent key (del fruits_dictionary['missing']) raises KeyError.
      2. Valid Absent-Result / Fallback Path: fruits_dictionary.get('missing') returns None
         or a custom default sentinel, without mutating or raising.
      3. Smallest Input (line 18): Empty dictionary {} behavior on indexing (KeyError)
         and fallback (.get() -> None or sentinel).
      4. State Preservation: Caller-owned dictionary keys, values, and length remain
         completely intact and uncorrupted after a KeyError failure.
    """

    fruits_dictionary = {
        'cherry': 'red',
        'apple': 'green',
        'banana': 'yellow',
    }

    assert isinstance(fruits_dictionary, dict)

    # You may access set elements by keys.
    assert fruits_dictionary['apple'] == 'green'
    assert fruits_dictionary['banana'] == 'yellow'
    assert fruits_dictionary['cherry'] == 'red'

    # To check whether a single key is in the dictionary, use the in keyword.
    assert 'apple' in fruits_dictionary
    assert 'pineapple' not in fruits_dictionary

    # Change the apple color to "red".
    fruits_dictionary['apple'] = 'red'

    # Add new key/value pair to the dictionary
    fruits_dictionary['pineapple'] = 'yellow'
    assert fruits_dictionary['pineapple'] == 'yellow'

    # Performing list(d) on a dictionary returns a list of all the keys used in the dictionary,
    # in insertion order (if you want it sorted, just use sorted(d) instead).
    assert list(fruits_dictionary) == ['cherry', 'apple', 'banana', 'pineapple']
    assert sorted(fruits_dictionary) == ['apple', 'banana', 'cherry', 'pineapple']

    # It is also possible to delete a key:value pair with del.
    del fruits_dictionary['pineapple']
    assert list(fruits_dictionary) == ['cherry', 'apple', 'banana']

    # --- Failure-Path & Recovery Regression Tests ---
    # Record caller-owned state snapshot before triggering failure
    state_before_len = len(fruits_dictionary)
    state_before_keys = list(fruits_dictionary.keys())
    state_before_items = dict(fruits_dictionary)

    # 1. Failure path: KeyError on missing key lookup
    with pytest.raises(KeyError):
        _ = fruits_dictionary['not_existing_fruit']

    # 1b. Failure path: KeyError on deleting an absent key
    with pytest.raises(KeyError):
        del fruits_dictionary['not_existing_fruit']

    # 2. State preservation assertion: dictionary remains intact and uncorrupted after KeyError
    assert len(fruits_dictionary) == state_before_len
    assert list(fruits_dictionary.keys()) == state_before_keys
    assert fruits_dictionary == state_before_items

    # 3. Post-failure recovery: ordinary valid lookup succeeds immediately after failure
    assert fruits_dictionary['apple'] == 'red'
    assert fruits_dictionary['banana'] == 'yellow'
    assert fruits_dictionary['cherry'] == 'red'

    # --- Valid Absent-Result / Fallback Path (.get() and empty dict) ---
    # .get() on absent key returns None by default without raising
    assert fruits_dictionary.get('not_existing_fruit') is None

    # .get() on absent key with custom default sentinel
    assert fruits_dictionary.get('not_existing_fruit', 'default_color') == 'default_color'

    # Derived neighboring input: querying existing key via .get() and fallback
    assert fruits_dictionary.get('apple') == 'red'
    assert fruits_dictionary.get('banana', 'fallback') == 'yellow'
    assert fruits_dictionary.get('mango', 'unknown fruit') == 'unknown fruit'

    # Smallest input: empty dictionary {} behavior
    empty_dict = {}
    assert len(empty_dict) == 0
    assert not bool(empty_dict)
    with pytest.raises(KeyError):
        _ = empty_dict['any_key']
    assert empty_dict.get('any_key') is None
    assert empty_dict.get('any_key', 'fallback_sentinel') == 'fallback_sentinel'
    assert len(empty_dict) == 0

    # The dict() constructor builds dictionaries directly from sequences of key-value pairs.
    dictionary_via_constructor = dict([('sape', 4139), ('guido', 4127), ('jack', 4098)])

    assert dictionary_via_constructor['sape'] == 4139
    assert dictionary_via_constructor['guido'] == 4127
    assert dictionary_via_constructor['jack'] == 4098

    # In addition, dict comprehensions can be used to create dictionaries from arbitrary key
    # and value expressions:
    dictionary_via_expression = {x: x**2 for x in (2, 4, 6)}
    assert dictionary_via_expression[2] == 4
    assert dictionary_via_expression[4] == 16
    assert dictionary_via_expression[6] == 36

    # When the keys are simple strings, it is sometimes easier to specify pairs using
    # keyword arguments.
    dictionary_for_string_keys = dict(sape=4139, guido=4127, jack=4098)
    assert dictionary_for_string_keys['sape'] == 4139
    assert dictionary_for_string_keys['guido'] == 4127
    assert dictionary_for_string_keys['jack'] == 4098
