"""File Wildcards.

@see: https://docs.python.org/3/tutorial/stdlib.html#file-wildcards

The glob module provides a function for making file lists from directory wildcard searches:
"""

import glob
import os


def test_glob(glob_func=glob.glob):
    """File Wildcards and Repeatability Contract.

    Observable External Dependencies:
      1. Current Working Directory (CWD): The relative pattern
         'src/standard_libraries/glob_files/*.txt' depends on os.getcwd() matching repo root.
      2. Filesystem State: The presence and names of files in 'src/standard_libraries/glob_files/'
         ('first_file.txt', 'second_file.txt'). Any external mutation alters results.
      3. Directory Entry Ordering: glob.glob() returns filenames in non-deterministic order
         across OS platforms; sorted() is required to ensure consistent comparisons.
      4. System Glob Seam: Standard library glob.glob function.

    Repeatability and Input-Isolation Contract:
      - Determinism: Executing the same query repeatedly against unchanged filesystem state
        produces identical sorted results.
      - Query Isolation: Interleaving different glob pattern queries (e.g. '*.py') does not
        alter, cache, or corrupt subsequent queries for '*.txt'.
      - Dependency Seam: glob_func defaults to glob.glob, preserving full backward
        compatibility with existing callers while allowing dependency injection for isolation.
    """

    # --- Source Anchor ---
    # == operator for lists relies on the order of elements in the list.
    # In some cases (like on Linux Mint, python3.6) the glob() function returns list
    # in reverse order then it might be expected. Thus lets sort both lists before comparison
    # using sorted() built-in function.
    anchor_pattern = 'src/standard_libraries/glob_files/*.txt'
    anchor_expected = sorted([
        'src/standard_libraries/glob_files/first_file.txt',
        'src/standard_libraries/glob_files/second_file.txt'
    ])
    assert sorted(glob_func(anchor_pattern)) == anchor_expected

    # --- Derived Neighboring Inputs ---
    # 1. Pattern matching only first file:
    pattern_first = 'src/standard_libraries/glob_files/*first*.txt'
    assert sorted(glob_func(pattern_first)) == [
        'src/standard_libraries/glob_files/first_file.txt'
    ]

    # 2. Pattern matching only second file:
    pattern_second = 'src/standard_libraries/glob_files/*second*.txt'
    assert sorted(glob_func(pattern_second)) == [
        'src/standard_libraries/glob_files/second_file.txt'
    ]

    # 3. Single-character wildcard pattern '?':
    pattern_single_char = 'src/standard_libraries/glob_files/?irst_file.txt'
    assert sorted(glob_func(pattern_single_char)) == [
        'src/standard_libraries/glob_files/first_file.txt'
    ]

    # 4. Pattern with no matches (empty list expected):
    pattern_py = 'src/standard_libraries/glob_files/*.py'
    assert glob_func(pattern_py) == []

    # --- In-test Repeatability & Isolation Check ---
    # Repeat anchor query immediately after other pattern queries:
    repeat_anchor = sorted(glob_func(anchor_pattern))
    assert repeat_anchor == anchor_expected


def test_glob_fixture_repeatability_and_isolation(tmp_path):
    """Verify repeatability and input isolation across fresh temporary fixtures."""
    # 1. Fresh isolated run 1 in directory A
    dir_a = tmp_path / "run_a"
    dir_a.mkdir()
    (dir_a / "first_file.txt").touch()
    (dir_a / "second_file.txt").touch()
    (dir_a / "data.csv").touch()

    pattern_a = str(dir_a / "*.txt")
    result_a1 = sorted(glob.glob(pattern_a))
    expected_a = sorted([
        str(dir_a / "first_file.txt"),
        str(dir_a / "second_file.txt")
    ])
    assert result_a1 == expected_a

    # 2. Fresh isolated run 2 in directory B (identical structure)
    dir_b = tmp_path / "run_b"
    dir_b.mkdir()
    (dir_b / "first_file.txt").touch()
    (dir_b / "second_file.txt").touch()
    (dir_b / "data.csv").touch()

    pattern_b = str(dir_b / "*.txt")
    result_b = sorted(glob.glob(pattern_b))
    expected_b = sorted([
        str(dir_b / "first_file.txt"),
        str(dir_b / "second_file.txt")
    ])
    assert result_b == expected_b

    # Verify identical normalized basename results
    basenames_a = [os.path.basename(p) for p in result_a1]
    basenames_b = [os.path.basename(p) for p in result_b]
    assert basenames_a == basenames_b == ['first_file.txt', 'second_file.txt']

    # 3. Interleaved query with distinct patterns (*.csv, then *.py)
    pattern_csv = str(dir_a / "*.csv")
    assert sorted(glob.glob(pattern_csv)) == [str(dir_a / "data.csv")]

    pattern_py = str(dir_a / "*.py")
    assert glob.glob(pattern_py) == []

    # 4. Post-other-input run: query *.txt on dir_a again; earlier runs cannot alter later result
    result_a2 = sorted(glob.glob(pattern_a))
    assert result_a2 == result_a1 == expected_a


def test_glob_mock_dependency_seam():
    """Verify test_glob functions identically with an isolated mock glob seam."""
    mock_registry = {
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

    def mock_glob(pattern):
        return list(mock_registry.get(pattern, []))

    # Executing test_glob via dependency seam must pass all assertions without disk I/O
    test_glob(glob_func=mock_glob)
