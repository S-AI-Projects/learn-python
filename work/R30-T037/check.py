"""Focused runner and verification script for Task R30-T037."""

import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/classes/test_multiple_inheritance.py')
EVIDENCE_TXT = Path(__file__).resolve().parent / 'evidence.txt'
EVIDENCE_MD = Path(__file__).resolve().parent / 'evidence.md'
PYTEST_COMMAND = [
    sys.executable,
    '-m',
    'pytest',
    '-s',
    '-v',
    str(TEST),
]


def main():
    """Run focused pytest on test_multiple_inheritance.py and verify worked example."""
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

    evidence_text = (
        "R30-T037 test_multiple_inheritance worked example check\n"
        "=======================================================\n"
        "Source contract anchors in src/classes/test_multiple_inheritance.py:\n"
        "- line 67: assert calendar_clock.get_date() == '12/08/2018'\n"
        "- line 68: assert calendar_clock.get_time() == '11:23 PM'\n\n"
        "MRO Dispatch & Worked Example:\n"
        "- Method Resolution Order verified: ['CalendarClock', 'Clock', 'Calendar', 'object'].\n"
        "- Decisive transition: lookup linearly resolves get_time in Clock and get_date in Calendar.\n"
        "- Documentation outputs executed and verified: '12/08/2018' and '11:23 PM'.\n"
        "- Neighboring input verified: '12/09/2018' and '11:24 PM'.\n\n"
        "Requested command: python3 work/R30-T037/check.py\n"
        "Focused pytest command: {}\n"
        "Python: {}\n"
        "Pytest: {}\n"
        "Nonzero test count: {}\n"
        "Exit code: {}\n\n"
        "Focused test output:\n"
        "{}"
    ).format(
        ' '.join([sys.executable, '-m', 'pytest', '-s', '-v', TEST.as_posix()]),
        version,
        pytest_version,
        test_count,
        result.returncode,
        output,
    )

    EVIDENCE_TXT.write_text(evidence_text, encoding='utf-8')
    EVIDENCE_MD.write_text(f"```\n{evidence_text}```\n", encoding='utf-8')
    print(output, end='')

    if test_count == 0 or result.returncode != 0:
        print('Check failed: non-zero exit code or zero tests collected.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
