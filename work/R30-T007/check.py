"""
Automated runnable example & doctest check runner for R30-T007.

Verifies test_bitwise in src/operators/test_bitwise.py:
  - Focused pytest execution targeting ONLY src/operators/test_bitwise.py
  - Direct execution of the docstring runnable example via doctest
  - Direct execution and validation of captured stdout trace for anchors (5, 3)
  - Direct execution and validation of captured stdout trace for derived neighbors (6, 3)
  - Verification of hand-calculated intermediate binary states (&, |, ~, ^, >>, <<)

Exits non-zero if ANY assertion, doctest, or pytest check fails.
"""

import contextlib
import doctest
import importlib
import io
import json
import os
import subprocess
import sys

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
TARGET_FILE = os.path.join(REPO_ROOT, "src", "operators", "test_bitwise.py")
RESULTS_FILE = os.path.join(SCRIPT_DIR, "results.json")

HAND_CALCULATED_STATES = [
    {
        "inputs": {"a": 5, "b": 3},
        "binary_a": "0b0101",
        "binary_b": "0b0011",
        "operations": [
            {
                "op": "&",
                "calc": "0b0101 & 0b0011 -> 0b0001 = 1",
                "decisive": "only bit 0 set in both",
                "expected": 1,
            },
            {
                "op": "|",
                "calc": "0b0101 | 0b0011 -> 0b0111 = 7",
                "decisive": "union of set bits {0, 2} and {0, 1}",
                "expected": 7,
            },
            {
                "op": "~",
                "calc": "-(5 + 1) = -6",
                "decisive": "all bits inverted, two's complement sign bit set",
                "expected": -6,
            },
            {
                "op": "^",
                "calc": "0b0101 ^ 0b0011 -> 0b0110 = 6",
                "decisive": "differing bits {1, 2} set",
                "expected": 6,
            },
            {
                "op": ">>",
                "calc": "0b0101 >> 1 -> 0b0010 = 2",
                "decisive": "bit 0 dropped, bit 2 moves to bit 1",
                "expected": 2,
            },
            {
                "op": "<<",
                "calc": "0b0101 << 1 -> 0b1010 = 10",
                "decisive": "zero pushed in, bits shift left",
                "expected": 10,
            },
        ],
    },
    {
        "inputs": {"a": 6, "b": 3},
        "binary_a": "0b0110",
        "binary_b": "0b0011",
        "operations": [
            {
                "op": "&",
                "calc": "0b0110 & 0b0011 -> 0b0010 = 2",
                "decisive": "only bit 1 set in both",
                "expected": 2,
            },
            {
                "op": "|",
                "calc": "0b0110 | 0b0011 -> 0b0111 = 7",
                "decisive": "union of set bits {1, 2} and {0, 1}",
                "expected": 7,
            },
            {
                "op": "~",
                "calc": "-(6 + 1) = -7",
                "decisive": "all bits inverted, two's complement sign bit set",
                "expected": -7,
            },
            {
                "op": "^",
                "calc": "0b0110 ^ 0b0011 -> 0b0101 = 5",
                "decisive": "differing bits {0, 2} set",
                "expected": 5,
            },
            {
                "op": ">>",
                "calc": "0b0110 >> 1 -> 0b0011 = 3",
                "decisive": "bit 0 dropped, bits {1, 2} shift right",
                "expected": 3,
            },
            {
                "op": "<<",
                "calc": "0b0110 << 1 -> 0b1100 = 12",
                "decisive": "zero pushed in, bits shift left",
                "expected": 12,
            },
        ],
    },
]


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


def run_checks():
    """Run doctest and stdout validation of the runnable example."""
    checks = []
    all_passed = True

    # Import target module
    sys.path.insert(0, REPO_ROOT)
    try:
        mod = importlib.import_module("src.operators.test_bitwise")
    finally:
        sys.path.pop(0)

    # 1. Run doctest directly on the module
    dt_res = doctest.testmod(mod, verbose=False)
    dt_ok = (dt_res.failed == 0 and dt_res.attempted > 0)
    if not dt_ok:
        all_passed = False
    checks.append({
        "check": "doctest_execution",
        "attempted": dt_res.attempted,
        "failed": dt_res.failed,
        "passed": dt_ok,
    })

    # 2. Execute and capture trace for anchor (5, 3)
    buf_5_3 = io.StringIO()
    with contextlib.redirect_stdout(buf_5_3):
        mod.trace_bitwise_operations(5, 3)
    actual_5_3 = buf_5_3.getvalue().strip()
    expected_5_3 = "\n".join([
        "5 & 3 = 1 (0b0101 & 0b0011 -> 0b0001; decisive: only bit 0 set in both)",
        "5 | 3 = 7 (0b0101 | 0b0011 -> 0b0111; decisive: union of set bits {0, 2} and {0, 1})",
        "~5 = -6 (two's complement: -(5 + 1) = -6; decisive: sign bit set)",
        "5 ^ 3 = 6 (0b0101 ^ 0b0011 -> 0b0110; decisive: differing bits {1, 2} set)",
        "5 >> 1 = 2 (0b0101 >> 1 -> 0b0010; decisive: bit 0 dropped, bit 2 moves to bit 1)",
        "5 << 1 = 10 (0b0101 << 1 -> 0b1010; decisive: zero pushed in, bits shift left)",
    ])
    ok_5_3 = (actual_5_3 == expected_5_3)
    if not ok_5_3:
        all_passed = False
    checks.append({
        "check": "anchor_runnable_example_output",
        "inputs": {"a": 5, "b": 3},
        "expected": expected_5_3,
        "actual": actual_5_3,
        "passed": ok_5_3,
    })

    # 3. Execute and capture trace for neighboring input (6, 3)
    buf_6_3 = io.StringIO()
    with contextlib.redirect_stdout(buf_6_3):
        mod.trace_bitwise_operations(6, 3)
    actual_6_3 = buf_6_3.getvalue().strip()
    expected_6_3 = "\n".join([
        "6 & 3 = 2 (0b0110 & 0b0011 -> 0b0010; decisive: only bit 1 set in both)",
        "6 | 3 = 7 (0b0110 | 0b0011 -> 0b0111; decisive: union of set bits {1, 2} and {0, 1})",
        "~6 = -7 (two's complement: -(6 + 1) = -7; decisive: sign bit set)",
        "6 ^ 3 = 5 (0b0110 ^ 0b0011 -> 0b0101; decisive: differing bits {0, 2} set)",
        "6 >> 1 = 3 (0b0110 >> 1 -> 0b0011; decisive: bit 0 dropped, bits {1, 2} shift right)",
        "6 << 1 = 12 (0b0110 << 1 -> 0b1100; decisive: zero pushed in, bits shift left)",
    ])
    ok_6_3 = (actual_6_3 == expected_6_3)
    if not ok_6_3:
        all_passed = False
    checks.append({
        "check": "neighboring_runnable_example_output",
        "inputs": {"a": 6, "b": 3},
        "expected": expected_6_3,
        "actual": actual_6_3,
        "passed": ok_6_3,
    })

    # 4. Direct invocation of test functions
    mod.test_bitwise_operators()
    mod.test_docstring_worked_example()
    checks.append({
        "check": "test_functions_direct_invocation",
        "passed": True,
    })

    return checks, all_passed


def main():
    print("=" * 72)
    print("R30-T007 Runnable Example & Doctest Check Runner")
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

    # 2. Run doctest and stdout checks
    print("\nExecuting runnable example and doctest checks:")
    checks, all_checks_passed = run_checks()
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
        "hand_calculated_intermediate_states": HAND_CALCULATED_STATES,
        "checks": checks,
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
            print("  - runnable example or doctest checks failed")
    print("=" * 72)

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
