"""Run the focused arithmetic regression tests and save their evidence."""

import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/operators/test_arithmetic.py')
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
    """Run arithmetic tests, save results, and propagate failures."""
    env = os.environ.copy()

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
    output = '\n'.join(line.rstrip() for line in output.splitlines()) + '\n'
    counts = [
        int(value)
        for value in re.findall(
            r'(\d+) (?:passed|failed|error|errors|skipped|xfailed|xpassed)',
            output,
        )
    ]
    test_count = sum(counts)
    evidence = (
        'R30-T046 arithmetic focused refactor\n'
        '=====================================\n'
        'Contract: integer operands; addition, subtraction, and '
        'multiplication '
        'return the expected integer values. The test module has no external '
        'I/O or dependencies.\n'
        'Fixture operands: (5, 3); independently expected outputs: '
        '(8, 2, 15).\n'
        'Neighbor operands: (6, 3); independently expected outputs: '
        '(9, 3, 18).\n'
        'Refactor: name the shared operand pair in test_arithmetic_operators; '
        'the three operations and all expected values remain unchanged.\n'
        'Baseline before refactor: 2 tests passed; fixture and neighbor '
        'expected/actual outputs matched.\n\n'
        'Requested command: python3 work/R30-T046/check.py\n'
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
