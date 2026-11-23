"""
Automated boundary-analysis check runner for R30-T002.

Verifies the input/output contract and boundary partition for
  parrot(voltage, state='a stiff', action='voom', parrot_type='Norwegian Blue')
in src/functions/test_function_keyword_arguments.py.

Exits non-zero if ANY assertion, pytest run, or expected-exception check fails.
"""

import json
import subprocess
import sys
import os

# ---------------------------------------------------------------------------
# Paths — resolved relative to this file so the script runs from any cwd
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
TARGET_FILE = os.path.join(
    REPO_ROOT, "src", "functions", "test_function_keyword_arguments.py"
)
RESULTS_FILE = os.path.join(SCRIPT_DIR, "results.json")

# ---------------------------------------------------------------------------
# The function under test — mirrored inline for direct verification
# ---------------------------------------------------------------------------


def parrot(voltage, state='a stiff', action='voom', parrot_type='Norwegian Blue'):
    """Mirror of parrot() from src for standalone inline verification."""
    message = "This parrot wouldn't " + action + ' '
    message += 'if you put ' + str(voltage) + ' volts through it. '
    message += 'Lovely plumage, the ' + parrot_type + '. '
    message += "It's " + state + '!'
    return message


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
# Boundary table (documentation record)
# ---------------------------------------------------------------------------

BOUNDARY_TABLE = [
    # (partition, label, expected_kind)
    ("valid interior",  "parrot(1000) — 1 positional [ANCHOR]",                      "str"),
    ("valid boundary",  "parrot(voltage=1000) — 1 keyword [ANCHOR]",                  "str"),
    ("valid interior",  "parrot(voltage=1000000, action='VOOOOOM') [ANCHOR]",         "str"),
    ("valid interior",  "parrot(action='VOOOOOM', voltage=1000000) order-free",       "str"),
    ("valid interior",  "parrot(1000000, 'bereft of life', 'jump') 3 positional",     "str"),
    ("valid interior",  "parrot(1000, state='pushing up the daisies') pos+kw",        "str"),
    ("valid boundary",  "parrot(0) — voltage boundary (neighboring 0)",               "str"),
    ("valid boundary",
     "parrot(voltage=0, state='dead', action='run', parrot_type='Macaw') all kwargs", "str"),
    ("unsupported",     "parrot() — missing required voltage",                         "TypeError"),
    ("unsupported",     "parrot(110, voltage=220) — duplicate keyword arg",            "TypeError"),
    ("unsupported",     "parrot(actor='John Cleese') — unknown keyword arg",           "TypeError"),
    ("unsupported",     "function_with_one_argument(0, number=0) — dup in 1-arg fn",  "TypeError"),
]

# ---------------------------------------------------------------------------
# Pre-calculated expected strings
# ---------------------------------------------------------------------------

MSG_1000 = (
    "This parrot wouldn't voom if you put 1000 volts through it. "
    "Lovely plumage, the Norwegian Blue. "
    "It's a stiff!"
)
MSG_1000000_VOOOOOM = (
    "This parrot wouldn't VOOOOOM if you put 1000000 volts through it. "
    "Lovely plumage, the Norwegian Blue. "
    "It's a stiff!"
)
MSG_1000000_JUMP = (
    "This parrot wouldn't jump if you put 1000000 volts through it. "
    "Lovely plumage, the Norwegian Blue. "
    "It's bereft of life!"
)
MSG_1000_DAISIES = (
    "This parrot wouldn't voom if you put 1000 volts through it. "
    "Lovely plumage, the Norwegian Blue. "
    "It's pushing up the daisies!"
)
MSG_0 = (
    "This parrot wouldn't voom if you put 0 volts through it. "
    "Lovely plumage, the Norwegian Blue. "
    "It's a stiff!"
)
MSG_ALL_KWARGS = (
    "This parrot wouldn't run if you put 0 volts through it. "
    "Lovely plumage, the Macaw. "
    "It's dead!"
)

# ---------------------------------------------------------------------------
# Valid-call cases: (partition, label, call_fn, expected_str)
# ---------------------------------------------------------------------------

VALID_CASES = [
    ("valid interior",
     "parrot(1000) [anchor]",
     lambda: parrot(1000),
     MSG_1000),
    ("valid boundary",
     "parrot(voltage=1000) [anchor]",
     lambda: parrot(voltage=1000),
     MSG_1000),
    ("valid interior",
     "parrot(voltage=1000000, action='VOOOOOM') [anchor]",
     lambda: parrot(voltage=1000000, action='VOOOOOM'),
     MSG_1000000_VOOOOOM),
    ("valid interior",
     "parrot(action='VOOOOOM', voltage=1000000) order-free",
     lambda: parrot(action='VOOOOOM', voltage=1000000),
     MSG_1000000_VOOOOOM),
    ("valid interior",
     "parrot(1000000, 'bereft of life', 'jump') 3 positional",
     lambda: parrot(1000000, 'bereft of life', 'jump'),
     MSG_1000000_JUMP),
    ("valid interior",
     "parrot(1000, state='pushing up the daisies')",
     lambda: parrot(1000, state='pushing up the daisies'),
     MSG_1000_DAISIES),
    ("valid boundary",
     "parrot(0) — neighboring voltage boundary",
     lambda: parrot(0),
     MSG_0),
    ("valid boundary",
     "parrot(voltage=0, state='dead', action='run', parrot_type='Macaw') all kwargs",
     lambda: parrot(voltage=0, state='dead', action='run', parrot_type='Macaw'),
     MSG_ALL_KWARGS),
]

# ---------------------------------------------------------------------------
# Unsupported cases (must raise TypeError)
# ---------------------------------------------------------------------------


def _parrot_no_args():
    parrot()  # type: ignore[call-arg]


def _parrot_duplicate():
    parrot(110, voltage=220)  # type: ignore[misc]


def _parrot_unknown_kwarg():
    parrot(actor='John Cleese')  # type: ignore[call-arg]


def _fn_one_arg(number):
    return number


def _dup_one_arg():
    _fn_one_arg(0, number=0)  # type: ignore[misc]


UNSUPPORTED_CASES = [
    ("unsupported",
     "parrot() — missing required voltage",
     _parrot_no_args,
     TypeError),
    ("unsupported",
     "parrot(110, voltage=220) — duplicate keyword arg",
     _parrot_duplicate,
     TypeError),
    ("unsupported",
     "parrot(actor='John Cleese') — unknown keyword arg",
     _parrot_unknown_kwarg,
     TypeError),
    ("unsupported",
     "function_with_one_argument(0, number=0) — dup in 1-arg fn",
     _dup_one_arg,
     TypeError),
]

# ---------------------------------------------------------------------------
# pytest runner
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("=" * 72)
    print("R30-T002 Boundary-Analysis Check Runner")
    print("=" * 72)

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
    print(f"  Tests collected/run: {test_count}")
    if test_count == 0:
        print("ERROR: pytest reported 0 tests — something is wrong.")

    # 2. Valid-call boundary partition checks
    print("\nValid-call boundary partition checks:")
    valid_results = []
    all_valid_passed = True
    for partition, label, call_fn, expected in VALID_CASES:
        try:
            actual = call_fn()
            passed = actual == expected
        except Exception as exc:
            actual = f"UNEXPECTED EXCEPTION: {exc}"
            passed = False
        if not passed:
            all_valid_passed = False
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] [{partition}] {label}")
        if not passed:
            print(f"         expected: {expected!r}")
            print(f"         actual  : {actual!r}")
        valid_results.append({
            "partition": partition,
            "label": label,
            "expected": expected,
            "actual": actual if isinstance(actual, str) else str(actual),
            "passed": passed,
        })

    # 3. Unsupported-boundary exception checks
    print("\nUnsupported-boundary exception checks:")
    unsupported_results = []
    all_unsupported_passed = True
    for partition, label, call_fn, exc_type in UNSUPPORTED_CASES:
        raised_name = None
        try:
            call_fn()
            passed = False
        except exc_type as exc:
            raised_name = type(exc).__name__
            passed = True
        except Exception as exc:
            raised_name = type(exc).__name__
            passed = False
        if not passed:
            all_unsupported_passed = False
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] [{partition}] {label}")
        print(f"         expected: {exc_type.__name__}  "
              f"raised: {raised_name if raised_name else 'NOTHING'}")
        unsupported_results.append({
            "partition": partition,
            "label": label,
            "expected_exception": exc_type.__name__,
            "raised": raised_name,
            "passed": passed,
        })

    # 4. Print boundary table
    print("\nBoundary table summary:")
    col = max(len(row[0]) for row in BOUNDARY_TABLE)
    for partition, label, kind in BOUNDARY_TABLE:
        print(f"  [{partition:<{col}}] {label}")

    # 5. Save results JSON
    summary = {
        "python_version": python_version,
        "pytest_version": pytest_version,
        "pytest_command": " ".join(PYTEST_CMD),
        "pytest_returncode": pytest_rc,
        "pytest_test_count": test_count,
        "valid_cases": valid_results,
        "unsupported_cases": unsupported_results,
        "boundary_table": [
            {"partition": p, "label": l, "kind": k}
            for p, l, k in BOUNDARY_TABLE
        ],
    }
    with open(RESULTS_FILE, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"\nResults saved to: {RESULTS_FILE}")

    # 6. Final verdict
    overall = (
        pytest_rc == 0
        and test_count > 0
        and all_valid_passed
        and all_unsupported_passed
    )
    print("\n" + "=" * 72)
    if overall:
        print("ALL CHECKS PASSED ✓")
    else:
        print("SOME CHECKS FAILED ✗")
        if pytest_rc != 0:
            print(f"  - pytest exited {pytest_rc}")
        if test_count == 0:
            print("  - pytest ran 0 tests")
        if not all_valid_passed:
            print("  - one or more valid-call checks failed")
        if not all_unsupported_passed:
            print("  - one or more unsupported-boundary checks failed")
    print("=" * 72)

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()

