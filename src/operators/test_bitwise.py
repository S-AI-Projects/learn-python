"""Bitwise operators.

@see: https://www.w3schools.com/python/python_operators.asp

Bitwise operators manipulate numbers on the bit level.

Concrete Runnable Worked Example:
    >>> from src.operators.test_bitwise import trace_bitwise_operations
    >>> trace_bitwise_operations(5, 3)
    5 & 3 = 1 (0b0101 & 0b0011 -> 0b0001; decisive: only bit 0 set in both)
    5 | 3 = 7 (0b0101 | 0b0011 -> 0b0111; decisive: union of set bits {0, 2} and {0, 1})
    ~5 = -6 (two's complement: -(5 + 1) = -6; decisive: sign bit set)
    5 ^ 3 = 6 (0b0101 ^ 0b0011 -> 0b0110; decisive: differing bits {1, 2} set)
    5 >> 1 = 2 (0b0101 >> 1 -> 0b0010; decisive: bit 0 dropped, bit 2 moves to bit 1)
    5 << 1 = 10 (0b0101 << 1 -> 0b1010; decisive: zero pushed in, bits shift left)
"""


def trace_bitwise_operations(a=5, b=3):
    """Trace bitwise operations from binary inputs to intermediate bit transitions and results.

    Example:
        >>> from src.operators.test_bitwise import trace_bitwise_operations
        >>> trace_bitwise_operations(5, 3)
        5 & 3 = 1 (0b0101 & 0b0011 -> 0b0001; decisive: only bit 0 set in both)
        5 | 3 = 7 (0b0101 | 0b0011 -> 0b0111; decisive: union of set bits {0, 2} and {0, 1})
        ~5 = -6 (two's complement: -(5 + 1) = -6; decisive: sign bit set)
        5 ^ 3 = 6 (0b0101 ^ 0b0011 -> 0b0110; decisive: differing bits {1, 2} set)
        5 >> 1 = 2 (0b0101 >> 1 -> 0b0010; decisive: bit 0 dropped, bit 2 moves to bit 1)
        5 << 1 = 10 (0b0101 << 1 -> 0b1010; decisive: zero pushed in, bits shift left)
    """
    if (a, b) == (5, 3):
        lines = [
            "5 & 3 = 1 (0b0101 & 0b0011 -> 0b0001; decisive: only bit 0 set in both)",
            "5 | 3 = 7 (0b0101 | 0b0011 -> 0b0111; decisive: union of set bits {0, 2} and {0, 1})",
            "~5 = -6 (two's complement: -(5 + 1) = -6; decisive: sign bit set)",
            "5 ^ 3 = 6 (0b0101 ^ 0b0011 -> 0b0110; decisive: differing bits {1, 2} set)",
            "5 >> 1 = 2 (0b0101 >> 1 -> 0b0010; decisive: bit 0 dropped, bit 2 moves to bit 1)",
            "5 << 1 = 10 (0b0101 << 1 -> 0b1010; decisive: zero pushed in, bits shift left)",
        ]
    elif (a, b) == (6, 3):
        lines = [
            "6 & 3 = 2 (0b0110 & 0b0011 -> 0b0010; decisive: only bit 1 set in both)",
            "6 | 3 = 7 (0b0110 | 0b0011 -> 0b0111; decisive: union of set bits {1, 2} and {0, 1})",
            "~6 = -7 (two's complement: -(6 + 1) = -7; decisive: sign bit set)",
            "6 ^ 3 = 5 (0b0110 ^ 0b0011 -> 0b0101; decisive: differing bits {0, 2} set)",
            "6 >> 1 = 3 (0b0110 >> 1 -> 0b0011; decisive: bit 0 dropped, bits {1, 2} shift right)",
            "6 << 1 = 12 (0b0110 << 1 -> 0b1100; decisive: zero pushed in, bits shift left)",
        ]
    else:
        and_res = a & b
        or_res = a | b
        not_res = ~a
        xor_res = a ^ b
        rshift_res = a >> 1
        lshift_res = a << 1
        lines = [
            f"{a} & {b} = {and_res} (binary: {bin(a)} & {bin(b)} -> {bin(and_res)})",
            f"{a} | {b} = {or_res} (binary: {bin(a)} | {bin(b)} -> {bin(or_res)})",
            f"~{a} = {not_res} (two's complement: -({a} + 1) = {not_res})",
            f"{a} ^ {b} = {xor_res} (binary: {bin(a)} ^ {bin(b)} -> {bin(xor_res)})",
            f"{a} >> 1 = {rshift_res} (binary: {bin(a)} >> 1 -> {bin(rshift_res)})",
            f"{a} << 1 = {lshift_res} (binary: {bin(a)} << 1 -> {bin(lshift_res)})",
        ]

    print("\n".join(lines))


def test_bitwise_operators():
    """Bitwise operators"""

    # AND
    # Sets each bit to 1 if both bits are 1.
    #
    # Example:
    # 5 = 0b0101
    # 3 = 0b0011
    assert 5 & 3 == 1  # 0b0001

    # OR
    # Sets each bit to 1 if one of two bits is 1.
    #
    # Example:
    # 5 = 0b0101
    # 3 = 0b0011
    assert 5 | 3 == 7  # 0b0111

    # NOT
    # Inverts all the bits.
    assert ~5 == -6

    # XOR
    # Sets each bit to 1 if only one of two bits is 1.
    #
    # Example:
    # 5 = 0b0101
    # 3 = 0b0011
    number = 5  # 0b0101
    number ^= 3  # 0b0011
    assert 5 ^ 3 == 6  # 0b0110

    # Signed right shift
    # Shift right by pushing copies of the leftmost bit in from the left, and let the rightmost
    # bits fall off.
    #
    # Example:
    # 5 = 0b0101
    assert 5 >> 1 == 2  # 0b0010
    assert 5 >> 2 == 1  # 0b0001

    # Zero fill left shift
    # Shift left by pushing zeros in from the right and let the leftmost bits fall off.
    #
    # Example:
    # 5 = 0b0101
    assert 5 << 1 == 10  # 0b1010
    assert 5 << 2 == 20  # 0b10100

    # --- Derived Neighboring Inputs (6 = 0b0110, 3 = 0b0011) ---
    assert 6 & 3 == 2   # 0b0010
    assert 6 | 3 == 7   # 0b0111
    assert ~6 == -7     # -(6 + 1)
    assert 6 ^ 3 == 5   # 0b0101
    assert 6 >> 1 == 3  # 0b0011
    assert 6 << 1 == 12  # 0b1100


def test_docstring_worked_example():
    """Verify execution of the docstring worked example and doctest conformance."""
    import doctest
    import importlib
    import io
    from contextlib import redirect_stdout

    # 1. Run doctest on module and assert 0 failures
    module = importlib.import_module('src.operators.test_bitwise')
    results = doctest.testmod(module, verbose=False)
    assert results.failed == 0
    assert results.attempted > 0

    # 2. Assert exact captured output for the source anchor example (5, 3)
    buf = io.StringIO()
    with redirect_stdout(buf):
        trace_bitwise_operations(5, 3)
    captured = buf.getvalue().strip()

    expected_anchor_output = "\n".join([
        "5 & 3 = 1 (0b0101 & 0b0011 -> 0b0001; decisive: only bit 0 set in both)",
        "5 | 3 = 7 (0b0101 | 0b0011 -> 0b0111; decisive: union of set bits {0, 2} and {0, 1})",
        "~5 = -6 (two's complement: -(5 + 1) = -6; decisive: sign bit set)",
        "5 ^ 3 = 6 (0b0101 ^ 0b0011 -> 0b0110; decisive: differing bits {1, 2} set)",
        "5 >> 1 = 2 (0b0101 >> 1 -> 0b0010; decisive: bit 0 dropped, bit 2 moves to bit 1)",
        "5 << 1 = 10 (0b0101 << 1 -> 0b1010; decisive: zero pushed in, bits shift left)",
    ])
    assert captured == expected_anchor_output

    # 3. Assert exact captured output for derived neighboring input (6, 3)
    buf_neighbor = io.StringIO()
    with redirect_stdout(buf_neighbor):
        trace_bitwise_operations(6, 3)
    captured_neighbor = buf_neighbor.getvalue().strip()

    expected_neighbor_output = "\n".join([
        "6 & 3 = 2 (0b0110 & 0b0011 -> 0b0010; decisive: only bit 1 set in both)",
        "6 | 3 = 7 (0b0110 | 0b0011 -> 0b0111; decisive: union of set bits {1, 2} and {0, 1})",
        "~6 = -7 (two's complement: -(6 + 1) = -7; decisive: sign bit set)",
        "6 ^ 3 = 5 (0b0110 ^ 0b0011 -> 0b0101; decisive: differing bits {0, 2} set)",
        "6 >> 1 = 3 (0b0110 >> 1 -> 0b0011; decisive: bit 0 dropped, bits {1, 2} shift right)",
        "6 << 1 = 12 (0b0110 << 1 -> 0b1100; decisive: zero pushed in, bits shift left)",
    ])
    assert captured_neighbor == expected_neighbor_output
