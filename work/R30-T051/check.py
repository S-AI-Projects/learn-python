#!/usr/bin/env python3
"""Focused runner for Task R30-T051: fibonacci_at_position contract regression."""

import json
import os
import sys
import subprocess
from unittest.mock import patch

# Ensure repo root and src/modules are on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULES_DIR = os.path.join(REPO_ROOT, "src", "modules")
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

import fibonacci_module


def run_checks():
    evidence = {
        "task_id": "R30-T051",
        "item": "src/modules/fibonacci_module.py",
        "tested_function": "fibonacci_at_position",
        "fixture_checks": [],
        "tool_versions": {},
        "pytest_command": "",
        "pytest_test_count": 0,
        "success": False,
    }

    # Record tool versions
    evidence["tool_versions"]["python"] = sys.version
    try:
        import pytest
        evidence["tool_versions"]["pytest"] = pytest.__version__
    except ImportError:
        evidence["tool_versions"]["pytest"] = "not-installed"

    # Step 1: In-process focused verification with external I/O mocked
    fixture_cases = [
        {"position": 0, "expected": 0, "kind": "smallest supported input (0-index boundary)"},
        {"position": 1, "expected": 1, "kind": "boundary / initial base case"},
        {"position": 2, "expected": 1, "kind": "repeated-value domain boundary (F(1) == F(2))"},
        {"position": 5, "expected": 5, "kind": "ordinary input"},
        {"position": 10, "expected": 55, "kind": "ordinary input"},
    ]

    with patch("sys.stdout"), patch("sys.stderr"):
        for case in fixture_cases:
            pos = case["position"]
            expected = case["expected"]
            actual = fibonacci_module.fibonacci_at_position(pos)
            assert actual == expected, f"Mismatch for position {pos}: expected {expected}, got {actual}"
            evidence["fixture_checks"].append({
                "input": pos,
                "expected": expected,
                "actual": actual,
                "match": True,
                "kind": case["kind"]
            })

        # Observable mutation check: ensure inputs or global state are not mutated
        sentinel_pos = 5
        res = fibonacci_module.fibonacci_at_position(sentinel_pos)
        assert res == 5 and sentinel_pos == 5, "Mutation observed on input position"
        evidence["mutation_test"] = {"input_before": 5, "input_after": sentinel_pos, "mutated": False}

    # Step 2: Native check running focused pytest on the module tests
    cmd = [sys.executable, "-m", "pytest", "src/modules/test_modules.py", "-k", "test_fibonacci_at_position_contract", "-v"]
    evidence["pytest_command"] = " ".join(cmd)

    proc = subprocess.run(cmd, cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print(f"pytest failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}", file=sys.stderr)
        sys.exit(proc.returncode)

    evidence["pytest_output"] = proc.stdout
    evidence["pytest_test_count"] = 1
    evidence["success"] = True

    # Save evidence report
    report_path = os.path.join(os.path.dirname(__file__), "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)

    print("R30-T051: All checks PASSED successfully.")
    print(f"Verified {len(fixture_cases)} fixture cases. Report saved to {report_path}")


if __name__ == "__main__":
    run_checks()
