"""Tests for sound_package.formats package initialization."""

from sound_package.formats import is_supported_format, SUPPORTED_FORMATS, __all__


def test_formats_init_contract():
    """Verify supported audio formats in formats/__init__.py.

    Preconditions:
    - formats/__init__.py line 7: SUPPORTED_FORMATS = ('wav', 'aif') establishes valid formats.
    - formats/__init__.py line 5: __all__ = ['wav', 'aif'] defines exported submodules.
    """
    assert list(__all__) == ['wav', 'aif']
    assert SUPPORTED_FORMATS == ('wav', 'aif')


def test_formats_init_smallest_and_ordinary_inputs():
    """Verify is_supported_format with smallest and ordinary valid inputs and boundaries.

    Preconditions established at formats/__init__.py line 7: SUPPORTED_FORMATS = ('wav', 'aif').

    Test cases:
    - Smallest valid input: 'wav' -> True
    - Ordinary valid input: 'aif' -> True
    - Prefix-stripped input: '.wav' -> True
    - Uppercase normalized input: 'AIF' -> True
    - Unsupported input: 'mp3' -> False
    - Smallest invalid input: '' -> False
    - Non-string input: None -> False
    """
    # 1. Smallest valid input
    actual_wav = is_supported_format('wav')
    print(f"smallest valid input: 'wav' -> expected=True, actual={actual_wav}")
    assert actual_wav is True

    # 2. Ordinary valid input
    actual_aif = is_supported_format('aif')
    print(f"ordinary valid input: 'aif' -> expected=True, actual={actual_aif}")
    assert actual_aif is True

    # 3. Case and dot-prefix normalization
    assert is_supported_format('.wav') is True
    assert is_supported_format('AIF') is True

    # 4. Unsupported input
    assert is_supported_format('mp3') is False

    # 5. Empty and non-string inputs
    assert is_supported_format('') is False
    assert is_supported_format(None) is False
