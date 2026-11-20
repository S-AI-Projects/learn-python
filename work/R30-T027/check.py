"""check.py – focused runner for R30-T027.

Verifies the worked-example assertions in test_zlib and its regression
companion, then runs the pytest suite for the module.  Exits non-zero on any
failure and writes work/R30-T027/report.json with full evidence.
"""
import json
import subprocess
import sys
import os
import types
from io import StringIO
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REPORT_PATH = os.path.join(os.path.dirname(__file__), 'report.json')
TARGET_REL = 'src/standard_libraries/test_zlib.py'
TARGET_ABS = os.path.join(REPO_ROOT, TARGET_REL)


def run_checks():
    """Execute all checks; return (failures, evidence_dict)."""
    sys.path.insert(0, REPO_ROOT)
    import importlib.util
    spec = importlib.util.spec_from_file_location('test_zlib', TARGET_ABS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    evidence = {}
    failures = []

    # --- Check 1: return value is None ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret = mod.test_zlib()
    evidence['return_value'] = repr(ret)
    if ret is not None:
        failures.append(f'Expected None return, got {ret!r}')

    # --- Check 2: regression test return value ---
    with patch('sys.stdout', new_callable=StringIO), \
         patch('sys.stderr', new_callable=StringIO):
        ret2 = mod.test_zlib_regression()
    evidence['regression_return_value'] = repr(ret2)
    if ret2 is not None:
        failures.append(f'Expected None from regression test, got {ret2!r}')

    # --- Check 3: source anchor – input length ---
    import zlib
    string = b'witch which has which witches wrist watch'
    evidence['anchor1'] = {
        'input': "b'witch which has which witches wrist watch'",
        'check': 'len(string)',
        'expected': 41,
        'actual': len(string),
    }
    if len(string) != 41:
        failures.append(f'Anchor1 len(string) failed: {len(string)}')

    # --- Check 4: source anchor – compressed length ---
    compressed = zlib.compress(string)
    evidence['anchor2'] = {
        'check': 'len(zlib.compress(string))',
        'expected': 37,
        'actual': len(compressed),
    }
    if len(compressed) != 37:
        failures.append(f'Anchor2 compressed len failed: {len(compressed)}')

    # --- Check 5: source anchor – lossless round-trip ---
    decompressed = zlib.decompress(compressed)
    evidence['anchor3'] = {
        'check': 'zlib.decompress(compressed)',
        'expected': repr(string),
        'actual': repr(decompressed),
    }
    if decompressed != string:
        failures.append(f'Anchor3 decompressed mismatch: {decompressed!r}')

    # --- Check 6: CRC-32 deterministic ---
    crc = zlib.crc32(string)
    evidence['crc32'] = {'expected': 226805979, 'actual': crc}
    if crc != 226805979:
        failures.append(f'CRC32 mismatch: {crc}')

    # --- Check 7: neighboring supported input (independently calculated) ---
    neighbor = b'hello hello hello'
    nb_compressed = zlib.compress(neighbor)
    nb_decompressed = zlib.decompress(nb_compressed)
    nb_crc = zlib.crc32(neighbor)
    evidence['neighboring_input'] = {
        'input': repr(neighbor),
        'len_input': len(neighbor),
        'expected_len_input': 17,
        'len_compressed': len(nb_compressed),
        'expected_len_compressed': 16,
        'decompressed_matches': nb_decompressed == neighbor,
        'crc32': nb_crc,
        'expected_crc32': 3858335872,
    }
    if len(neighbor) != 17:
        failures.append(f'Neighbor len failed: {len(neighbor)}')
    if len(nb_compressed) != 16:
        failures.append(f'Neighbor compressed len failed: {len(nb_compressed)}')
    if nb_decompressed != neighbor:
        failures.append(f'Neighbor decompressed mismatch: {nb_decompressed!r}')
    if nb_crc != 3858335872:
        failures.append(f'Neighbor CRC32 mismatch: {nb_crc}')

    # --- Check 8: decisive state transition – compression reduces size ---
    evidence['compression_reduces_size'] = {
        'input_len': len(string),
        'compressed_len': len(compressed),
        'reduced': len(compressed) < len(string),
    }
    if not (len(compressed) < len(string)):
        failures.append('Compression did not reduce size')

    # --- Check 9: module attribute mutation ---
    mod2 = types.ModuleType('test_zlib')
    mod2.__dict__.update(vars(mod))
    attrs_before = set(dir(mod2))
    mod.test_zlib()
    attrs_after = set(dir(mod2))
    evidence['module_attrs_mutated'] = list(set(dir(mod)) - attrs_before)
    if attrs_before != attrs_after:
        failures.append(f'Module attrs mutated: {set(dir(mod2)) - attrs_before}')

    # --- Check 10: run pytest on the target module ---
    proc = subprocess.run(
        [sys.executable, '-m', 'pytest', TARGET_REL, '-v', '--tb=short'],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    evidence['pytest_stdout'] = proc.stdout
    evidence['pytest_stderr'] = proc.stderr
    evidence['pytest_returncode'] = proc.returncode
    test_count = proc.stdout.count(' PASSED')
    evidence['pytest_test_count'] = test_count
    if test_count == 0:
        failures.append('No tests reported PASSED by pytest')
    if proc.returncode != 0:
        failures.append(f'pytest exited {proc.returncode}')

    # --- Tool versions ---
    ver = subprocess.run(
        [sys.executable, '--version'], capture_output=True, text=True
    )
    evidence['python_version'] = ver.stdout.strip() or ver.stderr.strip()
    pver = subprocess.run(
        [sys.executable, '-m', 'pytest', '--version'],
        capture_output=True, text=True
    )
    evidence['pytest_version'] = pver.stdout.strip()

    return failures, evidence


def main():
    failures, evidence = run_checks()
    evidence['failures'] = failures
    evidence['passed'] = len(failures) == 0

    with open(REPORT_PATH, 'w') as f:
        json.dump(evidence, f, indent=2)

    if failures:
        print('FAIL – the following checks did not pass:')
        for msg in failures:
            print(f'  • {msg}')
        sys.exit(1)
    else:
        print(f'All checks passed. pytest_test_count={evidence["pytest_test_count"]}')
        print(f'Report saved to {REPORT_PATH}')


if __name__ == '__main__':
    main()
