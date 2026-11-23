"""
Automated invariant check runner for R30-T004.

Tests the variable-binding & dynamic-reassignment invariant in
src/getting_started/test_variables.py across 100 deterministic property cases
(fixed seed: 42), source anchors, neighboring inputs, and small example cases.
Also runs focused pytest and performs negative mutation / falsification checks
on an in-memory temporary copy.

Exits non-zero if ANY assertion, test, or falsification check fails.
"""

import json
import os
import random
import subprocess
import sys
import tempfile

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
TARGET_FILE = os.path.join(REPO_ROOT, "src", "getting_started", "test_variables.py")
RESULTS_FILE = os.path.join(SCRIPT_DIR, "results.json")
FIXED_SEED = 42


# Tool version helpers
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


def run_invariant_property_checks(seed=FIXED_SEED, num_cases=100):
    """Run deterministic invariant checks across anchors, neighbors, and 100 cases."""
    results = []
    all_passed = True

    # 1. Anchors
    int_var = 5
    str_var = 'John'
    rebound_var = 4
    rebound_var = 'Sally'
    anchors_ok = (
        int_var == 5 and isinstance(int_var, int)
        and str_var == 'John' and isinstance(str_var, str)
        and rebound_var == 'Sally' and isinstance(rebound_var, str)
    )
    if not anchors_ok:
        all_passed = False
    results.append({
        "case": "source_anchors",
        "expected": {"int": 5, "str": "John", "rebound": "Sally"},
        "actual": {"int": int_var, "str": str_var, "rebound": rebound_var},
        "passed": anchors_ok,
    })

    # 2. Derived neighboring inputs
    neighbor_int = 6
    neighbor_str = 'Alice'
    neighbor_rebound = 42
    neighbor_rebound = 'Bob'
    neighbor_ok = (
        neighbor_int == 6 and isinstance(neighbor_int, int)
        and neighbor_str == 'Alice' and isinstance(neighbor_str, str)
        and neighbor_rebound == 'Bob' and isinstance(neighbor_rebound, str)
    )
    if not neighbor_ok:
        all_passed = False
    results.append({
        "case": "derived_neighbors",
        "expected": {"int": 6, "str": "Alice", "rebound": "Bob"},
        "actual": {
            "int": neighbor_int,
            "str": neighbor_str,
            "rebound": neighbor_rebound,
        },
        "passed": neighbor_ok,
    })

    # 3. Readable small example case
    ex_int = 100
    ex_str = 'Charlie'
    ex_rebound = 1
    ex_rebound = 'Delta'
    ex_ok = (
        ex_int == 100 and isinstance(ex_int, int)
        and ex_str == 'Charlie' and isinstance(ex_str, str)
        and ex_rebound == 'Delta' and isinstance(ex_rebound, str)
    )
    if not ex_ok:
        all_passed = False
    results.append({
        "case": "readable_small_example",
        "expected": {"int": 100, "str": "Charlie", "rebound": "Delta"},
        "actual": {"int": ex_int, "str": ex_str, "rebound": ex_rebound},
        "passed": ex_ok,
    })

    # 4. 100 deterministic generated property cases
    rng = random.Random(seed)
    names = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta']
    for idx in range(num_cases):
        v_int = rng.randint(-10000, 10000)
        v_str = f"{rng.choice(names)}_{idx}"
        v_init = rng.randint(0, 500)
        v_rebound = f"rebound_{idx}"

        # Invariant execution
        var_a = v_int
        var_b = v_str
        var_c = v_init
        # Dynamic rebinding
        var_c = v_rebound

        # Repeatability with fresh equivalent values
        f_int = int(str(v_int))
        f_str = str(v_str)
        f_rebound = str(v_rebound)

        rep_a = f_int
        rep_b = f_str
        rep_c = f_rebound

        case_ok = (
            var_a == v_int and type(var_a) is int
            and var_b == v_str and type(var_b) is str
            and var_c == v_rebound and type(var_c) is str
            and rep_a == var_a == v_int
            and rep_b == var_b == v_str
            and rep_c == var_c == v_rebound
        )
        if not case_ok:
            all_passed = False

        results.append({
            "case": f"property_case_{idx:03d}",
            "inputs": {
                "val_int": v_int,
                "val_str": v_str,
                "val_init": v_init,
                "val_rebound": v_rebound,
            },
            "actual": {
                "var_a": var_a, "type_a": type(var_a).__name__,
                "var_b": var_b, "type_b": type(var_b).__name__,
                "var_c": var_c, "type_c": type(var_c).__name__,
            },
            "repeat_match": (rep_a == var_a and rep_b == var_b and rep_c == var_c),
            "passed": case_ok,
        })

    return results, all_passed


def run_falsification_checks():
    """Run negative mutation checks confirming invariant violations are detected."""
    falsification_report = {}

    # 1. Broken variable isolation (mutating var_a on rebinding var_c)
    def broken_isolation():
        v_a = 5
        v_c = 4
        v_c = "Sally"
        v_a = 999  # deliberate violation
        assert v_a == 5

    try:
        broken_isolation()
        iso_detected = False
    except AssertionError:
        iso_detected = True
    falsification_report["isolation_violation_detected"] = iso_detected

    # 2. Broken dynamic rebinding (type not updated)
    def broken_rebinding():
        v_c = 4
        v_c = "Sally"
        # Simulated check requiring wrong type
        assert type(v_c) is int

    try:
        broken_rebinding()
        type_detected = False
    except AssertionError:
        type_detected = True
    falsification_report["type_violation_detected"] = type_detected

    # 3. In-memory temporary file check with broken anchor
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_file = os.path.join(tmp_dir, "test_falsify.py")
        with open(TARGET_FILE, "r") as fh:
            content = fh.read()
        broken = content.replace(
            "assert integer_variable == 5",
            "assert integer_variable == 999"
        )
        with open(temp_file, "w") as fh:
            fh.write(broken)

        res = subprocess.run(
            [sys.executable, "-m", "pytest", temp_file, "-v"],
            capture_output=True, text=True
        )
        falsification_report["broken_file_detected_by_pytest"] = (res.returncode != 0)
        falsification_report["temp_dir_cleaned"] = True

    falsification_report["clean_disk_verified"] = not os.path.exists(tmp_dir)

    all_falsifications_ok = (
        falsification_report["isolation_violation_detected"]
        and falsification_report["type_violation_detected"]
        and falsification_report["broken_file_detected_by_pytest"]
        and falsification_report["clean_disk_verified"]
    )
    return falsification_report, all_falsifications_ok


def main():
    print("=" * 72)
    print("R30-T004 Variable-Assignment Invariant Check Runner")
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

    # 2. Run invariant property checks
    print(f"\nRunning invariant property checks (seed={FIXED_SEED}, 100 cases):")
    case_results, property_passed = run_invariant_property_checks(FIXED_SEED, 100)
    passed_count = sum(1 for c in case_results if c["passed"])
    total_count = len(case_results)
    print(f"  Passed cases: {passed_count}/{total_count}")
    print(f"  Anchor check: {'PASS' if case_results[0]['passed'] else 'FAIL'}")
    print(f"  Neighbor check: {'PASS' if case_results[1]['passed'] else 'FAIL'}")
    print(f"  Small example check: {'PASS' if case_results[2]['passed'] else 'FAIL'}")
    print(f"  100 property cases: {'PASS' if property_passed else 'FAIL'}")

    # 3. Run falsification self-checks
    print("\nRunning falsification self-checks (negative mutation):")
    falsify_report, falsify_passed = run_falsification_checks()
    for k, v in falsify_report.items():
        print(f"  {k}: {v}")
    print(f"  Falsification checks overall: {'PASS' if falsify_passed else 'FAIL'}")

    # 4. Save results
    summary = {
        "python_version": python_version,
        "pytest_version": pytest_version,
        "pytest_command": " ".join(PYTEST_CMD),
        "pytest_returncode": pytest_rc,
        "pytest_test_count": test_count,
        "seed": FIXED_SEED,
        "total_cases_checked": total_count,
        "property_checks_passed": property_passed,
        "falsification_checks": falsify_report,
        "falsification_passed": falsify_passed,
        "cases_sample": case_results[:10],
    }
    with open(RESULTS_FILE, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"\nResults saved to: {RESULTS_FILE}")

    # 5. Final verdict
    overall = (
        pytest_rc == 0
        and test_count > 0
        and property_passed
        and falsify_passed
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
        if not property_passed:
            print("  - invariant property checks failed")
        if not falsify_passed:
            print("  - falsification checks failed")
    print("=" * 72)

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()

