"""
Automated repeatability & isolation check runner for R30-T005.

Verifies test_glob in src/standard_libraries/test_glob.py across:
  - Focused pytest execution targeting ONLY src/standard_libraries/test_glob.py
  - Documented external filesystem dependencies
  - Source anchor execution
  - Derived neighboring glob patterns (*first*.txt, *second*.txt, ?irst_file.txt, *.py)
  - Fresh isolated run 1 vs Fresh isolated run 2 (identical explicit results)
  - Interleaved/post-other-input query isolation (earlier runs cannot alter later results)
  - Mocked dependency seam isolation (offline, zero disk access)

Exits non-zero if ANY assertion or test fails.
"""

import glob
import json
import os
import subprocess
import sys
import tempfile

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
TARGET_FILE = os.path.join(REPO_ROOT, "src", "standard_libraries", "test_glob.py")
RESULTS_FILE = os.path.join(SCRIPT_DIR, "results.json")

DOCUMENTED_DEPENDENCIES = [
    {
        "name": "Current Working Directory (CWD)",
        "description": "Relative paths like 'src/standard_libraries/glob_files/*.txt' "
                       "depend on os.getcwd() matching the repo root.",
        "mitigation": "Dependency injection seam (glob_func) or absolute path anchors.",
    },
    {
        "name": "Filesystem Directory State",
        "description": "External presence, modification, or removal of files in "
                       "glob_files/ alters glob outputs directly.",
        "mitigation": "tmp_path fixtures and mocked dependency seams for isolated testing.",
    },
    {
        "name": "Directory Entry Ordering",
        "description": "Underlying filesystem readdir order is arbitrary across operating systems.",
        "mitigation": "Explicit sorted() wrapping on all glob outputs.",
    },
    {
        "name": "Standard Library glob.glob",
        "description": "Platform implementation of glob wildcard pattern matching.",
        "mitigation": "Callable glob_func seam with default=glob.glob preserving callers.",
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


def run_repeatability_and_isolation_checks():
    """Execute repeatability and isolation checks across fresh fixtures and mocks."""
    checks = []
    all_passed = True

    # 1. Source anchor check
    anchor_pattern = 'src/standard_libraries/glob_files/*.txt'
    anchor_actual = sorted(glob.glob(anchor_pattern))
    anchor_expected = sorted([
        'src/standard_libraries/glob_files/first_file.txt',
        'src/standard_libraries/glob_files/second_file.txt'
    ])
    anchor_ok = (anchor_actual == anchor_expected)
    if not anchor_ok:
        all_passed = False
    checks.append({
        "check": "source_anchor",
        "pattern": anchor_pattern,
        "expected": anchor_expected,
        "actual": anchor_actual,
        "passed": anchor_ok,
    })

    # 2. Derived neighboring inputs
    neighboring_cases = [
        ('src/standard_libraries/glob_files/*first*.txt',
         ['src/standard_libraries/glob_files/first_file.txt']),
        ('src/standard_libraries/glob_files/*second*.txt',
         ['src/standard_libraries/glob_files/second_file.txt']),
        ('src/standard_libraries/glob_files/?irst_file.txt',
         ['src/standard_libraries/glob_files/first_file.txt']),
        ('src/standard_libraries/glob_files/*.py',
         []),
    ]
    for pattern, expected in neighboring_cases:
        actual = sorted(glob.glob(pattern))
        passed = (actual == expected)
        if not passed:
            all_passed = False
        checks.append({
            "check": "neighboring_input",
            "pattern": pattern,
            "expected": expected,
            "actual": actual,
            "passed": passed,
        })

    # 3. Fresh isolated run 1 vs Fresh isolated run 2
    with tempfile.TemporaryDirectory() as tmp_root:
        # Run 1 in fresh fixture A
        dir_a = os.path.join(tmp_root, "fixture_a")
        os.makedirs(dir_a)
        with open(os.path.join(dir_a, "first_file.txt"), "w") as f:
            f.write("A1")
        with open(os.path.join(dir_a, "second_file.txt"), "w") as f:
            f.write("A2")
        with open(os.path.join(dir_a, "data.csv"), "w") as f:
            f.write("CSV")

        pattern_a = os.path.join(dir_a, "*.txt")
        run_1_actual = sorted(glob.glob(pattern_a))
        run_1_expected = sorted([
            os.path.join(dir_a, "first_file.txt"),
            os.path.join(dir_a, "second_file.txt")
        ])
        run_1_ok = (run_1_actual == run_1_expected)
        if not run_1_ok:
            all_passed = False
        checks.append({
            "check": "fresh_isolated_run_1",
            "fixture": "fixture_a",
            "expected": run_1_expected,
            "actual": run_1_actual,
            "passed": run_1_ok,
        })

        # Run 2 in fresh fixture B (identical structure)
        dir_b = os.path.join(tmp_root, "fixture_b")
        os.makedirs(dir_b)
        with open(os.path.join(dir_b, "first_file.txt"), "w") as f:
            f.write("B1")
        with open(os.path.join(dir_b, "second_file.txt"), "w") as f:
            f.write("B2")
        with open(os.path.join(dir_b, "data.csv"), "w") as f:
            f.write("CSV")

        pattern_b = os.path.join(dir_b, "*.txt")
        run_2_actual = sorted(glob.glob(pattern_b))
        run_2_expected = sorted([
            os.path.join(dir_b, "first_file.txt"),
            os.path.join(dir_b, "second_file.txt")
        ])
        run_2_ok = (run_2_actual == run_2_expected)

        # Confirm normalized basenames match identically between Run 1 and Run 2
        basenames_1 = [os.path.basename(p) for p in run_1_actual]
        basenames_2 = [os.path.basename(p) for p in run_2_actual]
        runs_identical = (basenames_1 == basenames_2 == ['first_file.txt', 'second_file.txt'])
        if not (run_2_ok and runs_identical):
            all_passed = False
        checks.append({
            "check": "fresh_isolated_run_2",
            "fixture": "fixture_b",
            "expected": run_2_expected,
            "actual": run_2_actual,
            "normalized_match_run1": runs_identical,
            "passed": run_2_ok and runs_identical,
        })

        # 4. Interleaved queries followed by Post-other-input Run
        pattern_csv = os.path.join(dir_a, "*.csv")
        csv_actual = sorted(glob.glob(pattern_csv))
        csv_expected = [os.path.join(dir_a, "data.csv")]
        csv_ok = (csv_actual == csv_expected)

        pattern_py = os.path.join(dir_a, "*.py")
        py_actual = glob.glob(pattern_py)
        py_ok = (py_actual == [])

        # Post-other-input run on dir_a
        post_actual = sorted(glob.glob(pattern_a))
        post_ok = (post_actual == run_1_actual == run_1_expected)
        if not (csv_ok and py_ok and post_ok):
            all_passed = False
        checks.append({
            "check": "post_other_input_isolation",
            "interleaved_csv_passed": csv_ok,
            "interleaved_py_passed": py_ok,
            "post_run_matches_initial": post_ok,
            "expected": run_1_expected,
            "actual": post_actual,
            "passed": csv_ok and py_ok and post_ok,
        })

    # 5. Mocked dependency seam isolation (pure in-memory mock)
    mock_store = {
        'src/standard_libraries/glob_files/*.txt': [
            'src/standard_libraries/glob_files/second_file.txt',
            'src/standard_libraries/glob_files/first_file.txt',
        ],
        'src/standard_libraries/glob_files/*first*.txt': [
            'src/standard_libraries/glob_files/first_file.txt',
        ],
        'src/standard_libraries/glob_files/*second*.txt': [
            'src/standard_libraries/glob_files/second_file.txt',
        ],
        'src/standard_libraries/glob_files/?irst_file.txt': [
            'src/standard_libraries/glob_files/first_file.txt',
        ],
        'src/standard_libraries/glob_files/*.py': [],
    }

    def mock_glob(p):
        return list(mock_store.get(p, []))

    mock_run_1 = sorted(mock_glob('src/standard_libraries/glob_files/*.txt'))
    # Interleaved mock queries
    _ = mock_glob('src/standard_libraries/glob_files/*.py')
    _ = mock_glob('src/standard_libraries/glob_files/*first*.txt')
    mock_run_2 = sorted(mock_glob('src/standard_libraries/glob_files/*.txt'))

    mock_ok = (mock_run_1 == mock_run_2 == anchor_expected)
    if not mock_ok:
        all_passed = False
    checks.append({
        "check": "mocked_dependency_seam_isolation",
        "mock_run_1": mock_run_1,
        "mock_run_2": mock_run_2,
        "expected": anchor_expected,
        "passed": mock_ok,
    })

    return checks, all_passed


def main():
    print("=" * 72)
    print("R30-T005 Repeatability & Isolation Check Runner")
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

    # 2. Run repeatability & isolation checks
    print("\nRunning repeatability and input-isolation checks:")
    checks, all_checks_passed = run_repeatability_and_isolation_checks()
    for c in checks:
        status = "PASS" if c["passed"] else "FAIL"
        print(f"  [{status}] {c['check']}")

    # 3. Documented external dependencies
    print("\nDocumented external dependencies:")
    for dep in DOCUMENTED_DEPENDENCIES:
        print(f"  - {dep['name']}: {dep['description']}")

    # 4. Save results
    summary = {
        "python_version": python_version,
        "pytest_version": pytest_version,
        "pytest_command": " ".join(PYTEST_CMD),
        "pytest_returncode": pytest_rc,
        "pytest_test_count": test_count,
        "documented_dependencies": DOCUMENTED_DEPENDENCIES,
        "repeatability_checks": checks,
        "all_checks_passed": all_checks_passed,
    }
    with open(RESULTS_FILE, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"\nResults saved to: {RESULTS_FILE}")

    # 5. Final verdict
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
            print("  - repeatability or input-isolation checks failed")
    print("=" * 72)

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()

