"""Data Compression.

@see: https://docs.python.org/3/tutorial/stdlib.html#data-compression

Common data archiving and compression formats are directly supported by modules including: zlib,
gzip, bz2, lzma, zipfile and tarfile.
"""

import zlib


def test_zlib():
    """zlib."""
    string = b'witch which has which witches wrist watch'
    assert len(string) == 41

    zlib_compressed_string = zlib.compress(string)
    assert len(zlib_compressed_string) == 37

    zlib_decompressed_string = zlib.decompress(zlib_compressed_string)
    assert zlib_decompressed_string == b'witch which has which witches wrist watch'

    assert zlib.crc32(string) == 226805979


def test_zlib_empty_bytes_boundary():
    """Empty bytes are the minimum input for the compress/decompress calls above.

    Boundary table (test_zlib lines 17 and 20): b'' -> b''; b'\\x00' -> b'\\x00'.
    The 41-byte fixture at lines 14-21 is ordinary input, not a minimum-size rule.
    """
    input_bytes = b''
    expected = b''
    actual = zlib.decompress(zlib.compress(input_bytes))
    print('empty bytes: expected={!r}, actual={!r}'.format(expected, actual))
    assert actual == expected


def test_zlib_one_byte_neighbor():
    """The first non-empty supported input round-trips to its original byte."""
    input_bytes = b'\x00'
    expected = b'\x00'
    actual = zlib.decompress(zlib.compress(input_bytes))
    print('one-byte neighbor: expected={!r}, actual={!r}'.format(expected, actual))
    assert actual == expected

    expected_crc32 = 3523407757
    actual_crc32 = zlib.crc32(input_bytes)
    print(
        'one-byte CRC-32: expected={!r}, actual={!r}'.format(
            expected_crc32, actual_crc32
        )
    )
    assert actual_crc32 == expected_crc32
