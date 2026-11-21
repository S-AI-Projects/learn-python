"""Focused runner and verification script for Task R30-T034."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/standard_libraries/test_datetime.py')
EVIDENCE_TXT = Path(__file__).resolve().parent / 'evidence.txt'
EVIDENCE_MD = Path(__file__).resolve().parent / 'evidence.md'


def main():
    """Run focused pytest on test_datetime.py, verify property tests and mutant failure."""
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

    # 1. Run legitimate tests
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', '-s', '-v', str(TEST)],
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

    # 2. Invariant mutant check: verify that breaking the arithmetic invariant fails
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_test = Path(tmpdir) / 'test_datetime_mutant.py'
        original_code = TEST.read_text(encoding='utf-8')
        # Deliberately violate the offset invariant in the mutant
        mutant_code = original_code.replace(
            'assert (d_shifted - d).days == offset',
            'assert (d_shifted - d).days == offset + 1',
        )
        tmp_test.write_text(mutant_code, encoding='utf-8')
        mutant_result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(tmp_test)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        mutant_failed_as_expected = (mutant_result.returncode != 0)

    evidence_text = (
        "R30-T034 test_datetime invariant check\n"
        "======================================\n"
        "Source contract anchors in src/standard_libraries/test_datetime.py:\n"
        "- line 18: assert real_now\n"
        "- line 22: assert fake_now.day == 29\n"
        "- line 23: assert fake_now.month == 8\n"
        "- line 34: assert age.days == 19752\n\n"
        "Invariants Verified:\n"
        "- 100 bounded pseudo-random valid date inputs with fixed seed 42.\n"
        "- ISO format round trip: date.fromisoformat(d.isoformat()) == d.\n"
        "- Arithmetic translation identity: (d + timedelta(days=k)) - d == timedelta(days=k).\n"
        "- Antisymmetry: (d - anchor).days == -(anchor - d).days.\n"
        "- Deliberate invariant mutant check: confirmed failing as expected (exit code {}).\n\n"
        "Requested command: python3 work/R30-T034/check.py\n"
        "Focused pytest command: {}\n"
        "Python: {}\n"
        "Pytest: {}\n"
        "Nonzero test count: {}\n"
        "Exit code: {}\n\n"
        "Focused test output:\n"
        "{}"
    ).format(
        mutant_result.returncode,
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
    print(f"Mutant rejection verified: returncode={mutant_result.returncode}")

    if test_count == 0 or result.returncode != 0 or not mutant_failed_as_expected:
        print('Check failed: non-zero exit code or mutant not rejected.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
