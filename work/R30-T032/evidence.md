```
R30-T032 test_generators boundary check
=======================================
Source contract anchors in src/additions/test_generators.py:
- line 26: for _ in range(3): yield random.randint(1, 10)
- line 30: yield random.randint(10, 20)
- line 37: assert 0 <= random_number <= 10
- line 39: assert 10 <= random_number <= 20

Boundary Table:
- Yield count boundary: exactly 4 items, followed by StopIteration on 5th next().
- Indices 0, 1, 2 (index < 3): range [1, 10] within asserted bounds [0, 10].
- Index 3 (neighboring boundary transition): range [10, 20] within asserted bounds [10, 20].
- Lower bounds verified: [1, 1, 1, 10]
- Upper bounds verified: [10, 10, 10, 20]

Requested command: python3 work/R30-T032/check.py
Focused pytest command: /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m pytest -s -v src/additions/test_generators.py
Python: Python 3.14.7
Pytest: pytest 9.2.0
Nonzero test count: 3
Exit code: 0

Focused test output:
============================= test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.2.0, pluggy-1.7.0 -- /Library/Frameworks/Python.framework/Versions/3.14/bin/python3
cachedir: .pytest_cache
rootdir: /Users/shivamsourav/Ai-Project
collecting ... collected 3 items

src/additions/test_generators.py::test_generators PASSED
src/additions/test_generators.py::test_generators_boundaries index 0: actual=10, expected in [1, 10]
index 1: actual=10, expected in [1, 10]
index 2: actual=7, expected in [1, 10]
index 3: actual=17, expected in [10, 20]
PASSED
src/additions/test_generators.py::test_generators_mocked_domain_boundaries lower boundaries: values=[1, 1, 1, 10]
upper boundaries: values=[10, 10, 10, 20]
PASSED

============================== 3 passed in 0.02s ===============================
```
