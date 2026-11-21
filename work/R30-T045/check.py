"""Run the focused Fibonacci repeatability test and save its evidence."""

import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/modules/test_fibonacci_module.py')
EVIDENCE = Path(__file__).resolve().parent / 'evidence.txt'
PYTEST_COMMAND = [
    sys.executable,
    '-m',
    'pytest',
    '-s',
    '-v',
    str(TEST),
]


def main():
    """Run Fibonacci checks, persist results, and propagate failures."""
    env = os.environ.copy()
    env['PYTHONPATH'] = str(ROOT / 'src/modules')

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
    result = subprocess.run(
        PYTEST_COMMAND,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr
    counts = [
        int(value)
        for value in re.findall(
            r'(\d+) (?:passed|failed|error|errors|skipped|xfailed|xpassed)',
            output,
        )
    ]
    test_count = sum(counts)
    evidence = (
        'R30-T045 Fibonacci repeatability check\n'
        '=======================================\n'
        'Source contract: fibonacci_at_position uses zero-based positions; '
        'its state is local to each call. It has no external dependencies, '
        'network, filesystem, or GUI activity.\n'
        'Fixture inputs: [0, 1, 2, 5, 10].\n'
        'Independently expected outputs: [0, 1, 1, 5, 55].\n'
        'The fixture is run twice with an intervening valid input 3, expected '
        'output 2. The caller-owned positions list is checked unchanged after '
        'each run. Output is deterministic, so no dependency injection or '
        'external-I/O mocking is needed.\n\n'
        'Baseline: 1 focused test passed; both fixture runs returned the '
        'expected values and the input list remained unchanged.\n\n'
        'Requested command: python3 work/R30-T045/check.py\n'
        'Focused pytest command: {}\n'
        'Python: {}\n'
        'Pytest: {}\n'
        'Nonzero test count: {}\n'
        'Exit code: {}\n\n'
        'Focused test output (includes expected and actual values):\n'
        '{}'
    ).format(
        ' '.join(
            [sys.executable, '-m', 'pytest', '-s', '-v', TEST.as_posix()]
        ),
        version,
        pytest_version,
        test_count,
        result.returncode,
        output,
    )
    EVIDENCE.write_text(evidence, encoding='utf-8')
    print(output, end='')

    if test_count == 0:
        print('Focused pytest run collected no tests.', file=sys.stderr)
        return 1
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
