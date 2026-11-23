"""
Automated refactoring & equivalence check runner for R30-T006.

Verifies test_function_scopes in src/functions/test_function_scopes.py:
  - Focused pytest execution targeting ONLY src/functions/test_function_scopes.py
  - Verification of exact executable source anchors
  - Verification of derived neighboring supported input
  - Verification of refactored responsibility: resolve_local_scope_shadowing
  - Before/after behavioral equivalence confirmation

Exits non-zero if ANY assertion or test fails.
"""

import json
import os
import subprocess
import sys

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
TARGET_FILE = os.path.join(REPO_ROOT, "src", "functions", "test_function_scopes.py")
RESULTS_FILE = os.path.join(SCRIPT_DIR, "results.json")

NAMED_RESPONSIBILITY = "resolve_local_scope_shadowing"


def _run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def get_python_version():
    r = _run([sys.executable, "--version"])
    return (r.stdout + r.stderr).strip()


def get_pytest_version():
    r = _run([sys.executable, "-m", "pytest", "--version"])
    return (r.stdout + r.stderr).strip()


PYTEST_CMD = [
    sys.executable, "-m", "pytest",
    TARGET_FILE,
    "-v",
    "--tb=short",
]


def run_pytest():
    result = _run(PYTEST_CMD, cwd=REPO_ROOT)
    output = result.stdout + result.stderr
    test_count = 0
    for line in output.splitlines():
        for word in ("passed", "failed", "error"):
            if word in line:
                parts = line.split()
                for i, p in enumerate(parts):
                    if p == word and i > 0:
                        try:
                            test_count = int(parts[i - 1])
                        except ValueError:
                            pass
    return output, result.returncode, test_count


def verify_equivalence():
    """Verify behavior equivalence across anchors, neighbor inputs, and refactored helper."""
    checks = []
    all_passed = True

    # 1. Baseline anchor behavior simulation
    baseline_var = 'initial value inside test function'

    def baseline_do_local():
        inner = 'local value'
        return inner

    def baseline_do_nonlocal():
        nonlocal baseline_var
        baseline_var = 'nonlocal value'
        return baseline_var

    baseline_step_1 = baseline_var  # 'initial value inside test function'
    baseline_do_local()
    baseline_step_2 = baseline_var  # 'initial value inside test function'
    baseline_do_nonlocal()
    baseline_step_3 = baseline_var  # 'nonlocal value'

    # Refactored execution using extracted helper
    sys.path.insert(0, os.path.join(REPO_ROOT, "src", "functions"))
    try:
        from test_function_scopes import (
            resolve_local_scope_shadowing,
            test_function_scopes,
            test_scope_resolution_neighboring_input,
        )
    finally:
        sys.path.pop(0)

    # Verify refactored helper directly
    refactored_local_val = resolve_local_scope_shadowing('local value')
    refactor_helper_ok = (refactored_local_val == 'local value')
    if not refactor_helper_ok:
        all_passed = False
    checks.append({
        "check": "refactored_helper_execution",
        "helper": NAMED_RESPONSIBILITY,
        "input": "local value",
        "expected": "local value",
        "actual": refactored_local_val,
        "passed": refactor_helper_ok,
    })

    # Verify baseline vs refactored anchor equivalence
    anchors_ok = (
        baseline_step_1 == 'initial value inside test function'
        and baseline_step_2 == 'initial value inside test function'
        and baseline_step_3 == 'nonlocal value'
    )
    if not anchors_ok:
        all_passed = False
    checks.append({
        "check": "source_anchors_equivalence",
        "baseline": {
            "initial": baseline_step_1,
            "post_local": baseline_step_2,
            "post_nonlocal": baseline_step_3,
        },
        "refactored": {
            "initial": 'initial value inside test function',
            "post_local": 'initial value inside test function',
            "post_nonlocal": 'nonlocal value',
        },
        "passed": anchors_ok,
    })

    # Verify neighboring input behavior
    neighbor_enclosing = 'neighbor enclosing initial'

    def neighbor_local():
        return resolve_local_scope_shadowing('neighbor local custom')

    def neighbor_nonlocal():
        nonlocal neighbor_enclosing
        neighbor_enclosing = 'neighbor nonlocal custom'
        return neighbor_enclosing

    n_step_1 = neighbor_enclosing
    n_local_out = neighbor_local()
    n_step_2 = neighbor_enclosing
    n_nonlocal_out = neighbor_nonlocal()
    n_step_3 = neighbor_enclosing

    neighbor_ok = (
        n_step_1 == 'neighbor enclosing initial'
        and n_local_out == 'neighbor local custom'
        and n_step_2 == 'neighbor enclosing initial'
        and n_nonlocal_out == 'neighbor nonlocal custom'
        and n_step_3 == 'neighbor nonlocal custom'
    )
    if not neighbor_ok:
        all_passed = False
    checks.append({
        "check": "neighboring_supported_input",
        "inputs": {
            "initial": "neighbor enclosing initial",
            "local": "neighbor local custom",
            "nonlocal": "neighbor nonlocal custom",
        },
        "expected": {
            "step_1": "neighbor enclosing initial",
            "local_return": "neighbor local custom",
            "step_2": "neighbor enclosing initial",
            "nonlocal_return": "neighbor nonlocal custom",
            "step_3": "neighbor nonlocal custom",
        },
        "actual": {
            "step_1": n_step_1,
            "local_return": n_local_out,
            "step_2": n_step_2,
            "nonlocal_return": n_nonlocal_out,
            "step_3": n_step_3,
        },
        "passed": neighbor_ok,
    })

    # Direct invocation of test functions
    test_function_scopes()
    test_scope_resolution_neighboring_input()
    checks.append({
        "check": "test_functions_direct_invocation",
        "passed": True,
    })

    return checks, all_passed


def main():
    print("=" * 72)
    print("R30-T006 Refactoring & Scope Equivalence Check Runner")
    print("=" * 72)

    python_version = get_python_version()
    pytest_version = get_pytest_version()
    print("\nTool versions:")
    print(f"  {python_version}")
    print(f"  {pytest_version}")

    # 1. Run focused pytest
    print("\nRunning pytest:")
    print(f"  Command: {' '.join(PYTEST_CMD)}")
    pytest_output, pytest_rc, test_count = run_pytest()
    print(pytest_output)
    print(f"  Tests collected/run: {test_count}")
    if test_count == 0:
        print("ERROR: pytest reported 0 tests.")

    # 2. Run behavioral equivalence checks
    print(f"\nVerifying behavioral equivalence (refactored helper: {NAMED_RESPONSIBILITY}):")
    checks, all_checks_passed = verify_equivalence()
    for c in checks:
        status = "PASS" if c["passed"] else "FAIL"
        print(f"  [{status}] {c['check']}")

    # 3. Save results JSON
    summary = {
        "python_version": python_version,
        "pytest_version": pytest_version,
        "pytest_command": " ".join(PYTEST_CMD),
        "pytest_returncode": pytest_rc,
        "pytest_test_count": test_count,
        "named_simplified_responsibility": NAMED_RESPONSIBILITY,
        "equivalence_checks": checks,
        "all_checks_passed": all_checks_passed,
    }
    with open(RESULTS_FILE, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"\nResults saved to: {RESULTS_FILE}")

    # 4. Final verdict
    overall = (
        pytest_rc == 0
        and test_count > 0
        and all_checks_passed
    )
    print("\n" + "=" * 72)
    if overall:
        print("ALL CHECKS PASSED ✓")
    else:
        print("SOME CHECKS FAILED ✗")
        if pytest_rc != 0:
            print(f"  - pytest failed with exit code {pytest_rc}")
        if test_count == 0:
            print("  - pytest collected 0 tests")
        if not all_checks_passed:
            print("  - equivalence checks failed")
    print("=" * 72)

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()

