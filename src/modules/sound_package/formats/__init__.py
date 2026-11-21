"""Formats package initialization.

Provides format identification and supported format listings for sound_package.
"""

__all__ = ['wav', 'aif']

SUPPORTED_FORMATS = ('wav', 'aif')


def is_supported_format(format_name):
    """Check if an audio format extension or name is supported.

    Preconditions:
    - line 7: SUPPORTED_FORMATS = ('wav', 'aif') establishes the supported formats.

    Contract:
    - Smallest valid input: 'wav' -> True
    - Ordinary valid input: 'aif' -> True
    - Case-insensitive / prefixed input: '.WAV' -> True
    - Unsupported input: 'mp3' -> False
    - Non-string input: None or 123 -> False

    Does not mutate input arguments or global state.
    """
    if not isinstance(format_name, str):
        return False
    normalized = format_name.lower().lstrip('.')
    return normalized in SUPPORTED_FORMATS
