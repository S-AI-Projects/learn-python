"""Test tuple correctness and measure reproducible indexing scaling."""

import os
from pathlib import Path
import platform
import random
import re
import statistics
import subprocess
import sys
import timeit


ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/data_types/test_tuples.py')
EVIDENCE = Path(__file__).resolve().parent / 'evidence.txt'
SIZES = (16, 1024, 65536)
REPETITIONS = 5
OPERATIONS_PER_REPETITION = 100000
SEED = 49049
PYTEST_COMMAND = [
    sys.executable,
    '-m',
    'pytest',
    '-s',
    '-v',
    str(TEST),
]


def run_scaling_experiment():
    """Measure indexing; input setup and correctness checks stay untimed."""
    measurements = []
    summaries = []
    for size in SIZES:
        samples_ns = []
        for repetition in range(REPETITIONS):
            seed = SEED + size * 10 + repetition
            generator = random.Random(seed)
            expected = generator.randrange(1_000_000)
            items = [expected]
            items.extend(
                generator.randrange(1_000_000) for _ in range(size - 1)
            )
            values = tuple(items)

            actual_before = values[0]
            assert actual_before == expected

            timer = timeit.Timer('values[0]', globals={'values': values})
            elapsed = timer.timeit(number=OPERATIONS_PER_REPETITION)

            actual_after = values[0]
            assert actual_after == expected
            sample_ns = elapsed * 1_000_000_000 / OPERATIONS_PER_REPETITION
            samples_ns.append(sample_ns)
            measurements.append(
                (size, repetition + 1, seed, expected, actual_after, sample_ns)
            )

        summaries.append(
            (
                size,
                statistics.median(samples_ns),
                (min(samples_ns), max(samples_ns)),
            )
        )
    return measurements, summaries


def main():
    """Run tests and benchmark, save evidence, and propagate failures."""
    env = os.environ.copy()
    result = subprocess.run(
        PYTEST_COMMAND,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    test_output = result.stdout + result.stderr
    test_output = '\n'.join(
        line.rstrip() for line in test_output.splitlines()
    ) + '\n'
    counts = [
        int(value)
        for value in re.findall(
            r'(\d+) (?:passed|failed|error|errors|skipped|xfailed|xpassed)',
            test_output,
        )
    ]
    test_count = sum(counts)

    measurements, summaries = run_scaling_experiment()

    version = subprocess.run(
        [sys.executable, '--version'],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    pytest_version = subprocess.run(
        [sys.executable, '-m', 'pytest', '--version'],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    measurement_lines = [
        'n={}, repetition={}, seed={}, expected={!r}, actual={!r}, '
        'ns_per_index={:.3f}'.format(*measurement)
        for measurement in measurements
    ]
    summary_lines = [
        'n={}, median_ns_per_index={:.3f}, range_ns_per_index=({:.3f}, {:.3f})'
        .format(size, median, bounds[0], bounds[1])
        for size, median, bounds in summaries
    ]
    evidence = (
        'R30-T049 tuple-index scaling experiment\n'
        '=======================================\n'
        'Correctness fixture: fruits_tuple=("apple", "banana", "cherry"); '
        'expected type tuple, index 0 "apple", index 1 "banana".\n'
        'Neighbor regression: ("pear", "banana", "cherry", "date"); expected '
        'index 0 and -1 results ("pear", "date").\n'
        'Measured operation: values[0], corresponding to tuple indexing in '
        'test_tuples. Input-size variable n is tuple length. CPython tuple '
        'indexing is O(1) worst-case; the observed timings below are not a '
        'proof and have no pass/fail threshold.\n'
        'Method: inputs generated with fixed seeds; a fresh tuple per '
        'repetition; 5 repetitions at each of n=16, 1024, 65536; 100000 '
        'index operations per sample. Tuple generation and expected/actual '
        'checks occur outside the timed interval. timeit compiles the '
        'statement before timing. Process startup and pytest are not timed; '
        'the timeit loop overhead remains included. No file/network/UI I/O '
        'is involved.\n\n'
        'Focused pytest command: {}\n'
        'Requested command: python3 work/R30-T049/check.py\n'
        'Python: {}\n'
        'Pytest: {}\n'
        'Platform: {}\n'
        'Nonzero pytest test count: {}\n'
        'Pytest exit code: {}\n\n'
        'Per-repetition correctness and timing observations (nanoseconds per '
        'index):\n{}\n\n'
        'Median and min/max range per input size:\n{}\n\n'
        'Focused pytest output:\n{}'
    ).format(
        ' '.join(
            [sys.executable, '-m', 'pytest', '-s', '-v', TEST.as_posix()]
        ),
        version,
        pytest_version,
        platform.platform(),
        test_count,
        result.returncode,
        '\n'.join(measurement_lines),
        '\n'.join(summary_lines),
        test_output,
    )
    EVIDENCE.write_text(evidence, encoding='utf-8')
    print(test_output, end='')
    print('\n'.join(summary_lines))

    if test_count == 0:
        print('Focused pytest run collected no tests.', file=sys.stderr)
        return 1
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
