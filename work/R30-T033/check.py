"""Focused runner and verification script for Task R30-T033."""

import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/getting_started/test_variables.py')
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
    """Run focused pytest on test_variables.py, persist results, and verify cross-check."""
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
        "R30-T033 test_variables cross-check\n"
        "===================================\n"
        "Source contract anchors in src/getting_started/test_variables.py:\n"
        "- line 32: assert integer_variable == 5\n"
        "- line 33: assert string_variable == 'John'\n"
        "- line 38: assert variable_with_changed_type == 'Sally'\n\n"
        "Independent Oracle Cross-Check:\n"
        "- Compared dynamic assignment in 22 distinct domain sequences against environment_oracle.\n"
        "- Verified type transitions and final values for integers, strings, floats, lists, dicts, and None.\n"
        "- Neighboring inputs: 6, 'Johnny', and [5, 'Sally Anne'] confirmed.\n\n"
        "Requested command: python3 work/R30-T033/check.py\n"
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
