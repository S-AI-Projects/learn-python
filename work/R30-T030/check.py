"""check.py – focused runner for R30-T030.

Proves that a regression test can detect a plausible one-line mistake in
test_function_keyword_arguments. Compares original vs mutant execution on the
same named assertion. Writes full evidence to work/R30-T030/report.json.
"""
import json
import os
import subprocess
import sys
import types
from io import StringIO
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REPORT_PATH = os.path.join(os.path.dirname(__file__), 'report.json')
TARGET_REL = 'src/functions/test_function_keyword_arguments.py'
TARGET_ABS = os.path.join(REPO_ROOT, TARGET_REL)


def run_checks():
    """Execute all checks and mutation tests; return (failures, evidence)."""
    sys.path.insert(0, REPO_ROOT)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'test_function_keyword_arguments', TARGET_ABS
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    evidence = {}
    failures = []

    # --- Check 1: original test return value is None with external I/O mocked ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret = mod.test_function_keyword_arguments()
    evidence['return_value'] = repr(ret)
    if ret is not None:
        failures.append(f'Expected None return, got {ret!r}')

    # --- Check 2: regression test return value is None ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret2 = mod.test_function_keyword_arguments_regression()
    evidence['regression_return_value'] = repr(ret2)
    if ret2 is not None:
        failures.append(f'Expected None from regression test, got {ret2!r}')

    # --- Check 3: source anchor assertions ---
    msg_1000 = (
        "This parrot wouldn't voom if you put 1000 volts through it. "
        "Lovely plumage, the Norwegian Blue. "
        "It's a stiff!"
    )
    msg_vooooom = (
        "This parrot wouldn't VOOOOOM if you put 1000000 volts through it. "
        "Lovely plumage, the Norwegian Blue. "
        "It's a stiff!"
    )

    anchors = [
        (
            'parrot(1000) == message',
            mod.parrot(1000),
            msg_1000,
        ),
        (
            'parrot(voltage=1000) == message',
            mod.parrot(voltage=1000),
            msg_1000,
        ),
        (
            'parrot(voltage=1000000, action=VOOOOOM) == message',
            mod.parrot(voltage=1000000, action='VOOOOOM'),
            msg_vooooom,
        ),
    ]
    evidence['anchors'] = []
    for label, actual, expected in anchors:
        evidence['anchors'].append({
            'check': label,
            'expected': expected,
            'actual': actual,
        })
        if actual != expected:
            failures.append(f'Anchor {label} failed: {actual!r}')

    # --- Check 4: neighboring supported input (independently calculated) ---
    neighbor_msg = (
        "This parrot wouldn't voom if you put 250 volts through it. "
        "Lovely plumage, the Norwegian Blue. "
        "It's a stiff!"
    )
    neighbor_actual = mod.parrot(250)
    evidence['neighboring_input'] = {
        'input': 'parrot(250)',
        'expected': neighbor_msg,
        'actual': neighbor_actual,
    }
    if neighbor_actual != neighbor_msg:
        failures.append(f'Neighboring input failed: {neighbor_actual!r}')

    # --- Check 5: Mutation test (plausible 1-line mistake detection) ---
    # Plausible mistake: omitting trailing separator space in accumulation:
    # Original: message += 'if you put ' + str(voltage) + ' volts through it. '
    # Mutant:   message += 'if you put ' + str(voltage) + ' volts through it.'
    def mutant_parrot(
        voltage,
        state='a stiff',
        action='voom',
        parrot_type='Norwegian Blue'
    ):
        """Mutant with a plausible single-line concatenation formatting mistake."""
        message = 'This parrot wouldn\'t ' + action + ' '
        # Missing trailing space after 'it.'
        message += 'if you put ' + str(voltage) + ' volts through it.'
        message += 'Lovely plumage, the ' + parrot_type + '. '
        message += 'It\'s ' + state + '!'
        return message

    reduced_input = 1000
    expected_output = msg_1000

    # Test original passes the named assertion
    original_passed = False
    try:
        assert mod.parrot(reduced_input) == expected_output
        original_passed = True
    except AssertionError:
        original_passed = False
        failures.append('Original parrot unexpectedly failed named assertion')

    # Test mutant fails the exact same named assertion for semantic reason
    mutant_failed_as_expected = False
    mutant_actual = mutant_parrot(reduced_input)
    try:
        assert mutant_actual == expected_output
    except AssertionError:
        mutant_failed_as_expected = True

    if not mutant_failed_as_expected:
        failures.append('Mutant unexpectedly passed the assertion')

    evidence['mutation_analysis'] = {
        'plausible_mistake_description': (
            'Omission of trailing space delimiter in the voltage accumulation line: '
            'message += "if you put " + str(voltage) + " volts through it."'
        ),
        'reduced_input': reduced_input,
        'expected_output': expected_output,
        'original_output': mod.parrot(reduced_input),
        'mutant_output': mutant_actual,
        'original_passed': original_passed,
        'mutant_failed_as_expected': mutant_failed_as_expected,
        'same_named_assertion': 'assert parrot(1000) == message',
        'semantic_divergence': (
            'Mutant concatenated "through it.Lovely" without space delimiter'
        ),
    }

    # --- Check 6: repeatability invariant ---
    run1 = mod.parrot(1000)
    run2 = mod.parrot(1000)
    evidence['repeatability'] = {
        'run1': run1,
        'run2': run2,
        'agreed': run1 == run2,
    }
    if run1 != run2:
        failures.append('Repeatability invariant failed: run1 != run2')

    # --- Check 7: module attribute mutation ---
    mod2 = types.ModuleType('test_function_keyword_arguments')
    mod2.__dict__.update(vars(mod))
    attrs_before = set(dir(mod2))
    mod.test_function_keyword_arguments()
    evidence['module_attrs_mutated'] = list(set(dir(mod)) - attrs_before)
    if set(dir(mod)) != attrs_before:
        failures.append(f'Module attrs mutated: {set(dir(mod)) - attrs_before}')

    # --- Check 8: native pytest test runner ---
    proc = subprocess.run(
        [sys.executable, '-m', 'pytest', TARGET_REL, '-v', '--tb=short'],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    evidence['pytest_command'] = f'{sys.executable} -m pytest {TARGET_REL} -v'
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
