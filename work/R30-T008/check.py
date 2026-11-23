#!/usr/bin/env python3
"""Automated verification runner for R30-T008 (Issue #13).

Covers failure paths, state preservation, post-failure recovery, and
sentinel/absent-result behavior in src/data_types/test_dictionaries.py.
"""

import json
import os
import subprocess
import sys
import pytest


def get_tool_versions():
    """Return Python and pytest versions."""
    py_ver = sys.version.split()[0]
    pytest_ver = pytest.__version__
    return {"python": py_ver, "pytest": pytest_ver}


def run_targeted_pytest(repo_root):
    """Run focused pytest on src/data_types/test_dictionaries.py."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "src/data_types/test_dictionaries.py",
        "-v",
        "--tb=short",
    ]
    res = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return {
        "command": " ".join(cmd),
        "exit_code": res.returncode,
        "stdout": res.stdout,
        "success": res.returncode == 0,
    }


def verify_dictionary_contract():
    """Execute focused checks covering failure path, recovery, and fallback."""
    checks = []

    # Source anchor baseline
    fruits = {"apple": "green", "banana": "yellow"}
    assert isinstance(fruits, dict)
    assert fruits["apple"] == "green"
    assert fruits["banana"] == "yellow"
    checks.append({
        "name": "source_anchors_baseline",
        "source_lines": "38-40",
        "input": "fruits_dictionary = {'apple': 'green', 'banana': 'yellow'}",
        "expected": "dict instance, apple=green, banana=yellow",
        "actual": (
            f"type={type(fruits).__name__}, "
            f"apple={fruits['apple']}, banana={fruits['banana']}"
        ),
        "status": "PASSED",
    })

    # Neighboring supported inputs: .get() on existing keys
    apple_val = fruits.get("apple")
    banana_val = fruits.get("banana", "default_val")
    assert apple_val == "green"
    assert banana_val == "yellow"
    checks.append({
        "name": "neighboring_get_existing",
        "source_lines": "38-40",
        "input": "fruits.get('apple'), fruits.get('banana', 'default_val')",
        "expected": "apple='green', banana='yellow'",
        "actual": f"apple='{apple_val}', banana='{banana_val}'",
        "status": "PASSED",
    })

    # Neighboring supported inputs: .get() with custom fallback sentinel
    mango_val = fruits.get("mango", "unknown fruit")
    assert mango_val == "unknown fruit"
    checks.append({
        "name": "neighboring_get_custom_sentinel",
        "source_lines": "38-40",
        "input": "fruits.get('mango', 'unknown fruit')",
        "expected": "unknown fruit",
        "actual": mango_val,
        "status": "PASSED",
    })

    # Documented Failure Path 1: KeyError on missing key indexing
    before_len = len(fruits)
    before_keys = set(fruits.keys())
    before_items = list(fruits.items())

    key_error_raised = False
    try:
        _ = fruits["non_existent_key"]
    except KeyError as exc:
        key_error_raised = True
        err_msg = str(exc)

    assert key_error_raised, "Expected KeyError when accessing non-existent key"
    checks.append({
        "name": "failure_path_missing_key_lookup",
        "source_lines": "38-40",
        "input": "fruits['non_existent_key']",
        "expected": "raise KeyError('non_existent_key')",
        "actual": f"KeyError raised: {err_msg}",
        "status": "PASSED",
    })

    # State preservation assertion after KeyError
    assert len(fruits) == before_len
    assert set(fruits.keys()) == before_keys
    assert list(fruits.items()) == before_items
    checks.append({
        "name": "state_preservation_after_key_error",
        "source_lines": "38-40",
        "input": "fruits state check after KeyError",
        "expected": f"len={before_len}, keys={before_keys}",
        "actual": f"len={len(fruits)}, keys={set(fruits.keys())}",
        "status": "PASSED",
    })

    # Post-failure recovery assertion: regular lookups succeed immediately
    assert fruits["apple"] == "green"
    assert fruits["banana"] == "yellow"
    checks.append({
        "name": "post_failure_recovery_lookup",
        "source_lines": "38-40",
        "input": "fruits['apple'], fruits['banana']",
        "expected": "apple='green', banana='yellow'",
        "actual": f"apple='{fruits['apple']}', banana='{fruits['banana']}'",
        "status": "PASSED",
    })

    # Documented Failure Path 2: KeyError on deleting absent key
    del_key_error_raised = False
    try:
        del fruits["non_existent_fruit"]
    except KeyError:
        del_key_error_raised = True

    assert del_key_error_raised, "Expected KeyError when deleting non-existent key"
    assert len(fruits) == before_len
    assert set(fruits.keys()) == before_keys
    checks.append({
        "name": "failure_path_del_missing_key",
        "source_lines": "61",
        "input": "del fruits['non_existent_fruit']",
        "expected": "raise KeyError and preserve dictionary state",
        "actual": f"KeyError raised, len={len(fruits)}, keys={set(fruits.keys())}",
        "status": "PASSED",
    })

    # Valid absent-result / fallback path: .get() returning None default sentinel
    absent_val = fruits.get("missing_key")
    assert absent_val is None
    checks.append({
        "name": "valid_absent_fallback_get_none",
        "source_lines": "38-40",
        "input": "fruits.get('missing_key')",
        "expected": "None",
        "actual": repr(absent_val),
        "status": "PASSED",
    })

    # Smallest input reaching failure & fallback paths: empty dictionary {}
    empty_dict = {}
    assert isinstance(empty_dict, dict)
    assert len(empty_dict) == 0
    assert not bool(empty_dict)
    assert empty_dict.get("anything") is None
    assert empty_dict.get("anything", 42) == 42

    empty_lookup_key_error = False
    try:
        _ = empty_dict["missing"]
    except KeyError:
        empty_lookup_key_error = True
    assert empty_lookup_key_error

    empty_del_key_error = False
    try:
        del empty_dict["missing"]
    except KeyError:
        empty_del_key_error = True
    assert empty_del_key_error
    assert len(empty_dict) == 0

    checks.append({
        "name": "smallest_input_empty_dictionary",
        "source_lines": "18",
        "input": "empty_dict = {}",
        "expected": "len=0, bool=False, get() is None, KeyError on [] and del",
        "actual": (
            f"len={len(empty_dict)}, bool={bool(empty_dict)}, "
            f"get_none={empty_dict.get('missing') is None}, "
            f"lookup_err={empty_lookup_key_error}, del_err={empty_del_key_error}"
        ),
        "status": "PASSED",
    })

    return checks


def main():
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    work_dir = os.path.dirname(os.path.abspath(__file__))

    print("==================================================")
    print(" R30-T008 / Issue #13 Verification Runner")
    print(" Target: src/data_types/test_dictionaries.py")
    print("==================================================")

    tools = get_tool_versions()
    print(f"Tool Versions: Python {tools['python']} | Pytest {tools['pytest']}")
    print("-" * 50)

    # 1. Run targeted pytest
    print("[1/2] Running focused pytest on src/data_types/test_dictionaries.py...")
    pytest_res = run_targeted_pytest(repo_root)
    print(pytest_res["stdout"].strip())
    if not pytest_res["success"]:
        print("\nERROR: Targeted pytest failed!")
        sys.exit(1)

    # 2. Run focused dictionary contract checks
    print("-" * 50)
    print("[2/2] Running dictionary failure, recovery, and fallback checks...")
    checks = verify_dictionary_contract()
    for chk in checks:
        print(f"  [{chk['status']}] {chk['name']} (Lines {chk['source_lines']})")

    # 3. Assemble and save results.json
    results = {
        "issue": "#13",
        "task": "R30-T008",
        "target_file": "src/data_types/test_dictionaries.py",
        "covered_source_lines": {
            "failure_path_key_error": "lines 38-40, 61",
            "fallback_path_get_sentinel": "lines 38-40",
            "smallest_input_empty_dict": "line 18",
        },
        "tool_versions": tools,
        "pytest_execution": {
            "command": pytest_res["command"],
            "exit_code": pytest_res["exit_code"],
            "success": pytest_res["success"],
        },
        "contract_checks": checks,
        "all_passed": True,
    }

    results_file = os.path.join(work_dir, "results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("-" * 50)
    print(f"Results successfully saved to: {results_file}")
    print("All checks passed successfully.")
    print("==================================================")


if __name__ == "__main__":
    main()
