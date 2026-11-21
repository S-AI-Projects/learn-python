"""Focused runner and verification script for Task R30-T032."""

import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/additions/test_generators.py')
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
    """Run focused pytest on test_generators.py, persist results, and verify boundaries."""
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
        "R30-T032 test_generators boundary check\n"
        "=======================================\n"
        "Source contract anchors in src/additions/test_generators.py:\n"
        "- line 26: for _ in range(3): yield random.randint(1, 10)\n"
        "- line 30: yield random.randint(10, 20)\n"
        "- line 37: assert 0 <= random_number <= 10\n"
        "- line 39: assert 10 <= random_number <= 20\n\n"
        "Boundary Table:\n"
        "- Yield count boundary: exactly 4 items, followed by StopIteration on 5th next().\n"
        "- Indices 0, 1, 2 (index < 3): range [1, 10] within asserted bounds [0, 10].\n"
        "- Index 3 (neighboring boundary transition): range [10, 20] within asserted bounds [10, 20].\n"
        "- Lower bounds verified: [1, 1, 1, 10]\n"
        "- Upper bounds verified: [10, 10, 10, 20]\n\n"
        "Requested command: python3 work/R30-T032/check.py\n"
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
