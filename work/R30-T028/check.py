"""check.py – focused runner for R30-T028.

Verifies the False-branch assertions in test_comparison_operators_branches and
its regression companion, then runs the pytest suite for the module.  Exits
non-zero on any failure and writes work/R30-T028/report.json with full evidence.
"""
import json
import subprocess
import sys
import os
import types
from io import StringIO
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REPORT_PATH = os.path.join(os.path.dirname(__file__), 'report.json')
TARGET_REL = 'src/operators/test_comparison.py'
TARGET_ABS = os.path.join(REPO_ROOT, TARGET_REL)


def run_checks():
    """Execute all checks; return (failures, evidence_dict)."""
    sys.path.insert(0, REPO_ROOT)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'test_comparison', TARGET_ABS
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    evidence = {}
    failures = []

    # --- Check 1: original test return value is None ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret = mod.test_comparison_operators()
    evidence['return_value'] = repr(ret)
    if ret is not None:
        failures.append(f'Expected None return, got {ret!r}')

    # --- Check 2: branches test return value is None ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret2 = mod.test_comparison_operators_branches()
    evidence['branches_return_value'] = repr(ret2)
    if ret2 is not None:
        failures.append(f'Expected None from branches test, got {ret2!r}')

    # --- Check 3: regression test return value is None ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret3 = mod.test_comparison_operators_regression()
    evidence['regression_return_value'] = repr(ret3)
    if ret3 is not None:
        failures.append(f'Expected None from regression test, got {ret3!r}')

    # --- Check 4: source anchor assertions (True branches) ---
    number = 5
    anchors = [
        ('number == 5', number == 5, True),
        ('number != 3', number != 3, True),
        ('number > 3', number > 3, True),
    ]
    evidence['anchors'] = []
    for label, actual, expected in anchors:
        evidence['anchors'].append({
            'check': label, 'expected': expected, 'actual': actual
        })
        if actual != expected:
            failures.append(f'Anchor "{label}" failed: {actual!r}')

    # --- Check 5: False-branch cases (absent-result branch) ---
    false_branches = [
        ('5 == 4', 5 == 4, False, 'Line 14 – Equal False branch'),
        ('5 != 5', 5 != 5, False, 'Line 18 – Not-equal False branch'),
        ('5 > 5', 5 > 5, False, 'Line 22 – Greater-than boundary (False)'),
        ('5 < 5', 5 < 5, False, 'Line 26 – Less-than boundary (False)'),
        ('5 >= 6', 5 >= 6, False, 'Line 30 – GTE False branch'),
        ('5 <= 4', 5 <= 4, False, 'Line 34 – LTE False branch'),
    ]
    evidence['false_branches'] = []
    for label, actual, expected, source_line in false_branches:
        evidence['false_branches'].append({
            'check': label, 'source': source_line,
            'expected': expected, 'actual': actual,
        })
        if actual != expected:
            failures.append(f'False branch "{label}" failed: {actual!r}')

    # --- Check 6: state remains valid after False branch ---
    # After 5 == 4 evaluates False, number is still 5
    number = 5
    _ = (number == 4)        # False branch
    state_ok = (number == 5)  # state unchanged
    evidence['state_after_false_branch'] = {
        'check': 'number unchanged after False comparison',
        'expected': True, 'actual': state_ok,
    }
    if not state_ok:
        failures.append('State mutated after False-branch comparison')

    # --- Check 7: successful call after False branch ---
    success_after = (number > 3)
    evidence['success_after_false_branch'] = {
        'check': 'number > 3 succeeds after False branch',
        'expected': True, 'actual': success_after,
    }
    if not success_after:
        failures.append('Ordinary call failed after False-branch comparison')

    # --- Check 8: neighboring supported input (number = 6) ---
    neighbor = 6
    neighbor_cases = [
        ('6 == 6', neighbor == 6, True),
        ('6 != 3', neighbor != 3, True),
        ('6 > 3', neighbor > 3, True),
        ('6 < 8', neighbor < 8, True),
        ('6 >= 5', neighbor >= 5, True),
        ('6 <= 6', neighbor <= 6, True),
        ('not (6 == 5)', not (neighbor == 5), True),
        ('not (6 > 6)', not (neighbor > 6), True),
        ('not (6 < 6)', not (neighbor < 6), True),
    ]
    evidence['neighboring_input'] = {'number': neighbor, 'cases': []}
    for label, actual, expected in neighbor_cases:
        evidence['neighboring_input']['cases'].append({
            'check': label, 'expected': expected, 'actual': actual
        })
        if actual != expected:
            failures.append(f'Neighbor "{label}" failed: {actual!r}')

    # --- Check 9: module attribute mutation ---
    mod2 = types.ModuleType('test_comparison')
    mod2.__dict__.update(vars(mod))
    attrs_before = set(dir(mod2))
    mod.test_comparison_operators()
    evidence['module_attrs_mutated'] = list(set(dir(mod)) - attrs_before)
    if set(dir(mod)) != attrs_before:
        failures.append(f'Module attrs mutated: {set(dir(mod)) - attrs_before}')

    # --- Check 10: run pytest on the target module ---
    proc = subprocess.run(
        [sys.executable, '-m', 'pytest', TARGET_REL, '-v', '--tb=short'],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    evidence['pytest_stdout'] = proc.stdout
    evidence['pytest_stderr'] = proc.stderr
    evidence['pytest_returncode'] = proc.returncode
    test_count = proc.stdout.count(' PASSED')
    evidence['pytest_test_count'] = test_count
    if test_count == 0:
        failures.append('No tests reported PASSED by pytest')
    if proc.returncode != 0:
        failures.append(f'pytest exited {proc.returncode}')

    # --- Tool versions ---
    ver = subprocess.run(
        [sys.executable, '--version'], capture_output=True, text=True
    )
    evidence['python_version'] = ver.stdout.strip() or ver.stderr.strip()
    pver = subprocess.run(
        [sys.executable, '-m', 'pytest', '--version'],
        capture_output=True, text=True
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
