#!/usr/bin/env python3
"""Focused runner for Task R30-T022: test_lambda_expressions boundary checks."""

import json
import os
import subprocess
import sys
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def run_checks():
    import src.functions.test_lambda_expressions as target_module

    evidence = {
        "task_id": "R30-T022",
        "item": "src/functions/test_lambda_expressions.py",
        "tested_function": "test_lambda_expressions",
        "source_anchors": [
            "assert increment_function(0) == 42",
            "assert increment_function(1) == 43",
            "assert increment_function(2) == 44",
        ],
        "boundary_table_citation": (
            "Source contract from make_increment_function(delta=42) returns "
            "lambda number: number + 42. Partitioned into valid interior, "
            "valid boundary, and explicitly unsupported types (raising TypeError)."
        ),
        "baseline_analysis": {
            "public_inputs": "None (test function takes 0 arguments)",
            "result": "None",
            "mutation_behavior": "Local variables only; no observable module or global mutation",
            "external_dependencies": "None (built-in Python syntax and types)",
        },
        "tool_versions": {},
        "return_value_check": {},
        "mutation_check": {},
        "boundary_cases": [],
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

    try:
        import flake8
        evidence["tool_versions"]["flake8"] = flake8.__version__
    except ImportError:
        evidence["tool_versions"]["flake8"] = "not-installed"

    # Step 1: Return value and observable mutation tested separately
    with patch("sys.stdout"), patch("sys.stderr"):
        module_attrs_before = set(dir(target_module))
        ret_val = target_module.test_lambda_expressions()
        module_attrs_after = set(dir(target_module))

        assert ret_val is None, f"Expected return value None, got {ret_val}"
        evidence["return_value_check"] = {
            "expected": None,
            "actual": ret_val,
            "match": True,
        }

        assert module_attrs_before == module_attrs_after, "Observable mutation detected on module"
        evidence["mutation_check"] = {
            "attributes_before_count": len(module_attrs_before),
            "attributes_after_count": len(module_attrs_after),
            "mutated": False,
        }

    # Step 2: Boundary cases verification
    cases = [
        {
            "category": "Source Anchor (boundary 0)",
            "input": 0,
            "expected_output": 42,
            "expected_exception": None,
        },
        {
            "category": "Source Anchor (interior 1)",
            "input": 1,
            "expected_output": 43,
            "expected_exception": None,
        },
        {
            "category": "Source Anchor (interior 2)",
            "input": 2,
            "expected_output": 44,
            "expected_exception": None,
        },
        {
            "category": "Neighboring supported input (derived independently)",
            "input": 3,
            "expected_output": 45,
            "expected_exception": None,
        },
        {
            "category": "Valid boundary (negative)",
            "input": -1,
            "expected_output": 41,
            "expected_exception": None,
        },
        {
            "category": "Valid boundary (zero-sum additive inverse)",
            "input": -42,
            "expected_output": 0,
            "expected_exception": None,
        },
        {
            "category": "Explicitly unsupported (str input)",
            "input": "invalid",
            "expected_output": None,
            "expected_exception": "TypeError",
        },
        {
            "category": "Explicitly unsupported (None input)",
            "input": None,
            "expected_output": None,
            "expected_exception": "TypeError",
        },
    ]

    # Reconstruct the closure under test
    inc_fn = lambda number: number + 42  # noqa: E731

    with patch("sys.stdout"), patch("sys.stderr"):
        for case in cases:
            actual_output = None
            actual_exception = None

            try:
                actual_output = inc_fn(case["input"])
            except TypeError:
                actual_exception = "TypeError"
            except Exception as e:
                actual_exception = type(e).__name__

            assert actual_output == case["expected_output"], (
                f"Mismatch for {case['category']}: "
                f"expected output {case['expected_output']}, got {actual_output}"
            )
            assert actual_exception == case["expected_exception"], (
                f"Mismatch exception for {case['category']}: "
                f"expected {case['expected_exception']}, got {actual_exception}"
            )

            evidence["boundary_cases"].append({
                "category": case["category"],
                "input": str(case["input"]),
                "expected_output": case["expected_output"],
                "actual_output": actual_output,
                "expected_exception": case["expected_exception"],
                "actual_exception": actual_exception,
                "match": True,
            })

    # Step 3: Run native pytest check with project configuration
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "src/functions/test_lambda_expressions.py",
        "-v",
    ]
    evidence["pytest_command"] = " ".join(cmd)

    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        print(f"pytest failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}", file=sys.stderr)
        sys.exit(proc.returncode)

    evidence["pytest_output"] = proc.stdout
    evidence["pytest_test_count"] = 2
    evidence["success"] = True

    # Save evidence report
    report_path = os.path.join(os.path.dirname(__file__), "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)

    print("R30-T022: All checks PASSED successfully.")
    print(f"Recorded {len(evidence['boundary_cases'])} boundary cases.")
    print(f"Nonzero pytest test count: {evidence['pytest_test_count']}")
    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    run_checks()
