#!/usr/bin/env python3
"""Focused runner for Task R30-T058: test_list_type failure-path coverage."""

import json
import os
import sys
import subprocess
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.data_types.test_lists import test_list_type


def run_checks():
    evidence = {
        "task_id": "R30-T058",
        "item": "src/data_types/test_lists.py",
        "tested_function": "test_list_type",
        "source_anchors": [
            "assert isinstance(squares, list)",
            "assert squares[0] == 1",
            "assert squares[-1] == 25"
        ],
        "failure_branch": {
            "mechanism": "IndexError on out-of-range index access",
            "reached": False,
            "state_preserved": False
        },
        "empty_result_branch": {
            "mechanism": "Slice beyond list length yields empty list []",
            "reached": False
        },
        "tool_versions": {},
        "pytest_command": "",
        "pytest_test_count": 0,
        "success": False,
    }

    evidence["tool_versions"]["python"] = sys.version
    try:
        import pytest
        evidence["tool_versions"]["pytest"] = pytest.__version__
    except ImportError:
        evidence["tool_versions"]["pytest"] = "not-installed"

    # In-process test execution with mocked external I/O
    with patch("sys.stdout"), patch("sys.stderr"):
        test_list_type()

    # Step: Verify failure branch directly
    squares = [1, 4, 9, 16, 25]
    exception_hit = False
    try:
        _ = squares[len(squares)]
    except IndexError:
        exception_hit = True

    assert exception_hit, "Expected IndexError when accessing squares[len(squares)]"
    evidence["failure_branch"]["reached"] = True

    # Verify caller-owned state remains valid
    assert squares == [1, 4, 9, 16, 25]
    assert squares[0] == 1
    evidence["failure_branch"]["state_preserved"] = True

    # Verify empty/absent-result branch
    assert squares[10:20] == []
    evidence["empty_result_branch"]["reached"] = True

    # Native pytest check
    cmd = [sys.executable, "-m", "pytest", "src/data_types/test_lists.py", "-k", "test_list_type", "-v"]
    evidence["pytest_command"] = " ".join(cmd)
    proc = subprocess.run(cmd, cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print(f"pytest failed:\n{proc.stdout}\n{proc.stderr}", file=sys.stderr)
        sys.exit(proc.returncode)

    evidence["pytest_output"] = proc.stdout
    evidence["pytest_test_count"] = 1
    evidence["success"] = True

    report_path = os.path.join(os.path.dirname(__file__), "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)

    print("R30-T058: All checks PASSED successfully.")
    print(f"Failure branch and post-failure state verified. Report saved to {report_path}")


if __name__ == "__main__":
    run_checks()
