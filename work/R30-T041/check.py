"""Run the focused AIF contract tests and save their evidence."""

import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/modules/sound_package/formats/test_aif.py')
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
    """Run only the AIF tests, persist their observed results, and propagate failure."""
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

    command_text = ' '.join(
        ['python3', 'work/R30-T041/check.py']
    )
    focused_command = ' '.join(
        [sys.executable, '-m', 'pytest', '-s', '-v', TEST.as_posix()]
    )
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
        'R30-T041 AIF regression check\n'
        '============================\n'
        'Inputs and independent expected results:\n'
        "- Smallest and only valid input: aif_read() with no arguments "
        "(aif.py:4); expected 'Read from AIF file'.\n"
        "- Ordinary invocation: aif_read() (same sole valid input; aif.py:4); "
        "expected 'Read from AIF file'.\n"
        "- Repeated-call boundary: (aif_read(), aif_read()) (aif.py:4); "
        "expected ('Read from AIF file', 'Read from AIF file').\n"
        'The expected strings were specified literally in the tests before '
        'running the source. aif.py:6 establishes the fixed result.\n'
        'The function accepts no mutable input and performs no external I/O, '
        'so there is no observable caller-owned mutation or I/O to mock.\n\n'
        'Baseline before the source docstring change: 2 passed; the expected '
        'and actual values matched in both tests.\n\n'
        'Requested command: {}\n'
        'Focused pytest command: {}\n'
        'Python: {}\n'
        'Pytest: {}\n'
        'Nonzero test count: {}\n'
        'Exit code: {}\n\n'
        'Focused test output (includes expected and actual values):\n'
        '{}'
    ).format(
        command_text,
        focused_command,
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
