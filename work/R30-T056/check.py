#!/usr/bin/env python3
"""Focused runner for Task R30-T056: echo_function refactoring."""

import json
import os
import sys
import subprocess
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULES_DIR = os.path.join(REPO_ROOT, "src", "modules")
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

from sound_package.effects.echo import echo_function, format_effect_message


def run_checks():
    evidence = {
        "task_id": "R30-T056",
        "item": "src/modules/sound_package/effects/echo.py",
        "tested_function": "echo_function",
        "refactoring_summary": "Extracted string formatting calculation into format_effect_message helper",
        "preconditions": [
            {"source_file": "src/modules/sound_package/effects/echo.py", "line": 7, "precondition": "format_effect_message helper definition"},
            {"source_file": "src/modules/sound_package/effects/echo.py", "line": 12, "precondition": "echo_function signature with default parameters"}
        ],
        "cases_checked": [],
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
        # Smallest valid input
        res_smallest = echo_function()
        assert res_smallest == "Do echo effect"
        evidence["cases_checked"].append({
            "type": "smallest_valid_input (defaults)",
            "call": "echo_function()",
            "expected": "Do echo effect",
            "actual": res_smallest,
            "match": True
        })

        # Ordinary input
        res_ordinary = echo_function(action="Apply", effect="echo effect")
        assert res_ordinary == "Apply echo effect"
        evidence["cases_checked"].append({
            "type": "ordinary_input",
            "call": "echo_function('Apply', 'echo effect')",
            "expected": "Apply echo effect",
            "actual": res_ordinary,
            "match": True
        })

        # Helper unit check
        res_helper = format_effect_message("Test", "reverb")
        assert res_helper == "Test reverb"
        evidence["cases_checked"].append({
            "type": "helper_contract",
            "call": "format_effect_message('Test', 'reverb')",
            "expected": "Test reverb",
            "actual": res_helper,
            "match": True
        })

    # Native pytest check
    cmd = [sys.executable, "-m", "pytest", "src/modules/test_packages.py", "-k", "test_echo_function_refactoring", "-v"]
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

    print("R30-T056: All checks PASSED successfully.")
    print(f"Verified {len(evidence['cases_checked'])} cases. Report saved to {report_path}")


if __name__ == "__main__":
    run_checks()
