#!/usr/bin/env python3
"""Focused runner for Task R30-T059: __init__.py complexity experiment and scaling."""

import json
import os
import sys
import time
import subprocess
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULES_DIR = os.path.join(REPO_ROOT, "src", "modules")
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

from sound_package.effects import list_effects, AVAILABLE_EFFECTS


def run_checks():
    evidence = {
        "task_id": "R30-T059",
        "item": "src/modules/sound_package/effects/__init__.py",
        "tested_component": "__init__.py: list_effects",
        "complexity_specification": {
            "input_size_variable": "N = len(effects)",
            "theoretical_time_complexity": "O(N) linear time",
            "theoretical_space_complexity": "O(N) linear space",
            "distinction": "Theoretical claim is worst-case O(N) due to single-pass list comprehension; empirical measurements reflect interpreter execution timing."
        },
        "preconditions": [
            {
                "file": "src/modules/sound_package/effects/__init__.py",
                "line": 11,
                "precondition": "AVAILABLE_EFFECTS = ['echo'] defines default package exports"
            },
            {
                "file": "src/modules/sound_package/effects/__init__.py",
                "line": 17,
                "precondition": "def list_effects(effects=None) provides effect listing interface"
            }
        ],
        "fixture_checks": [],
        "scaling_measurements": [],
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

    # Step 1: Correctness verification for fixture cases (isolated from timing)
    with patch("sys.stdout"), patch("sys.stderr"):
        # Smallest valid input
        smallest_input = []
        smallest_expected = []
        smallest_actual = list_effects(smallest_input)
        assert smallest_actual == smallest_expected
        evidence["fixture_checks"].append({
            "case": "smallest_valid_input",
            "input": smallest_input,
            "expected": smallest_expected,
            "actual": smallest_actual,
            "match": True
        })

        # Ordinary input
        ordinary_input = ["echo", "reverb", "surround"]
        ordinary_expected = ["echo", "reverb", "surround"]
        ordinary_actual = list_effects(ordinary_input)
        assert ordinary_actual == ordinary_expected
        evidence["fixture_checks"].append({
            "case": "ordinary_input",
            "input": ordinary_input,
            "expected": ordinary_expected,
            "actual": ordinary_actual,
            "match": True
        })

    # Step 2: Complexity experiment on 3 increasing input sizes with 5 repetitions each
    # Fresh inputs, isolated from compilation and I/O
    test_sizes = [10, 100, 1000]
    repetitions = 5

    for size in test_sizes:
        durations = []
        for rep in range(repetitions):
            # Generate fresh test payload
            sample_payload = [f"effect_{i}" for i in range(size)]
            # Ensure correctness before timing
            expected_sample = sample_payload.copy()

            # Timed section: algorithmic operation only (no I/O, no startup)
            start_time = time.perf_counter_ns()
            out = list_effects(sample_payload)
            end_time = time.perf_counter_ns()

            assert out == expected_sample, f"Correctness check failed at size {size}"
            durations.append(end_time - start_time)

        durations.sort()
        median_ns = durations[len(durations) // 2]
        range_ns = {"min_ns": durations[0], "max_ns": durations[-1]}

        evidence["scaling_measurements"].append({
            "input_size_N": size,
            "repetitions": repetitions,
            "durations_ns": durations,
            "median_ns": median_ns,
            "range_ns": range_ns
        })

    # Native pytest check
    cmd = [sys.executable, "-m", "pytest", "src/modules/test_packages.py", "-k", "test_effects_init_complexity", "-v"]
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

    print("R30-T059: All checks PASSED successfully.")
    print(f"Complexity experiment completed. Report saved to {report_path}")


if __name__ == "__main__":
    run_checks()
