"""String Pattern Matching.

@see: https://docs.python.org/3/tutorial/stdlib.html#string-pattern-matching

The re module provides regular expression tools for advanced string processing.
For complex matching and manipulation, regular expressions offer succinct, optimized solutions:

These examples take immutable strings: findall returns a list, while sub and replace return new
strings. They do not mutate their inputs or perform external I/O.
"""

import re


def _find_f_words_reference(text):
    """Find f-prefixed tokens without using regular expressions."""
    return [word for word in text.split() if word.startswith('f')]


def test_re():
    """String Pattern Matching.

    The pattern r'\\bf[a-z]*' finds 'foot', 'fell', and 'fastest' because each
    starts at a word boundary and contains only lowercase letters after f.
    """

    assert re.findall(r'\bf[a-z]*', 'which foot or hand fell fastest') == [
        'foot',
        'fell',
        'fastest'
    ]

    assert re.sub(r'(\b[a-z]+) \1', r'\1', 'cat in the the hat') == 'cat in the hat'

    # When only simple capabilities are needed, string methods are preferred because they are
    # easier to read and debug:
    assert 'tea for too'.replace('too', 'two') == 'tea for two'


def test_findall_matches_independent_reference_for_small_inputs():
    """Compare findall with a token-based oracle over 21 lowercase inputs."""
    tokens = ('a', 'f', 'fa', 'ff')
    small_inputs = ['']
    small_inputs.extend(tokens)
    small_inputs.extend(
        '{} {}'.format(first, second)
        for first in tokens
        for second in tokens
    )
    print(
        'findall reference case count: expected=21, actual={!r}'.format(
            len(small_inputs)
        )
    )
    assert len(small_inputs) == 21

    for text in small_inputs:
        expected = _find_f_words_reference(text)
        actual = re.findall(r'\bf[a-z]*', text)
        print(
            'findall input={!r}: expected={!r}, actual={!r}'.format(
                text, expected, actual
            )
        )
        assert actual == expected


def test_sub_matches_explicit_reference_cases():
    """Check repeated-word substitutions against independently fixed results."""
    cases = [
        ('cat in the the hat', 'cat in the hat'),
        ('a a', 'a'),
        ('a a a', 'a a'),
        ('a a a a', 'a a'),
        ('a a b b', 'a b'),
        ('cat dog', 'cat dog'),
    ]

    for text, expected in cases:
        actual = re.sub(r'(\b[a-z]+) \1', r'\1', text)
        print(
            'sub input={!r}: expected={!r}, actual={!r}'.format(
                text, expected, actual
            )
        )
        assert actual == expected


def test_replace_neighboring_input():
    """Replacing both occurrences produces the independently expected string."""
    text = 'tea for too too'
    expected = 'tea for two two'
    actual = text.replace('too', 'two')
    print('replace input={!r}: expected={!r}, actual={!r}'.format(text, expected, actual))
    assert actual == expected


def test_findall_is_repeatable_with_fresh_equivalent_inputs():
    """Equivalent separately constructed strings produce the same result."""
    first_input = ''.join(('f', 'oot'))
    second_input = ''.join(('fo', 'ot'))
    expected = ['foot']
    first_actual = re.findall(r'\bf[a-z]*', first_input)
    second_actual = re.findall(r'\bf[a-z]*', second_input)
    print(
        'fresh equivalent inputs: expected={!r}, actual={!r}'.format(
            expected, (first_actual, second_actual)
        )
    )
    assert first_actual == expected
    assert second_actual == expected
