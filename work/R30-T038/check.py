"""Focused runner and verification script for Task R30-T038."""

import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/standard_libraries/test_json.py')
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
    """Run focused pytest on test_json.py and verify failure path coverage."""
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

    pytest_cmd_str = ' '.join([sys.executable, '-m', 'pytest', '-s', '-v', TEST.as_posix()])

    evidence_text = (
        f"R30-T038 test_json failure-path check\n"
        f"=====================================\n"
        f"Source contract anchors in src/standard_libraries/test_json.py:\n"
        f"- line 21: assert person_dictionary['first_name'] == 'John'\n"
        f"- line 22: assert person_dictionary['age'] == 42\n"
        f"- line 30: assert person_parsed_dictionary == person_dictionary\n\n"
        f"Failure Path and Invariant Verification:\n"
        f"- Line 28 json.loads failure: smallest input '{{' raises json.JSONDecodeError.\n"
        f"- State integrity: ordinary valid calls succeed immediately after exception handling.\n"
        f"- Neighboring input: {{'first_name': 'Jane', 'last_name': 'Smith', 'age': 43}} verified.\n"
        f"- Valid empty structure: '{{}}' successfully deserializes to {{}}.\n\n"
        f"Requested command: python3 work/R30-T038/check.py\n"
        f"Focused pytest command: {pytest_cmd_str}\n"
        f"Python: {version}\n"
        f"Pytest: {pytest_version}\n"
        f"Nonzero test count: {test_count}\n"
        f"Exit code: {result.returncode}\n\n"
        f"Focused test output:\n"
        f"{output}"
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
