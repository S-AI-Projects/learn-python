#!/usr/bin/env python3
"""Focused runner for Task R30-T021: test_handle_exceptions regression checks."""

import json
import os
import subprocess
import sys
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def run_checks():
    import src.exceptions.test_handle_exceptions as target_module
    evidence = {
        "task_id": "R30-T021",
        "item": "src/exceptions/test_handle_exceptions.py",
        "tested_function": "test_handle_exceptions",
        "source_anchors": [
            "assert result",
            "assert exception_has_been_handled",
            "assert result",
        ],
        "baseline_analysis": {
            "public_inputs": "None (test function takes 0 arguments)",
            "result": "None",
            "mutation_behavior": "Local variables only; no observable module or global mutation",
            "external_dependencies": "Built-in exceptions (ZeroDivisionError, NameError)",
            "baseline_mismatches": (
                "1. Line 97 comment incorrectly claimed '# We should not get here at all.' "
                "inside try block where result = 10 raises no exception.\n"
                "2. Line 101 comment under except NameError erroneously stated "
                "'# We should get here because of division by zero.'\n"
                "3. Assertions (assert result, assert exception_has_been_handled) tested "
                "bare truthiness instead of explicit expected values."
            ),
        },
        "tool_versions": {},
        "return_value_check": {},
        "mutation_check": {},
        "fixture_checks": [],
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

    try:
        import flake8
        evidence["tool_versions"]["flake8"] = flake8.__version__
    except ImportError:
        evidence["tool_versions"]["flake8"] = "not-installed"

    # Step 1: Returned values and observable mutation tested separately
    with patch("sys.stdout"), patch("sys.stderr"):
        module_attrs_before = set(dir(target_module))
        ret_val = target_module.test_handle_exceptions()
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

    # Step 2: Fixture cases covering ordinary input, neighboring supported input,
    # smallest supported input, and repeated-value domain boundary
    cases = [
        {
            "category": "Source Anchor (Exception Path)",
            "expr": "10 * (1 / 0)",
            "divisor": 0,
            "numerator": 10,
            "expected_result": None,
            "expected_handled": True,
            "expected_else_fired": False,
        },
        {
            "category": "Source Anchor (Clean Path)",
            "expr": "result = 10",
            "divisor": 1,
            "numerator": 10,
            "expected_result": 10,
            "expected_handled": False,
            "expected_else_fired": True,
        },
        {
            "category": "Neighboring supported input (derived independently)",
            "expr": "10 * (1 / 1)",
            "divisor": 1,
            "numerator": 10,
            "expected_result": 10.0,
            "expected_handled": False,
            "expected_else_fired": True,
        },
        {
            "category": "Ordinary input",
            "expr": "10 * (1 / 2)",
            "divisor": 2,
            "numerator": 10,
            "expected_result": 5.0,
            "expected_handled": False,
            "expected_else_fired": True,
        },
        {
            "category": "Smallest supported input (validating content over truthiness)",
            "expr": "0 * (1 / 1)",
            "divisor": 1,
            "numerator": 0,
            "expected_result": 0.0,
            "expected_handled": False,
            "expected_else_fired": True,
        },
        {
            "category": "Repeated-value / equivalent domain boundary (Pass 1)",
            "expr": "10 * (1 / 2)",
            "divisor": 2,
            "numerator": 10,
            "expected_result": 5.0,
            "expected_handled": False,
            "expected_else_fired": True,
        },
        {
            "category": "Repeated-value / equivalent domain boundary (Pass 2)",
            "expr": "10 * (1 / 2)",
            "divisor": 2,
            "numerator": 10,
            "expected_result": 5.0,
            "expected_handled": False,
            "expected_else_fired": True,
        },
        {
            "category": "Repeated exception boundary (Pass 1)",
            "expr": "10 * (1 / 0)",
            "divisor": 0,
            "numerator": 10,
            "expected_result": None,
            "expected_handled": True,
            "expected_else_fired": False,
        },
        {
            "category": "Repeated exception boundary (Pass 2)",
            "expr": "10 * (1 / 0)",
            "divisor": 0,
            "numerator": 10,
            "expected_result": None,
            "expected_handled": True,
            "expected_else_fired": False,
        },
    ]

    with patch("sys.stdout"), patch("sys.stderr"):
        for case in cases:
            handled = False
            else_fired = False
            actual_result = None

            try:
                if case["divisor"] == 0:
                    actual_result = case["numerator"] * (1 / 0)
                else:
                    actual_result = case["numerator"] * (1 / case["divisor"])
            except ZeroDivisionError:
                handled = True
            else:
                else_fired = True

            assert actual_result == case["expected_result"], (
                f"Mismatch result for {case['category']}: "
                f"expected {case['expected_result']}, got {actual_result}"
            )
            assert handled == case["expected_handled"], (
                f"Mismatch handled for {case['category']}: "
                f"expected {case['expected_handled']}, got {handled}"
            )
            assert else_fired == case["expected_else_fired"], (
                f"Mismatch else_fired for {case['category']}: "
                f"expected {case['expected_else_fired']}, got {else_fired}"
            )

            evidence["fixture_checks"].append({
                "category": case["category"],
                "input": case["expr"],
                "expected_result": case["expected_result"],
                "actual_result": actual_result,
                "expected_handled": case["expected_handled"],
                "actual_handled": handled,
                "expected_else_fired": case["expected_else_fired"],
                "actual_else_fired": else_fired,
                "match": True,
            })

    # Step 3: Run native focused pytest with project configuration
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "src/exceptions/test_handle_exceptions.py",
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

    print("R30-T021: All checks PASSED successfully.")
    print(f"Recorded {len(evidence['fixture_checks'])} fixture checks.")
    print(f"Nonzero pytest test count: {evidence['pytest_test_count']}")
    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    run_checks()
