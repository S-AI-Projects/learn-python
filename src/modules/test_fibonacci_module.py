"""Repeatability checks for fibonacci_module."""

from fibonacci_module import fibonacci_at_position


def test_fibonacci_at_position_is_repeatable_and_input_isolated():
    """Zero-based indices repeat the same values around an interleaved call."""
    positions = [0, 1, 2, 5, 10]
    original_positions = positions.copy()
    expected_results = [0, 1, 1, 5, 55]

    first_results = [
        fibonacci_at_position(position) for position in positions
    ]
    positions_after_first = positions.copy()
    interleaved_expected = 2
    interleaved_actual = fibonacci_at_position(3)
    second_results = [
        fibonacci_at_position(position) for position in positions
    ]
    positions_after_second = positions.copy()

    print(
        'indices={!r}: expected={!r}, first={!r}, second={!r}'.format(
            positions,
            expected_results,
            first_results,
            second_results,
        )
    )
    print(
        'interleaved index=3: expected={!r}, actual={!r}'.format(
            interleaved_expected,
            interleaved_actual,
        )
    )
    print(
        'input list: expected unchanged={!r}, after first={!r}, '
        'after second={!r}'.format(
            original_positions,
            positions_after_first,
            positions_after_second,
        )
    )

    assert first_results == expected_results
    assert interleaved_actual == interleaved_expected
    assert second_results == expected_results
    assert positions_after_first == original_positions
    assert positions_after_second == original_positions
