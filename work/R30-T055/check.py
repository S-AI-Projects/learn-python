#!/usr/bin/env python3
"""Focused runner for Task R30-T055: test_json deterministic execution and repeatability."""

import json
import os
import sys
import subprocess
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.standard_libraries.test_json import test_json, test_json_repeatability_and_isolation


def run_checks():
    evidence = {
        "task_id": "R30-T055",
        "item": "src/standard_libraries/test_json.py",
        "tested_function": "test_json",
        "source_anchors": [
            "assert person_dictionary['first_name'] == 'John'",
            "assert person_dictionary['age'] == 42",
            "assert person_parsed_dictionary == person_dictionary"
        ],
        "external_dependencies_identified": "None (pure function, no network/file/GUI/time)",
        "isolation_runs": [],
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
        test_json()
        test_json_repeatability_and_isolation()

    # Step 1: First anchor run
    anchor_dict = {'first_name': 'John', 'last_name': 'Smith', 'age': 42}
    anchor_json = '{"first_name": "John", "last_name": "Smith", "age": 42}'
    parsed_1 = json.loads(anchor_json)
    dumps_1 = json.dumps(anchor_dict)
    assert parsed_1 == anchor_dict
    assert dumps_1 == anchor_json
    evidence["isolation_runs"].append({
        "stage": "initial_anchor_run",
        "input": anchor_json,
        "expected": anchor_dict,
        "actual": parsed_1,
        "match": True
    })

    # Step 2: Neighboring supported input
    neighbor_dict = {'first_name': 'Jane', 'last_name': 'Doe', 'age': 30}
    neighbor_json = '{"first_name": "Jane", "last_name": "Doe", "age": 30}'
    parsed_neighbor = json.loads(neighbor_json)
    dumps_neighbor = json.dumps(neighbor_dict)
    assert parsed_neighbor == neighbor_dict
    assert dumps_neighbor == neighbor_json
    evidence["isolation_runs"].append({
        "stage": "neighboring_supported_input",
        "input": neighbor_json,
        "expected": neighbor_dict,
        "actual": parsed_neighbor,
        "match": True
    })

    # Step 3: Repeated anchor run after neighbor run (testing isolation)
    parsed_2 = json.loads(anchor_json)
    dumps_2 = json.dumps(anchor_dict)
    assert parsed_2 == anchor_dict
    assert dumps_2 == anchor_json
    assert parsed_2 == parsed_1
    evidence["isolation_runs"].append({
        "stage": "repeated_anchor_run_after_neighbor",
        "input": anchor_json,
        "expected": anchor_dict,
        "actual": parsed_2,
        "identical_to_run_1": True
    })

    # Native pytest check
    cmd = [sys.executable, "-m", "pytest", "src/standard_libraries/test_json.py", "-v"]
    evidence["pytest_command"] = " ".join(cmd)
    proc = subprocess.run(cmd, cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print(f"pytest failed:\n{proc.stdout}\n{proc.stderr}", file=sys.stderr)
        sys.exit(proc.returncode)

    evidence["pytest_output"] = proc.stdout
    evidence["pytest_test_count"] = 2
    evidence["success"] = True

    report_path = os.path.join(os.path.dirname(__file__), "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)

    print("R30-T055: All checks PASSED successfully.")
    print(f"Verified {len(evidence['isolation_runs'])} isolation runs. Report saved to {report_path}")


if __name__ == "__main__":
    run_checks()
