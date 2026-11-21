"""Contract tests for the AIF reader mock."""

from sound_package.formats.aif import aif_read


def test_aif_read_smallest_supported_call():
    """The reader's smallest and only ordinary invocation returns its fixed result."""
    # aif.py:4 establishes that the reader accepts no arguments.
    actual = aif_read()
    expected = 'Read from AIF file'
    print('smallest supported call: expected={!r}, actual={!r}'.format(expected, actual))
    assert actual == expected


def test_aif_read_repeated_calls_return_expected_values():
    """Repeated reads return the same value without accepting mutable input."""
    # aif.py:4 establishes the no-argument precondition; aif.py:6 is the fixed-result contract.
    actual = (aif_read(), aif_read())
    expected = ('Read from AIF file', 'Read from AIF file')
    print('repeated calls: expected={!r}, actual={!r}'.format(expected, actual))
    assert actual == expected
