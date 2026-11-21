"""Run focused list tests and prove the boundary regression catches a mutant."""

import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src/data_types/test_lists.py'
TEST_NODE = 'test_list_indexing_neighboring_input'
PYTEST_COMMAND = [
    sys.executable,
    '-m',
    'pytest',
    '-s',
    '-v',
    'src/data_types/test_lists.py',
]
MUTATION_TARGET = 'actual = (squares[0], squares[-1])'
MUTATION_REPLACEMENT = 'actual = (squares[0], squares[-2])'


def run(command, cwd, env):
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_count(output):
    counts = re.findall(
        r'(\d+) (?:passed|failed|error|errors|skipped|xfailed|xpassed)',
        output,
    )
    return sum(int(count) for count in counts)


def main():
    """Run the original test file and a temporary negative-index mutant."""
    env = os.environ.copy()
    original_result = run(PYTEST_COMMAND, ROOT, env)
    original_output = original_result.stdout + original_result.stderr
    original_count = test_count(original_output)

    source = SOURCE.read_text(encoding='utf-8')
    if source.count(MUTATION_TARGET) != 1:
        raise RuntimeError('Expected exactly one mutation target in test file.')

    with tempfile.TemporaryDirectory(prefix='r30-t050-') as temp_dir:
        mutant_path = Path(temp_dir) / 'test_lists_mutant.py'
        mutant_path.write_text(
            source.replace(MUTATION_TARGET, MUTATION_REPLACEMENT),
            encoding='utf-8',
        )
        mutant_command = [
            sys.executable,
            '-m',
            'pytest',
            '-q',
            '-s',
            '{}::{}'.format(mutant_path, TEST_NODE),
        ]
        mutant_result = run(mutant_command, ROOT, env)
        mutant_output = mutant_result.stdout + mutant_result.stderr

    mutant_detected = (
        mutant_result.returncode != 0
        and re.search(r'\b1 failed\b', mutant_output) is not None
        and TEST_NODE in mutant_output
        and 'expected=(1, 36), actual=(1, 25)' in mutant_output
    )

    version = run([sys.executable, '--version'], ROOT, env)
    pytest_version = run(
        [sys.executable, '-m', 'pytest', '--version'],
        ROOT,
        env,
    )
    if version.returncode != 0 or pytest_version.returncode != 0:
        raise RuntimeError('Could not determine Python and pytest versions.')

    result_summary = (
        'Original tests: exit={}, collected nonzero test count={}\n'
        'Mutant: exit={}, detected by the named regression={}\n'
        'Mutant expected/actual observation: expected=(1, 36), actual=(1, 25)\n'
    ).format(
        original_result.returncode,
        original_count,
        mutant_result.returncode,
        mutant_detected,
    )
    evidence = (
        'R30-T050 list indexing mutation-resistance check\n'
        '================================================\n'
        'Source contract: test_list_type in src/data_types/test_lists.py '
        '(line 17) has no arguments and implicitly returns None. It uses '
        'local lists only (including the mutations at lines 43-61) and has '
        'no external I/O; pytest is its only dependency. The five-item '
        'fixture at line 23 is checked as a list at line 25, with index 0 '
        'equal to 1 and index -1 equal to 25 at lines 29-30. The new test '
        'checks the same boundaries on six literal '
        'squares. Independently, the first value is 1 and the final value '
        'is 6**2 = 36, so expected is (1, 36).\n'
        'Fresh-input invariant: two separately constructed equivalent lists '
        'must each yield (1, 36); the test also expects the full observed '
        'sequence [(1, 36), (1, 36)].\n'
        'Mutation: in a temporary copy of the test module, changed only '
        'squares[-1] to squares[-2]. The same named regression must fail '
        'because it observes (1, 25) instead of (1, 36). The repository '
        'source is not mutated.\n\n'
        'Focused pytest command: {}\n'
        'Mutation pytest command: {}\n'
        'Requested command: python3 work/R30-T050/check.py\n'
        'Python: {}\n'
        'Pytest: {}\n'
        'Platform: {}\n'
        '{}\n'
        'Original pytest output:\n{}\n'
        'Mutant pytest output:\n{}\n'
    ).format(
        ' '.join(PYTEST_COMMAND),
        ' '.join(
            [
                sys.executable,
                '-m',
                'pytest',
                '-q',
                '-s',
                '<temporary mutant>::{}'.format(TEST_NODE),
            ]
        ),
        version.stdout.strip(),
        pytest_version.stdout.strip(),
        platform.platform(),
        result_summary,
        original_output.rstrip(),
        mutant_output.rstrip(),
    )
    evidence_path = Path(__file__).resolve().parent / 'evidence.txt'
    evidence_path.write_text(evidence, encoding='utf-8')

    print(original_output, end='')
    print(mutant_output, end='')
    print(result_summary, end='')
    print('Evidence saved to {}'.format(evidence_path))

    if original_count == 0:
        print('Focused pytest run collected no tests.', file=sys.stderr)
        return 1
    if original_result.returncode != 0:
        return original_result.returncode
    if not mutant_detected:
        print('The targeted mutant was not detected as expected.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
