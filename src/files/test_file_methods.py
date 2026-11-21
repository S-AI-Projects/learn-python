"""Methods of File Objects

@see: https://docs.python.org/3/tutorial/inputoutput.html#methods-of-file-objects

Reading from a file does not always have to be sequential. There are methods to look for
specific locations in the file, much like flipping to a page in a book.
"""

import doctest
import inspect
import io


def test_file_methods():
    """Methods of File Objects.

    Example using the contents of ``binary_file`` (``0123456789abcdef``):

    >>> from io import StringIO
    >>> multi_line_file = StringIO('first line\\nsecond line\\nthird line')
    >>> read_data = multi_line_file.read()
    >>> read_data
    'first line\\nsecond line\\nthird line'
    >>> binary_file = StringIO('0123456789abcdef')
    >>> binary_file.seek(0)
    0
    >>> binary_file.seek(6)
    6
    >>> binary_file.read(1)
    '6'
    >>> binary_file.tell()
    7
    >>> binary_file.seek(7)
    7
    >>> binary_file.read(1)
    '7'

    The key transition is that ``read(1)`` consumes the character at offset 6,
    advancing the stream to offset 7 before the neighboring read.
    """

    multi_line_file = open('src/files/multi_line_file.txt', 'r')
    binary_file = open('src/files/binary_file', 'r')

    # To read a file’s contents, call f.read(size), which reads some quantity of data and returns
    # it as a string (in text mode) or bytes object (in binary mode). size is an optional numeric
    # argument. When size is omitted or negative, the entire contents of the file will be read and
    # returned; it’s your problem if the file is twice as large as your machine’s memory. Otherwise,
    # at most size bytes are read and returned. If the end of the file has been reached, f.read()
    # will return an empty string ('').
    read_data = multi_line_file.read()

    # pylint: disable=duplicate-code
    assert read_data == 'first line\nsecond line\nthird line'

    # To change the file object’s position, use f.seek(offset, from_what). The position is computed
    # from adding offset to a reference point; the reference point is selected by the from_what
    # argument. A from_what value of 0 measures from the beginning of the file, 1 uses the current
    # file position, and 2 uses the end of the file as the reference point. from_what can be omitted
    # and defaults to 0, using the beginning of the file as the reference point.
    assert binary_file.seek(0) == 0  # Go to the 0th byte in the file
    assert binary_file.seek(6) == 6  # Go to the 6th byte in the file

    assert binary_file.read(1) == '6'

    # f.readline() reads a single line from the file; a newline character (\n) is left at the end
    # of the string, and is only omitted on the last line of the file if the file doesn’t end in a
    # newline. This makes the return value unambiguous; if f.readline() returns an empty string,
    # the end of the file has been reached, while a blank line is represented by '\n', a string
    # containing only a single newline.
    multi_line_file.seek(0)

    assert multi_line_file.readline() == 'first line\n'
    assert multi_line_file.readline() == 'second line\n'
    assert multi_line_file.readline() == 'third line'
    assert multi_line_file.readline() == ''

    multi_line_file.close()
    binary_file.close()


def test_file_methods_documented_example():
    """Execute the worked example and assert its displayed results."""
    docstring = inspect.cleandoc(test_file_methods.__doc__)
    example = doctest.DocTestParser().get_doctest(
        docstring,
        {},
        'test_file_methods',
        __file__,
        0,
    )
    displayed_output = io.StringIO()
    runner = doctest.DocTestRunner(verbose=True)
    result = runner.run(example, out=displayed_output.write)
    actual_display = displayed_output.getvalue()
    print(
        'doctest: expected failures=0, expected examples=11; '
        'actual failures={}, actual examples={}'.format(
            result.failed,
            result.attempted,
        )
    )
    print('doctest display:\n{}'.format(actual_display))
    assert result.failed == 0
    assert result.attempted == 11
    assert (
        "Expecting:\n    'first line\\nsecond line\\nthird line'\nok"
        in actual_display
    )
    assert 'Expecting:\n    6\nok' in actual_display
    assert "Expecting:\n    '6'\nok" in actual_display
    assert "Expecting:\n    '7'\nok" in actual_display
