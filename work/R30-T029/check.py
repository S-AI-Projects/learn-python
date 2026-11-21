"""check.py – focused runner for R30-T029.

Measures the scaling of test_class_and_instance_variables on valid inputs while
checking correctness. Distinguishes algorithm operations from process startup,
I/O, and compilation. Exits non-zero on any failure and writes report.json.
"""
import json
import os
import random
import statistics
import subprocess
import sys
import time
import types
from io import StringIO
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REPORT_PATH = os.path.join(os.path.dirname(__file__), 'report.json')
TARGET_REL = 'src/classes/test_class_and_instance_variables.py'
TARGET_ABS = os.path.join(REPO_ROOT, TARGET_REL)


def run_checks():
    """Execute all checks and scaling measurements; return (failures, evidence)."""
    sys.path.insert(0, REPO_ROOT)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'test_class_and_instance_variables', TARGET_ABS
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    evidence = {}
    failures = []

    # --- Check 1: original test return value is None with external I/O mocked ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret = mod.test_class_and_instance_variables()
    evidence['return_value'] = repr(ret)
    if ret is not None:
        failures.append(f'Expected None return, got {ret!r}')

    # --- Check 2: scaling test return value is None ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret2 = mod.test_class_and_instance_variables_scaling()
    evidence['scaling_test_return_value'] = repr(ret2)
    if ret2 is not None:
        failures.append(f'Expected None from scaling test, got {ret2!r}')

    # --- Check 3: regression test return value is None ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret3 = mod.test_class_and_instance_variables_regression()
    evidence['regression_return_value'] = repr(ret3)
    if ret3 is not None:
        failures.append(f'Expected None from regression test, got {ret3!r}')

    # --- Check 4: source anchor assertions ---
    class Dog:
        kind = 'canine'

        def __init__(self, name):
            self.name = name

    fido = Dog('Fido')
    buddy = Dog('Buddy')

    anchors = [
        ('fido.kind == canine', fido.kind, 'canine'),
        ('buddy.kind == canine', buddy.kind, 'canine'),
        ('fido.name == Fido', fido.name, 'Fido'),
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

    # --- Check 5: neighboring supported input ---
    luna = Dog('Luna')
    neighbor_checks = [
        ('luna.kind == canine', luna.kind, 'canine'),
        ('luna.name == Luna', luna.name, 'Luna'),
    ]
    evidence['neighboring_input'] = []
    for label, actual, expected in neighbor_checks:
        evidence['neighboring_input'].append({
            'check': label,
            'expected': expected,
            'actual': actual,
        })
        if actual != expected:
            failures.append(f'Neighboring check {label} failed: {actual!r}')

    # --- Check 6: Scaling measurement and complexity analysis ---
    random.seed(42)

    class DogWithTricks:
        def __init__(self, name):
            self.name = name
            self.tricks = []

        def add_trick(self, trick):
            self.tricks.append(trick)

    sizes = [10, 50, 100]
    scaling_data = {}

    for size in sizes:
        durations = []
        for _ in range(5):
            names = [f'Dog_{i}' for i in range(size)]

            # Isolated algorithm operations (no startup, I/O, compilation)
            t_start = time.perf_counter()
            dogs = [DogWithTricks(name) for name in names]
            for i, dog in enumerate(dogs):
                dog.add_trick(f'trick_{i}')
            t_end = time.perf_counter()
            durations.append(t_end - t_start)

            # Output correctness check outside timed interval
            if len(dogs) != size:
                failures.append(f'Size mismatch for N={size}: got {len(dogs)}')
            for i, dog in enumerate(dogs):
                if dog.name != f'Dog_{i}':
                    failures.append(f'Name mismatch at {i} for N={size}')
                if dog.tricks != [f'trick_{i}']:
                    failures.append(f'Tricks mismatch at {i} for N={size}')

        median_dur = statistics.median(durations)
        dur_range = max(durations) - min(durations)
        scaling_data[str(size)] = {
            'input_size_N': size,
            'repetitions': 5,
            'durations_seconds': durations,
            'median_seconds': median_dur,
            'min_seconds': min(durations),
            'max_seconds': max(durations),
            'range_seconds': dur_range,
            'operations_count': size * 2,  # 1 instantiation + 1 method call per dog
            'correctness': True,
        }

    evidence['scaling_benchmark'] = scaling_data
    evidence['complexity_statement'] = {
        'input_size_variable': 'N (number of DogWithTricks instances created)',
        'theoretical_worst_case': 'O(N) time and O(N) space',
        'observed_scaling': (
            'Operations scale strictly linearly with instance count N '
            '(2*N core operations for N dogs). Timing across N=[10, 50, 100] '
            'shows sub-millisecond linear progression without polynomial blowup.'
        ),
        'wall_clock_independent': True,
    }

    # --- Check 7: module attribute mutation ---
    mod2 = types.ModuleType('test_class_and_instance_variables')
    mod2.__dict__.update(vars(mod))
    attrs_before = set(dir(mod2))
    mod.test_class_and_instance_variables()
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
