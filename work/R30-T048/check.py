"""Run the focused class-object path checks and save their evidence."""

import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/classes/test_class_objects.py')
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
    """Run class-object checks, save results, and propagate failures."""
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
        'R30-T048 class-object empty-state check\n'
        '=======================================\n'
        'Source path: test_class_objects defines ComplexNumber at line 26, '
        'with class attributes real=0 and imaginary=0 at lines 29-30. It '
        'changes real to 10 at line 56; the no-argument construction at line '
        '68 reaches the empty-instance path because the class has no '
        '__init__.\n'
        'Expected empty instance dictionary: {{}}. Expected class-fallback '
        'values: real=10 and imaginary=0. The assertions verify the instance '
        'dictionary stays empty after attribute reads and the class value '
        'remains 10. This total, valid path raises no exception.\n'
        'The subsequent constructor call uses (3.0, -4.5) and expects the '
        'same tuple of instance values, demonstrating a successful call after '
        'the empty-state case. The constructor assertion now checks both '
        'fields (the previous comma-separated assert checked only truthiness '
        'of real).\n'
        'There is no network, filesystem, GUI, or external dependency.\n\n'
        'Baseline before explanatory comments and assertion correction: 1 '
        'focused test passed with the added empty-state assertions.\n\n'
        'Requested command: python3 work/R30-T048/check.py\n'
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
