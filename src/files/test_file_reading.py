"""Reading and Writing Files

@see: https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files

The process of reading and writing to a file is like finding a book and opening a book.
First, the file is located, opened to the first page, then reading/writing begins until it reaches
the end of the file.
"""
import sys


def test_files_open():
    """Open files

    open() returns a file object, and is most commonly used with two arguments:
    open(filename, mode).

    The first argument is a string containing the filename. The second argument is another string
    containing a few characters describing the way in which the file will be used. mode can be:

    - 'r' when the file will only be read,
    - 'w' for only writing (an existing file with the same name will be erased),
    - 'a' opens the file for appending; any data written to the file is automatically added to end.
    - 'r+' opens the file for both reading and writing.

    The mode argument is optional; 'r' will be assumed if it’s omitted.

    Normally, files are opened in text mode, that means, you read and write strings from and to the
    file, which are encoded in a specific encoding. If encoding is not specified, the default is
    platform dependent (see open()). 'b' appended to the mode opens the file in binary mode: now
    the data is read and written in the form of bytes objects. This mode should be used for all
    files that don’t contain text.

    In text mode, the default when reading is to convert platform-specific line endings (\n on
    Unix, \r\n on Windows) to just \n. When writing in text mode, the default is to convert
    occurrences of \n back to platform-specific line endings. This behind-the-scenes modification
    to file data is fine for text files, but will corrupt binary data like that in JPEG or EXE
    files. Be very careful to use binary mode when reading and writing such files.

    It is good practice to use the with keyword when dealing with file objects. The advantage is
    that the file is properly closed after its suite finishes, even if an exception is raised at
    some point. Using with is also much shorter than writing equivalent try-finally blocks:
    """

    # Open files without using 'with' statement.
    file = open('src/files/multi_line_file.txt', 'r')

    # Source anchor 1: file state before read
    assert file.closed is False

    read_data = file.read()

    # Source anchor 2: exact read content
    assert read_data == (
        'first line\n'
        'second line\n'
        'third line'
    )

    file.close()

    # Source anchor 3: file state after close
    assert file.closed is True

    # Open file using with.
    with open('src/files/multi_line_file.txt', 'r') as file:
        assert file.closed is False
        read_data = file.read()

        assert read_data == (
            'first line\n'
            'second line\n'
            'third line'
        )

    assert file.closed is True

    # Neighboring supported input derived independently:
    # Reading binary_file in text mode ('r') yields '0123456789abcdef'
    with open('src/files/binary_file', 'r') as neighboring_file:
        assert neighboring_file.closed is False
        binary_read_data = neighboring_file.read()
        assert binary_read_data == '0123456789abcdef'

    assert neighboring_file.closed is True


def test_file_reading_oracle_comparison():
    """Independent reference comparison for file reading contract.

    Source anchors:
      assert not file.closed -> assert file.closed is False
      assert read_data == ('first line\n' 'second line\n' 'third line')
      assert file.closed -> assert file.closed is True

    Oracle verification:
      - Evaluates at least 20 small valid inputs (read sizes 0..20, 33, 50).
      - Compares stream read outputs against an independently calculated ground truth table.
      - Confirms that repeated runs with fresh equivalent inputs yield identical results.
      - Verifies return value of test_files_open() is None with zero observable module mutation.
    """
    # Explicit ground-truth reference table for small read sizes:
    ground_truth = {
        0: '',
        1: 'f',
        2: 'fi',
        3: 'fir',
        4: 'firs',
        5: 'first',
        6: 'first ',
        7: 'first l',
        8: 'first li',
        9: 'first lin',
        10: 'first line',
        11: 'first line\n',
        12: 'first line\ns',
        13: 'first line\nse',
        14: 'first line\nsec',
        15: 'first line\nseco',
        16: 'first line\nsecon',
        17: 'first line\nsecond',
        18: 'first line\nsecond ',
        19: 'first line\nsecond l',
        20: 'first line\nsecond li',
        33: 'first line\nsecond line\nthird line',
        50: 'first line\nsecond line\nthird line',
    }

    # Evaluate all 23 inputs against fresh stream reads
    for size, expected in ground_truth.items():
        with open('src/files/multi_line_file.txt', 'r') as f:
            assert f.closed is False
            actual = f.read(size)
            assert actual == expected, (
                f"Mismatch at size {size}: expected {expected!r}, got {actual!r}"
            )
        assert f.closed is True

    # Repeated runs with fresh equivalent inputs give the same result
    for _ in range(2):
        with open('src/files/multi_line_file.txt', 'r') as f:
            assert f.read(5) == 'first'

    # Verify return value and zero module mutation
    current_module = sys.modules[__name__]
    attrs_before = set(dir(current_module))

    ret = test_files_open()
    assert ret is None

    attrs_after = set(dir(current_module))
    assert attrs_before == attrs_after
