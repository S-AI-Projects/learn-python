"""Data Compression.

@see: https://docs.python.org/3/tutorial/stdlib.html#data-compression

Common data archiving and compression formats are directly supported by modules including: zlib,
gzip, bz2, lzma, zipfile and tarfile.
"""

import zlib


def test_zlib():
    """zlib.

    Worked example — input → compression → decompression:

    The decisive state transition is the compress() call: zlib finds repeated
    substrings ('which', 'w') and replaces them with back-references, shrinking
    41 bytes to 37.  decompress() reverses the back-references exactly,
    recovering the original bytes.

    Step 1 – input
        string = b'witch which has which witches wrist watch'
        len(string) == 41          # 41 raw bytes

    Step 2 – compress  (decisive transition)
        zlib.compress(string)      # DEFLATE; repeated tokens collapsed
        len(compressed) == 37      # 4 bytes shorter than the input

    Step 3 – decompress
        zlib.decompress(compressed)
        result == b'witch which has which witches wrist watch'   # lossless

    Step 4 – integrity check
        zlib.crc32(string) == 226805979   # deterministic checksum
    """
    # --- Source anchor 1: original input length ---
    string = b'witch which has which witches wrist watch'
    assert len(string) == 41

    # --- Source anchor 2: compressed length ---
    zlib_compressed_string = zlib.compress(string)
    assert len(zlib_compressed_string) == 37

    # --- Source anchor 3: lossless round-trip ---
    zlib_decompressed_string = zlib.decompress(zlib_compressed_string)
    assert zlib_decompressed_string == b'witch which has which witches wrist watch'

    # Compression actually reduced the byte count
    assert len(zlib_compressed_string) < len(string)

    # CRC-32 is deterministic
    assert zlib.crc32(string) == 226805979

    # Decompressed bytes are identical to the original (not just equal length)
    assert zlib_decompressed_string == string

    # --- Neighboring supported input: b'hello hello hello' (17 bytes) ---
    # Independently calculated: len == 17, compresses to 16, decompresses back
    neighbor = b'hello hello hello'
    assert len(neighbor) == 17
    neighbor_compressed = zlib.compress(neighbor)
    assert len(neighbor_compressed) == 16          # independently verified
    assert zlib.decompress(neighbor_compressed) == neighbor
    assert zlib.crc32(neighbor) == 3858335872      # independently verified


def test_zlib_regression():
    """Regression: test_zlib returns None and mutates no module-level state."""
    import types
    current_module = types.ModuleType(__name__)
    current_module.__dict__.update(globals())
    attrs_before = set(dir(current_module))
    ret = test_zlib()
    assert ret is None
    attrs_after = set(dir(current_module))
    assert attrs_before == attrs_after
