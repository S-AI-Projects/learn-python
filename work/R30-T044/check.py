"""Run focused docstring invariants and verify their failure signal."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
TEST = Path('src/functions/test_function_documentation_string.py')
SOURCE = ROOT / TEST
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
    """Run focused tests, then confirm a broken temporary copy fails them."""
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
    output = '\n'.join(line.rstrip() for line in output.splitlines()) + '\n'
    counts = [
        int(value)
        for value in re.findall(
            r'(\d+) (?:passed|failed|error|errors|skipped|xfailed|xpassed)',
            output,
        )
    ]
    test_count = sum(counts)

    source = SOURCE.read_text(encoding='utf-8')
    pass_statement = '    pass\n'
    if source.count(pass_statement) != 1:
        raise RuntimeError('Expected exactly one do_nothing pass statement.')
    broken_source = source.replace(
        pass_statement,
        "    return 'broken'\n",
        1,
    )
    with tempfile.TemporaryDirectory(
        prefix='r30-t044-'
    ) as temporary_directory:
        broken_test = Path(temporary_directory) / TEST.name
        broken_test.write_text(broken_source, encoding='utf-8')
        negative_result = subprocess.run(
            [
                sys.executable,
                '-m',
                'pytest',
                '-q',
                str(broken_test),
            ],
            cwd=temporary_directory,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    negative_output = negative_result.stdout + negative_result.stderr
    negative_output = '\n'.join(
        line.rstrip() for line in negative_output.splitlines()
    ) + '\n'
    negative_detected = negative_result.returncode != 0

    evidence = (
        'R30-T044 documentation-string invariant check\n'
        '==============================================\n'
        'Source contract: do_nothing accepts no arguments. Its documented '
        'result is None and it has no side effects. The readable case checks '
        'the return and function attributes separately.\n'
        'The valid input domain is the singleton empty argument tuple (). A '
        'seeded random.Random(44045) selects from this domain for 100 bounded '
        'calls; each call is a fresh invocation with equivalent empty '
        'inputs.\n'
        'Expected property outputs: 100 None results and unchanged function '
        'attributes ({{}}). Actual expected/actual lists and state '
        'observations '
        'are recorded below.\n\n'
        'Baseline before docstring normalization: the existing exact '
        'assertion '
        'failed on Python 3.15.2 for the smallest case, do_nothing() with no '
        'arguments. The expected literal contained indentation while runtime '
        '__doc__ was dedented. The related test now uses inspect.cleandoc so '
        'the documented content is checked consistently.\n\n'
        'Requested command: python3 work/R30-T044/check.py\n'
        'Focused pytest command: {}\n'
        'Python: {}\n'
        'Pytest: {}\n'
        'Nonzero test count: {}\n'
        'Focused test exit code: {}\n'
        'Broken-copy control: replaced do_nothing pass with return '
        '\"broken\"; '
        'expected nonzero pytest status, actual status {} (detected={}).\n\n'
        'Focused test output (includes expected and actual values):\n'
        '{}\n'
        'Broken-copy pytest output:\n'
        '{}'
    ).format(
        ' '.join(
            [sys.executable, '-m', 'pytest', '-s', '-v', TEST.as_posix()]
        ),
        version,
        pytest_version,
        test_count,
        result.returncode,
        negative_result.returncode,
        negative_detected,
        output,
        negative_output,
    )
    EVIDENCE.write_text(evidence, encoding='utf-8')
    print(output, end='')
    print(
        'Broken-copy control expected nonzero status; '
        'actual status {}.'.format(negative_result.returncode)
    )

    if test_count == 0:
        print('Focused pytest run collected no tests.', file=sys.stderr)
        return 1
    if result.returncode != 0:
        return result.returncode
    if not negative_detected:
        print(
            'Broken-copy control did not detect the invariant violation.',
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
