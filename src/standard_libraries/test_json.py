"""Serialization.

@see: https://www.learnpython.org/en/Serialization

Python provides built-in JSON libraries to encode and decode JSON.
"""

import json


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


def test_json_repeatability_and_isolation():
    """Verify input isolation and deterministic repeatability for JSON operations.

    External dependencies: None (pure serialization/deserialization functions).

    Source anchors:
      assert person_dictionary['first_name'] == 'John'
      assert person_dictionary['age'] == 42
      assert person_parsed_dictionary == person_dictionary

    Neighboring supported input derived independently:
      dict: {'first_name': 'Jane', 'last_name': 'Doe', 'age': 30}
      json: '{"first_name": "Jane", "last_name": "Doe", "age": 30}'
    """
    anchor_dict = {'first_name': 'John', 'last_name': 'Smith', 'age': 42}
    anchor_json = '{"first_name": "John", "last_name": "Smith", "age": 42}'

    # First run in fresh isolated state
    parsed_1 = json.loads(anchor_json)
    assert parsed_1 == anchor_dict
    assert parsed_1['first_name'] == 'John'
    assert parsed_1['age'] == 42
    assert json.dumps(anchor_dict) == anchor_json

    # Interleaved run with neighboring supported input
    neighbor_dict = {'first_name': 'Jane', 'last_name': 'Doe', 'age': 30}
    neighbor_json = '{"first_name": "Jane", "last_name": "Doe", "age": 30}'
    parsed_neighbor = json.loads(neighbor_json)
    assert parsed_neighbor == neighbor_dict
    assert parsed_neighbor['first_name'] == 'Jane'
    assert parsed_neighbor['age'] == 30
    assert json.dumps(neighbor_dict) == neighbor_json

    # Second run of anchor fixture to prove isolation (no mutation leakage from neighbor run)
    parsed_2 = json.loads(anchor_json)
    assert parsed_2 == anchor_dict
    assert parsed_2['first_name'] == 'John'
    assert parsed_2['age'] == 42
    assert json.dumps(anchor_dict) == anchor_json

