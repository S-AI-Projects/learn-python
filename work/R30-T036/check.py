"""Focused runner and verification script for Task R30-T036."""

import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/modules/test_packages.py')
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
    """Run focused pytest on test_packages.py, persist results, and verify refactored contract."""
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
        "R30-T036 test_packages refactor check\n"
        "=====================================\n"
        "Source contract anchors in src/modules/test_packages.py:\n"
        "- line 29: >>> import sys\n"
        "- line 30: >>> sys.path\n"
        "- line 59: assert sound_package.effects.echo.echo_function() == 'Do echo effect'\n\n"
        "Refactoring and Contract Verification:\n"
        "- Extracted get_echo_effect_results() to decouple import pathway execution from assertion.\n"
        "- Preserved exact return values ('Do echo effect') for fully-qualified, submodule, and direct imports.\n"
        "- Tested neighboring effect submodule: sound_package.effects.reverse.reverse_function() == 'Do reverse effect'.\n"
        "- Verified sys.path search path availability.\n\n"
        "Requested command: python3 work/R30-T036/check.py\n"
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
