"""Run the file-method tests and save the executable example's evidence."""

import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/files/test_file_methods.py')
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
    """Run file-method tests, save output, and propagate failures."""
    env = os.environ.copy()
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
    evidence = (
        'R30-T047 executable file-method example\n'
        '========================================\n'
        'Text input: first line, second line, third line separated by newlines; '
        'read() returns the joined contents without a final newline.\n'
        'Seek input: in-memory text stream containing 0123456789abcdef.\n'
        'Expected intermediate states: seek(0) -> position 0; seek(6) -> '
        'position 6; read(1) -> character 6 and position 7.\n'
        'Neighbor input: seek(7) -> position 7; read(1) -> character 7.\n'
        'The decisive transition is read(1), which advances the current '
        'position from 6 to 7. The documented output is executed by doctest '
        'and asserted in test_file_methods_documented_example.\n'
        'No network, user account, or GUI is used. The worked example uses '
        'StringIO; the existing test reads only repository fixture files.\n\n'
        'Requested command: python3 work/R30-T047/check.py\n'
        'Focused pytest command: {}\n'
        'Python: {}\n'
        'Pytest: {}\n'
        'Nonzero test count: {}\n'
        'Exit code: {}\n\n'
        'Focused test output (includes doctest display):\n'
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
