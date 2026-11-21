"""Generators.

@see: https://www.learnpython.org/en/Generators

Generators are used to create iterators, but with a different approach. Generators are simple
functions which return an iterable set of items, one at a time, in a special way.

When an iteration over a set of item starts using the for statement, the generator is run. Once the
generator's function code reaches a "yield" statement, the generator yields its execution back to
the for loop, returning a new value from the set. The generator function can generate as many
values (possibly infinite) as it wants, yielding each one in its turn.
"""

import random
from unittest.mock import patch
import pytest


def lottery():
    """Generator function example.

    Here is a simple example of a generator function which returns random integers.
    This function decides how to generate the random numbers on its own, and executes the yield
    statements one at a time, pausing in between to yield execution back to the main for loop.
    """
    # returns first 3 random numbers between 1 and 10
    # pylint: disable=unused-variable
    for _ in range(3):
        yield random.randint(1, 10)

    # returns a 4th number between 10 and 20
    yield random.randint(10, 20)


def test_generators():
    """Yield statement"""
    for number_index, random_number in enumerate(lottery()):
        if number_index < 3:
            assert 0 <= random_number <= 10
        else:
            assert 10 <= random_number <= 20


def test_generators_boundaries():
    """Verify supported boundaries and neighbor transitions for lottery generator.

    Boundary Table (cites lines 26-30 and lines 35-39):
    - Yield index 0, 1, 2 (index < 3):
        * Source contract: random.randint(1, 10)
        * Supported assertion boundary: 0 <= random_number <= 10
        * Smallest supported value: 1
        * Largest supported value: 10
    - Yield index 3 (index >= 3, neighboring index transition from 2 to 3):
        * Source contract: random.randint(10, 20)
        * Supported assertion boundary: 10 <= random_number <= 20
        * Smallest supported value: 10
        * Largest supported value: 20
    - Yield count: exactly 4 items, followed by StopIteration
    """
    gen = lottery()
    items = []
    for _ in range(4):
        items.append(next(gen))

    # Assert exactly 4 items generated
    assert len(items) == 4

    # Assert 5th call raises StopIteration (boundary of sequence length)
    with pytest.raises(StopIteration):
        next(gen)

    # Assert bounds on actual random run
    for idx in range(3):
        assert 1 <= items[idx] <= 10
        assert 0 <= items[idx] <= 10
        print(f"index {idx}: actual={items[idx]}, expected in [1, 10]")

    assert 10 <= items[3] <= 20
    print(f"index 3: actual={items[3]}, expected in [10, 20]")


def test_generators_mocked_domain_boundaries():
    """Verify exact lower, upper, and neighboring domain boundaries using controlled values."""
    # Test lower boundaries: indices 0..2 produce 1, index 3 produces 10
    with patch('random.randint', side_effect=[1, 1, 1, 10]):
        gen_low = lottery()
        low_vals = list(gen_low)
        for idx in range(3):
            assert 0 <= low_vals[idx] <= 10
            assert low_vals[idx] == 1
        assert 10 <= low_vals[3] <= 20
        assert low_vals[3] == 10
        print(f"lower boundaries: values={low_vals}")

    # Test upper boundaries: indices 0..2 produce 10, index 3 produces 20
    with patch('random.randint', side_effect=[10, 10, 10, 20]):
        gen_high = lottery()
        high_vals = list(gen_high)
        for idx in range(3):
            assert 0 <= high_vals[idx] <= 10
            assert high_vals[idx] == 10
        assert 10 <= high_vals[3] <= 20
        assert high_vals[3] == 20
        print(f"upper boundaries: values={high_vals}")
