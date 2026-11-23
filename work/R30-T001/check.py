"""
Automated check runner for R30-T001.

Runs pytest against src/functions/test_function_default_arguments.py,
verifies every contract case individually, saves a results summary, and
exits non-zero if any assertion or test fails.
"""

import json
import subprocess
import sys
import os

# ---------------------------------------------------------------------------
# Paths – resolve relative to this file so the script works from any cwd
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
TARGET_FILE = os.path.join(REPO_ROOT, "src", "functions", "test_function_default_arguments.py")
RESULTS_FILE = os.path.join(SCRIPT_DIR, "results.json")

# ---------------------------------------------------------------------------
# Tool-version helpers
# ---------------------------------------------------------------------------

def _run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def get_python_version():
    r = _run([sys.executable, "--version"])
    return (r.stdout + r.stderr).strip()


def get_pytest_version():
    r = _run([sys.executable, "-m", "pytest", "--version"])
    return (r.stdout + r.stderr).strip()


# ---------------------------------------------------------------------------
# The function under test, copied inline so we can call it directly
# ---------------------------------------------------------------------------

def power_of(number, power=2):
    """Raises number to specific power (mirrored from source for inline checks)."""
    return number ** power


# ---------------------------------------------------------------------------
# Contract cases
# ---------------------------------------------------------------------------

CASES = [
    # label, args, kwargs, expected
    # --- source anchors ---
    ("anchor: power_of(3) default exponent",   (3,),     {},        9),
    ("anchor: power_of(3, 2) explicit 2",      (3, 2),   {},        9),
    ("anchor: power_of(3, 3)",                 (3, 3),   {},       27),
    # --- (a) ordinary neighbouring input ---
    ("ordinary: power_of(2) default exponent", (2,),     {},        4),
    # --- (b) smallest supported input – base 0 ---
    ("boundary: power_of(0) base=0",           (0,),     {},        0),
    # --- (b) exponent 0 boundary ---
    ("boundary: power_of(3, 0) exponent=0",    (3, 0),   {},        1),
    # --- (c) equal base/exponent ---
    ("boundary: power_of(2, 2) equal b/e",     (2, 2),   {},        4),
]


def run_contract_cases():
    """Run every case directly against the inline power_of; return list of result dicts."""
    results = []
    all_passed = True
    for label, args, kwargs, expected in CASES:
        actual = power_of(*args, **kwargs)
        passed = actual == expected
        if not passed:
            all_passed = False
        results.append({
            "label": label,
            "inputs": {"args": list(args), "kwargs": kwargs},
            "expected": expected,
            "actual": actual,
            "passed": passed,
        })
    return results, all_passed


def run_mutation_check():
    """Verify repeated calls return identical results (no hidden state)."""
    first = power_of(3)
    second = power_of(3)
    passed = first == second == 9
    return {
        "label": "mutation/state: power_of(3) called twice → both 9",
        "inputs": {"args": [3], "kwargs": {}},
        "expected": 9,
        "actual_first_call": first,
        "actual_second_call": second,
        "passed": passed,
    }, passed


# ---------------------------------------------------------------------------
# Pytest runner
# ---------------------------------------------------------------------------

PYTEST_CMD = [
    sys.executable, "-m", "pytest",
    TARGET_FILE,
    "-v",
    "--tb=short",
]


def run_pytest():
    """Run pytest and return (output_str, returncode, test_count)."""
    result = _run(PYTEST_CMD, cwd=REPO_ROOT)
    output = result.stdout + result.stderr

    # Parse test count from summary line e.g. "5 passed in 0.12s"
    test_count = None
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("R30-T001 Automated Check Runner")
    print("=" * 70)

    python_version = get_python_version()
    pytest_version = get_pytest_version()
    print(f"\nTool versions:")
    print(f"  {python_version}")
    print(f"  {pytest_version}")

    # 1. Run pytest
    print(f"\nRunning pytest:")
    print(f"  Command: {' '.join(PYTEST_CMD)}")
    pytest_output, pytest_rc, test_count = run_pytest()
    print(pytest_output)
    if test_count is None:
        test_count = 0
    print(f"  Tests collected/run: {test_count}")
    if test_count == 0:
        print("ERROR: pytest reported 0 tests – something is wrong.")

    # 2. Run inline contract cases
    print("\nContract case verification:")
    contract_results, contract_all_passed = run_contract_cases()
    for r in contract_results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['label']}")
        print(f"         inputs={r['inputs']}  expected={r['expected']}  actual={r['actual']}")

    # 3. Mutation / no-hidden-state check
    print()
    mutation_result, mutation_passed = run_mutation_check()
    status = "PASS" if mutation_result["passed"] else "FAIL"
    print(f"  [{status}] {mutation_result['label']}")
    print(
        f"         first_call={mutation_result['actual_first_call']}  "
        f"second_call={mutation_result['actual_second_call']}  "
        f"expected={mutation_result['expected']}"
    )

    # 4. Save results
    summary = {
        "python_version": python_version,
        "pytest_version": pytest_version,
        "pytest_command": " ".join(PYTEST_CMD),
        "pytest_returncode": pytest_rc,
        "pytest_test_count": test_count,
        "contract_cases": contract_results,
        "mutation_check": mutation_result,
    }
    with open(RESULTS_FILE, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"\nResults saved to: {RESULTS_FILE}")

    # 5. Final verdict
    overall_pass = (
        pytest_rc == 0
        and test_count > 0
        and contract_all_passed
        and mutation_passed
    )
    print("\n" + "=" * 70)
    if overall_pass:
        print("ALL CHECKS PASSED ✓")
    else:
        print("SOME CHECKS FAILED ✗")
        if pytest_rc != 0:
            print(f"  - pytest exited with code {pytest_rc}")
        if test_count == 0:
            print("  - pytest ran 0 tests")
        for r in contract_results:
            if not r["passed"]:
                print(f"  - FAIL: {r['label']}")
        if not mutation_passed:
            print("  - FAIL: mutation/state check")
    print("=" * 70)

    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
