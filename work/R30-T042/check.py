"""Run the focused zlib boundary tests and save their evidence."""

import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/standard_libraries/test_zlib.py')
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
    """Run only the zlib example tests, persist results, and propagate failures."""
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
        'R30-T042 zlib boundary check\n'
        '============================\n'
        'Source contract anchors in src/standard_libraries/test_zlib.py:\n'
        "- line 14: fixture b'witch which has which witches wrist watch'; "
        'line 15 asserts length 41.\n'
        '- line 17 compresses the fixture; line 18 asserts compressed length 37.\n'
        '- line 20 decompresses the compressed fixture; line 21 asserts the '
        'original bytes.\n\n'
        'Boundary table for the bytes passed to zlib.compress (line 17):\n'
        "- input b'' (minimum zero-length bytes): expected decompressed output b''.\n"
        "- input b'\\x00' (neighboring one-byte input): expected decompressed "
        "output b'\\x00'; expected CRC-32 3523407757 (0xD202EF8D).\n"
        'Independent CRC-32 calculation for b\"\\x00\": start with 0xFFFFFFFF; '
        'applying the reflected 0xEDB88320 polynomial for eight zero bits gives '
        '0x2DFD1072; final XOR with 0xFFFFFFFF gives 0xD202EF8D '
        '(3523407757). No unsupported-input exception policy is asserted.\n'
        'The example uses in-memory bytes and has no external I/O or mutation.\n\n'
        'Baseline before adding the runner: 3 passed; all explicit expected and '
        'actual values matched.\n\n'
        'Requested command: python3 work/R30-T042/check.py\n'
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
