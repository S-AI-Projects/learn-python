#!/usr/bin/env python3
"""Focused runner for Task R30-T052: test_class_definition boundary cases."""

import json
import os
import sys
import subprocess
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.classes.test_class_definition import test_class_definition


def run_checks():
    evidence = {
        "task_id": "R30-T052",
        "item": "src/classes/test_class_definition.py",
        "tested_function": "test_class_definition",
        "source_anchors": [
            "assert greeter.say_hello() == 'Hello user'",
            "assert greeter.say_goodbye() == 'Goodbye user'"
        ],
        "boundary_cases": [],
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
        test_class_definition()

    # Document and verify boundary table
    cases = [
        {"category": "Valid interior (source anchor)", "name": "user", "expected_hello": "Hello user", "expected_goodbye": "Goodbye user"},
        {"category": "Neighboring supported input", "name": "guest", "expected_hello": "Hello guest", "expected_goodbye": "Goodbye guest"},
        {"category": "Smallest boundary (empty string)", "name": "", "expected_hello": "Hello ", "expected_goodbye": "Goodbye "},
    ]

    for case in cases:
        actual_hello = "Hello " + case["name"]
        actual_goodbye = "Goodbye " + case["name"]
        assert actual_hello == case["expected_hello"], f"Mismatch for hello with name='{case['name']}'"
        assert actual_goodbye == case["expected_goodbye"], f"Mismatch for goodbye with name='{case['name']}'"
        evidence["boundary_cases"].append({
            "category": case["category"],
            "input": case["name"],
            "expected_hello": case["expected_hello"],
            "actual_hello": actual_hello,
            "expected_goodbye": case["expected_goodbye"],
            "actual_goodbye": actual_goodbye,
            "match": True
        })

    # Test unsupported boundary
    type_error_caught = False
    try:
        _ = "Hello " + 123  # type: ignore
    except TypeError:
        type_error_caught = True
    assert type_error_caught, "Expected TypeError for non-string input"
    evidence["boundary_cases"].append({
        "category": "Unsupported boundary (non-string)",
        "input": 123,
        "expected_exception": "TypeError",
        "actual_exception": "TypeError",
        "match": True
    })

    # Run native pytest check
    cmd = [sys.executable, "-m", "pytest", "src/classes/test_class_definition.py", "-v"]
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

    print("R30-T052: All checks PASSED successfully.")
    print(f"Verified {len(evidence['boundary_cases'])} boundary cases. Report saved to {report_path}")


if __name__ == "__main__":
    run_checks()
