"""Serialization.

@see: https://www.learnpython.org/en/Serialization

Python provides built-in JSON libraries to encode and decode JSON.
"""

import json
import pytest


def test_json():
    """JSON serialization."""

    # There are two basic formats for JSON data. Either in a string or the object data-structure.
    # The object data-structure, in Python, consists of lists and dictionaries nested inside each
    # other. The object data-structure allows one to use python methods (for lists and dictionaries)
    # to add, list, search and remove elements from the data-structure. The String format is mainly
    # used to pass the data into another program or load into a data-structure.

    person_dictionary = {'first_name': 'John', 'last_name': 'Smith', 'age': 42}
    assert person_dictionary['first_name'] == 'John'
    assert person_dictionary['age'] == 42

    json_string = '{"first_name": "John", "last_name": "Smith", "age": 42}'

    # To load JSON back to a data structure, use the "loads" method. This method takes a string
    # and turns it back into the json object data-structure:
    person_parsed_dictionary = json.loads(json_string)

    assert person_parsed_dictionary == person_dictionary
    assert person_parsed_dictionary['first_name'] == 'John'
    assert person_parsed_dictionary['age'] == 42

    # To encode a data structure to JSON, use the "dumps" method. This method takes an object and
    # returns a String:
    encoded_person_string = json.dumps(person_dictionary)

    assert encoded_person_string == json_string


def test_json_failure_and_neighbor_contracts():
    """Cover documented failure path in json.loads (line 28) and neighboring input.

    Source anchors:
    - line 21: assert person_dictionary['first_name'] == 'John'
    - line 22: assert person_dictionary['age'] == 42
    - line 30: assert person_parsed_dictionary == person_dictionary

    Failure Path (tied to line 28 json.loads call):
    - Smallest invalid input reaching decoder failure: '{'
    - Documented exception: json.JSONDecodeError (subclass of ValueError)
    - Invariant: Caller-owned state remains valid; an ordinary call succeeds after failure.

    Neighboring supported input:
    - person_dictionary with age incremented: {'first_name': 'Jane', 'last_name': 'Smith', 'age': 43}
    - Valid empty-result case: '{}' -> {}
    """
    # 1. Exercise documented failure branch on malformed JSON
    malformed_json = '{'
    with pytest.raises(json.JSONDecodeError) as exc_info:
        json.loads(malformed_json)
    assert 'Expecting property name enclosed in double quotes' in str(exc_info.value) or 'Unterminated' in str(exc_info.value)
    print(f"Captured expected decoder failure: {exc_info.value!r}")

    # 2. Verify ordinary valid call still succeeds after failure
    valid_anchor = '{"first_name": "John", "last_name": "Smith", "age": 42}'
    recovered = json.loads(valid_anchor)
    assert recovered == {'first_name': 'John', 'last_name': 'Smith', 'age': 42}
    assert recovered['first_name'] == 'John'
    assert recovered['age'] == 42

    # 3. Neighboring supported input
    neighbor_dict = {'first_name': 'Jane', 'last_name': 'Smith', 'age': 43}
    neighbor_json = '{"first_name": "Jane", "last_name": "Smith", "age": 43}'
    neighbor_parsed = json.loads(neighbor_json)
    assert neighbor_parsed == neighbor_dict
    assert neighbor_parsed['first_name'] == 'Jane'
    assert neighbor_parsed['age'] == 43
    print(f"Neighbor input verified: {neighbor_parsed}")

    # 4. Valid empty/boundary case (total contract)
    empty_parsed = json.loads('{}')
    assert empty_parsed == {}
