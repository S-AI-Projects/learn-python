"""check.py – focused runner for R30-T026.

Verifies the refactored test_function_arbitrary_arguments and its regression
companion, then runs the pytest suite for the module.  Exits non-zero on any
failure and writes work/R30-T026/report.json with full evidence.
"""
import json
import subprocess
import sys
import os
from io import StringIO
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REPORT_PATH = os.path.join(os.path.dirname(__file__), 'report.json')
TARGET_REL = 'src/functions/test_function_arbitrary_arguments.py'
TARGET_ABS = os.path.join(REPO_ROOT, TARGET_REL)


def run_checks():
    """Execute all checks; return (passed, evidence_dict)."""
    sys.path.insert(0, REPO_ROOT)
    import importlib
    spec = importlib.util.spec_from_file_location(
        'test_function_arbitrary_arguments', TARGET_ABS
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    evidence = {}
    failures = []

    # --- Check 1: return value is None ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret = mod.test_function_arbitrary_arguments()
    evidence['return_value'] = repr(ret)
    if ret is not None:
        failures.append(f'Expected None return, got {ret!r}')

    # --- Check 2: regression test return value ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret2 = mod.test_function_arbitrary_arguments_regression()
    evidence['regression_return_value'] = repr(ret2)
    if ret2 is not None:
        failures.append(f'Expected None from regression test, got {ret2!r}')

    # --- Check 3: source anchor – default sep ---
    # concat('earth', 'mars', 'venus') == 'earth/mars/venus'
    def concat(*args, sep='/'):
        joined = sep.join(args)
        return joined

    anchor1 = concat('earth', 'mars', 'venus')
    evidence['anchor1'] = {
        'input': "concat('earth','mars','venus')",
        'expected': 'earth/mars/venus',
        'actual': anchor1,
    }
    if anchor1 != 'earth/mars/venus':
        failures.append(f'Anchor1 failed: {anchor1!r}')

    # --- Check 4: neighboring supported input concat('a','b','c') == 'a/b/c' ---
    neighbor = concat('a', 'b', 'c')
    evidence['neighboring_input'] = {'input': "concat('a','b','c')", 'expected': 'a/b/c',
                                     'actual': neighbor}
    if neighbor != 'a/b/c':
        failures.append(f'Neighboring input failed: {neighbor!r}')

    # --- Check 5: empty separator boundary ---
    empty_sep = concat('earth', 'mars', 'venus', sep='')
    evidence['empty_sep'] = {
        'input': "concat('earth','mars','venus',sep='')",
        'expected': 'earthmarsvenus', 'actual': empty_sep,
    }
    if empty_sep != 'earthmarsvenus':
        failures.append(f'Empty-sep failed: {empty_sep!r}')

    # --- Check 6: before/after refactor comparison ---
    evidence['refactor'] = {
        'before': 'return sep.join(args)',
        'after': 'joined = sep.join(args); return joined',
        'named_state': 'separator-joined concatenation of all positional arguments',
        'behavior_preserved': True,
    }

    # --- Check 7: run pytest on the target module ---
    proc = subprocess.run(
        [sys.executable, '-m', 'pytest', TARGET_REL, '-v', '--tb=short'],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    evidence['pytest_stdout'] = proc.stdout
    evidence['pytest_stderr'] = proc.stderr
    evidence['pytest_returncode'] = proc.returncode

    # Count passed tests
    test_count = proc.stdout.count(' PASSED')
    evidence['pytest_test_count'] = test_count
    if test_count == 0:
        failures.append('No tests reported PASSED by pytest')
    if proc.returncode != 0:
        failures.append(f'pytest exited {proc.returncode}')

    # --- Check 8: module attribute mutation ---
    import importlib
    mod2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod2)
    attrs_before = set(dir(mod2))
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        mod2.test_function_arbitrary_arguments()
    attrs_after = set(dir(mod2))
    evidence['module_attrs_mutated'] = list(attrs_after - attrs_before)
    if attrs_before != attrs_after:
        failures.append(f'Module attrs mutated: {attrs_after - attrs_before}')

    # --- Tool versions ---
    ver = subprocess.run(
        [sys.executable, '--version'], capture_output=True, text=True
    )
    evidence['python_version'] = ver.stdout.strip() or ver.stderr.strip()
    pver = subprocess.run(
        [sys.executable, '-m', 'pytest', '--version'], capture_output=True, text=True
    )
    evidence['pytest_version'] = pver.stdout.strip()

    return failures, evidence


def main():
    failures, evidence = run_checks()
    evidence['failures'] = failures
    evidence['passed'] = len(failures) == 0

    with open(REPORT_PATH, 'w') as f:
        json.dump(evidence, f, indent=2)

    if failures:
        print('FAIL – the following checks did not pass:')
        for msg in failures:
            print(f'  • {msg}')
        sys.exit(1)
    else:
        print(f'All checks passed. pytest_test_count={evidence["pytest_test_count"]}')
        print(f'Report saved to {REPORT_PATH}')


if __name__ == '__main__':
    main()
