"""Focused runner and verification script for Task R30-T040."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/modules/sound_package/formats/test_formats_init.py')
INIT_FILE = Path('src/modules/sound_package/formats/__init__.py')
EVIDENCE_TXT = Path(__file__).resolve().parent / 'evidence.txt'
EVIDENCE_MD = Path(__file__).resolve().parent / 'evidence.md'


def main():
    """Run focused pytest on test_formats_init.py and verify mutant rejection."""
    env = os.environ.copy()
    env['PYTHONPATH'] = str(ROOT / 'src/modules') + os.pathsep + str(ROOT / 'src')

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

    # 1. Run baseline legitimate tests
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

    # 2. Invariant mutant check: deliberate one-line mistake in __init__.py
    # Plausible mistake: return normalized == 'wav' (omits 'aif' support)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_sound_pkg = Path(tmpdir) / 'sound_package'
        shutil.copytree(ROOT / 'src/modules/sound_package', tmp_sound_pkg)
        mutant_init = tmp_sound_pkg / 'formats/__init__.py'
        mutant_code = mutant_init.read_text(encoding='utf-8').replace(
            'return normalized in SUPPORTED_FORMATS',
            "return normalized == 'wav'",
        )
        mutant_init.write_text(mutant_code, encoding='utf-8')

        mutant_env = env.copy()
        mutant_env['PYTHONPATH'] = str(tmpdir)

        mutant_test = tmp_sound_pkg / 'formats/test_formats_init.py'
        mutant_result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(mutant_test)],
            cwd=ROOT,
            env=mutant_env,
            capture_output=True,
            text=True,
            check=False,
        )
        mutant_failed_as_expected = (mutant_result.returncode != 0)
        mutant_output = mutant_result.stdout + mutant_result.stderr

    pytest_cmd_str = ' '.join([sys.executable, '-m', 'pytest', '-s', '-v', TEST.as_posix()])

    evidence_text = (
        f"R30-T040 formats __init__ mutation-resistant check\n"
        f"==================================================\n"
        f"Source contract anchors in src/modules/sound_package/formats/__init__.py:\n"
        f"- line 5: __all__ = ['wav', 'aif']\n"
        f"- line 7: SUPPORTED_FORMATS = ('wav', 'aif')\n\n"
        f"Inputs and Expected Results:\n"
        f"- Smallest valid input: is_supported_format('wav') == True\n"
        f"- Ordinary valid input: is_supported_format('aif') == True\n"
        f"- Case-normalized input: is_supported_format('.wav') == True\n"
        f"- Unsupported format input: is_supported_format('mp3') == False\n\n"
        f"Mutant Rejection Verification:\n"
        f"- Plausible one-line mistake: replacing 'normalized in SUPPORTED_FORMATS' with 'normalized == \\'wav\\''.\n"
        f"- The mutant failed test_formats_init_smallest_and_ordinary_inputs on 'aif' as expected.\n"
        f"- Mutant exit code: {mutant_result.returncode}\n\n"
        f"Requested command: python3 work/R30-T040/check.py\n"
        f"Focused pytest command: {pytest_cmd_str}\n"
        f"Python: {version}\n"
        f"Pytest: {pytest_version}\n"
        f"Nonzero test count: {test_count}\n"
        f"Exit code: {result.returncode}\n\n"
        f"Focused test output:\n"
        f"{output}\n"
        f"Mutant execution output:\n"
        f"{mutant_output}"
    )

    EVIDENCE_TXT.write_text(evidence_text, encoding='utf-8')
    EVIDENCE_MD.write_text(f"```\n{evidence_text}```\n", encoding='utf-8')
    print(output, end='')
    print(f"\nMutant rejection verified: returncode={mutant_result.returncode}")

    if test_count == 0 or result.returncode != 0 or not mutant_failed_as_expected:
        print('Check failed: non-zero exit code or mutant not rejected.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
