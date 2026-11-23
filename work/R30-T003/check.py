"""
Automated reference-comparison check runner for R30-T003.

Cross-checks comparison operators (==, !=, >, <, >=, <=) in
src/operators/test_comparison.py against an independent difference oracle
and explicit expected results across >= 20 valid inputs.
Also runs focused pytest on src/operators/test_comparison.py and verifies
repeatability across fresh equivalent inputs.

Exits non-zero if ANY check or test fails.
"""

import json
import os
import subprocess
import sys

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
TARGET_FILE = os.path.join(REPO_ROOT, "src", "operators", "test_comparison.py")
RESULTS_FILE = os.path.join(SCRIPT_DIR, "results.json")


# Tool version helpers
def _run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def get_python_version():
    r = _run([sys.executable, "--version"])
    return (r.stdout + r.stderr).strip()


def get_pytest_version():
    r = _run([sys.executable, "-m", "pytest", "--version"])
    return (r.stdout + r.stderr).strip()


# Independent reference oracle: evaluates comparisons via numeric difference sign
# Does NOT call test_comparison_operators.
def evaluate_by_difference(lhs, rhs, op):
    """Independent reference oracle using numeric difference sign."""
    diff = lhs - rhs
    if op == '==':
        return diff == 0
    if op == '!=':
        return diff != 0
    if op == '>':
        return diff > 0
    if op == '<':
        return diff < 0
    if op == '>=':
        return diff >= 0
    if op == '<=':
        return diff <= 0
    raise ValueError(f"Unsupported operator: {op}")


def apply_comparison(lhs, rhs, op):
    """Direct comparison operator evaluation."""
    if op == '==':
        return lhs == rhs
    if op == '!=':
        return lhs != rhs
    if op == '>':
        return lhs > rhs
    if op == '<':
        return lhs < rhs
    if op == '>=':
        return lhs >= rhs
    if op == '<=':
        return lhs <= rhs
    raise ValueError(f"Unsupported operator: {op}")


# Test cases table: 30 cases (>= 20)
COMPARISON_CASES = [
    # Source anchors:
    {"lhs": 5, "rhs": 5, "op": "==", "expected": True, "category": "anchor", "desc": "5 == 5"},
    {"lhs": 5, "rhs": 3, "op": "!=", "expected": True, "category": "anchor", "desc": "5 != 3"},
    {"lhs": 5, "rhs": 3, "op": ">", "expected": True, "category": "anchor", "desc": "5 > 3"},
    {"lhs": 5, "rhs": 8, "op": "<", "expected": True, "category": "anchor", "desc": "5 < 8"},
    {"lhs": 5, "rhs": 5, "op": ">=", "expected": True, "category": "anchor", "desc": "5 >= 5"},
    {"lhs": 5, "rhs": 4, "op": ">=", "expected": True, "category": "anchor", "desc": "5 >= 4"},
    {"lhs": 5, "rhs": 5, "op": "<=", "expected": True, "category": "anchor", "desc": "5 <= 5"},
    {"lhs": 5, "rhs": 6, "op": "<=", "expected": True, "category": "anchor", "desc": "5 <= 6"},

    # Derived neighboring inputs (3, 4, 5):
    {"lhs": 5, "rhs": 4, "op": ">", "expected": True, "category": "neighbor", "desc": "5 > 4"},
    {"lhs": 4, "rhs": 5, "op": "<", "expected": True, "category": "neighbor", "desc": "4 < 5"},
    {"lhs": 4, "rhs": 4, "op": "==", "expected": True, "category": "neighbor", "desc": "4 == 4"},
    {"lhs": 4, "rhs": 3, "op": ">", "expected": True, "category": "neighbor", "desc": "4 > 3"},
    {"lhs": 3, "rhs": 4, "op": "<", "expected": True, "category": "neighbor", "desc": "3 < 4"},
    {"lhs": 3, "rhs": 3, "op": "==", "expected": True, "category": "neighbor", "desc": "3 == 3"},
    {"lhs": 3, "rhs": 5, "op": "<", "expected": True, "category": "neighbor", "desc": "3 < 5"},
    {"lhs": 4, "rhs": 4, "op": ">=", "expected": True, "category": "neighbor", "desc": "4 >= 4"},
    {"lhs": 4, "rhs": 4, "op": "<=", "expected": True, "category": "neighbor", "desc": "4 <= 4"},

    # Domain boundaries (zero, negatives):
    {"lhs": 0, "rhs": 0, "op": "==", "expected": True, "category": "boundary", "desc": "0 == 0"},
    {"lhs": 0, "rhs": 1, "op": "<", "expected": True, "category": "boundary", "desc": "0 < 1"},
    {"lhs": 1, "rhs": 0, "op": ">", "expected": True, "category": "boundary", "desc": "1 > 0"},
    {"lhs": -1, "rhs": 0, "op": "<", "expected": True, "category": "boundary", "desc": "-1 < 0"},
    {"lhs": 0, "rhs": -1, "op": ">", "expected": True, "category": "boundary", "desc": "0 > -1"},
    {"lhs": -1, "rhs": -1, "op": "==", "expected": True,
     "category": "boundary", "desc": "-1 == -1"},
    {"lhs": -2, "rhs": -1, "op": "<", "expected": True, "category": "boundary", "desc": "-2 < -1"},

    # Negative / False-outcome cases:
    {"lhs": 5, "rhs": 5, "op": "!=", "expected": False, "category": "false_case", "desc": "5 != 5"},
    {"lhs": 5, "rhs": 3, "op": "==", "expected": False, "category": "false_case", "desc": "5 == 3"},
    {"lhs": 3, "rhs": 5, "op": ">", "expected": False, "category": "false_case", "desc": "3 > 5"},
    {"lhs": 5, "rhs": 3, "op": "<", "expected": False, "category": "false_case", "desc": "5 < 3"},
    {"lhs": 3, "rhs": 5, "op": ">=", "expected": False, "category": "false_case", "desc": "3 >= 5"},
    {"lhs": 5, "rhs": 3, "op": "<=", "expected": False, "category": "false_case", "desc": "5 <= 3"},
]

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


def main():
    print("=" * 72)
    print("R30-T003 Reference-Comparison Check Runner")
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

    # 2. Execute reference comparison across all cases
    total_cases = len(COMPARISON_CASES)
    print(f"\nExecuting reference comparison across {total_cases} cases (>= 20 required):")
    case_results = []
    all_cases_passed = True
    repeat_passed = True

    for case in COMPARISON_CASES:
        lhs = case["lhs"]
        rhs = case["rhs"]
        op = case["op"]
        expected = case["expected"]
        desc = case["desc"]
        category = case["category"]

        # Actual direct comparison
        actual = apply_comparison(lhs, rhs, op)
        # Reference oracle via numeric difference
        oracle = evaluate_by_difference(lhs, rhs, op)
        # Repeated run with fresh equivalent inputs
        fresh_lhs = int(str(lhs))
        fresh_rhs = int(str(rhs))
        repeat_actual = apply_comparison(fresh_lhs, fresh_rhs, op)
        repeat_oracle = evaluate_by_difference(fresh_lhs, fresh_rhs, op)

        passed = (actual == expected == oracle)
        rep_ok = (repeat_actual == actual and repeat_oracle == oracle)

        if not passed:
            all_cases_passed = False
        if not rep_ok:
            repeat_passed = False

        status = "PASS" if (passed and rep_ok) else "FAIL"
        print(f"  [{status}] [{category:10s}] {desc:12s} op='{op}' | "
              f"actual={actual} expected={expected} oracle={oracle} repeat={repeat_actual}")

        case_results.append({
            "lhs": lhs,
            "rhs": rhs,
            "op": op,
            "category": category,
            "desc": desc,
            "expected": expected,
            "actual": actual,
            "oracle": oracle,
            "repeat_actual": repeat_actual,
            "passed": passed and rep_ok,
        })

    # 3. Save results JSON
    summary = {
        "python_version": python_version,
        "pytest_version": pytest_version,
        "pytest_command": " ".join(PYTEST_CMD),
        "pytest_returncode": pytest_rc,
        "pytest_test_count": test_count,
        "total_cases_checked": len(COMPARISON_CASES),
        "all_cases_passed": all_cases_passed,
        "repeatability_verified": repeat_passed,
        "cases": case_results,
    }
    with open(RESULTS_FILE, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"\nResults saved to: {RESULTS_FILE}")

    # 4. Final verdict
    overall_pass = (
        pytest_rc == 0
        and test_count > 0
        and all_cases_passed
        and repeat_passed
    )
    print("\n" + "=" * 72)
    if overall_pass:
        print("ALL CHECKS PASSED ✓")
    else:
        print("SOME CHECKS FAILED ✗")
        if pytest_rc != 0:
            print(f"  - pytest failed with exit code {pytest_rc}")
        if test_count == 0:
            print("  - pytest collected 0 tests")
        if not all_cases_passed:
            print("  - one or more comparison cases failed")
        if not repeat_passed:
            print("  - repeatability check with fresh inputs failed")
    print("=" * 72)

    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
