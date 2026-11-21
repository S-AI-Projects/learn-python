"""Run the focused regex reference comparisons and save their evidence."""

import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/standard_libraries/test_re.py')
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
    """Run only the regex example tests, persist results, and propagate failures."""
    env = os.environ.copy()
    env['PYTHONPATH'] = str(ROOT / 'src')

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
        'R30-T043 regex reference check\n'
        '===============================\n'
        'Source anchors in src/standard_libraries/test_re.py:test_re:\n'
        '- The findall fixture returns foot, fell, fastest.\n'
        '- The re.sub fixture reduces the adjacent repeated word in '
        "'cat in the the hat' to 'cat in the hat'.\n"
        "- The str.replace fixture maps 'tea for too' to 'tea for two'.\n\n"
        'Public contract: string inputs; findall returns a list; re.sub and '
        'str.replace return strings. Inputs are immutable; no external I/O or '
        'input mutation.\n'
        'Independent findall reference: split the restricted lowercase-word '
        'inputs into tokens and select tokens whose first character is f; this '
        'does not call re or reproduce the regex algorithm.\n'
        'Enumerated domain: the empty string, each of a/f/fa/ff, and all 16 '
        'ordered two-token combinations (21 total). Each expected result is '
        'compared with re.findall, and test output records input, expected, and '
        'actual values.\n'
        'Independent fixed sub cases include a a -> a, a a a -> a a, '
        'a a a a -> a a, a a b b -> a b, and cat dog -> cat dog.\n'
        "Neighboring replace input: 'tea for too too' -> 'tea for two two'.\n"
        "Fresh equivalent inputs 'foot' and 'foot' both independently expect "
        "['foot'].\n\n"
        'Baseline before documentation/runner changes: 5 passed; no mismatch '
        'occurred, so no failure reduction or implementation fix was needed.\n\n'
        'Requested command: python3 work/R30-T043/check.py\n'
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
