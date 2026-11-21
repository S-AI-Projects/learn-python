```
R30-T031 test_if contract regression check
==========================================
Source contract anchors in src/control_flow/test_if.py:
- line 42: number = 15; conclusion = ''
- line 51: assert conclusion == 'Number bigger than or equal to one'

Boundary table for numbers evaluated:
- input -100: expected 'Number is less than zero'
- input -1: expected 'Number is less than zero'
- input 0: expected 'Number equals to zero'
- input 0.5: expected 'Number is greater than zero but less than one'
- input 1: expected 'Number bigger than or equal to one'
- input 15: expected 'Number bigger than or equal to one'
- input 42: expected 'Number bigger than or equal to one'

Requested command: python3 work/R30-T031/check.py
Focused pytest command: /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m pytest -s -v src/control_flow/test_if.py
Python: Python 3.14.7
Pytest: pytest 9.2.0
Nonzero test count: 2
Exit code: 0

Focused test output:
============================= test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.2.0, pluggy-1.7.0 -- /Library/Frameworks/Python.framework/Versions/3.14/bin/python3
cachedir: .pytest_cache
rootdir: /Users/shivamsourav/Ai-Project
collecting ... collected 2 items

src/control_flow/test_if.py::test_if_statement PASSED
src/control_flow/test_if.py::test_if_statement_contract_boundaries smallest/negative input: input=-100, expected='Number is less than zero', actual='Number is less than zero'
negative boundary: input=-1, expected='Number is less than zero', actual='Number is less than zero'
zero boundary: input=0, expected='Number equals to zero', actual='Number equals to zero'
neighboring supported input: input=0.5, expected='Number is greater than zero but less than one', actual='Number is greater than zero but less than one'
boundary at one: input=1, expected='Number bigger than or equal to one', actual='Number bigger than or equal to one'
ordinary input anchor: input=15, expected='Number bigger than or equal to one', actual='Number bigger than or equal to one'
repeated equivalent domain value: input=42, expected='Number bigger than or equal to one', actual='Number bigger than or equal to one'
PASSED

============================== 2 passed in 0.01s ===============================
```
