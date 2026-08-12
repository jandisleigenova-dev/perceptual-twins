#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "reference_implementation" / "perceptual_twins_synthetic_poc.py"
EXPECTED = ROOT / "expected_outputs" / "synthetic_estimand_recovery.json"


def compare(a, b, path="root"):
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            raise AssertionError(f"{path}: key mismatch: {set(a) ^ set(b)}")
        for k in a:
            compare(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise AssertionError(f"{path}: list length mismatch")
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, f"{path}[{i}]")
    elif isinstance(a, bool) or isinstance(b, bool):
        if a is not b:
            raise AssertionError(f"{path}: {a!r} != {b!r}")
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if not math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=1e-12):
            raise AssertionError(f"{path}: {a!r} != {b!r}")
    else:
        if a != b:
            raise AssertionError(f"{path}: {a!r} != {b!r}")


def main():
    if not SCRIPT.exists() or not EXPECTED.exists():
        raise SystemExit("Missing reference implementation or expected output.")

    temp = Path(tempfile.mkdtemp(prefix="perceptual_twins_repro_"))
    try:
        subprocess.run(
            [sys.executable, str(SCRIPT), "--output-dir", str(temp)],
            check=True,
        )
        got = json.loads((temp / "synthetic_estimand_recovery.json").read_text(encoding="utf-8"))
        exp = json.loads(EXPECTED.read_text(encoding="utf-8"))
        compare(got, exp)

        if got["all_reference_values_covered"] is not True:
            raise AssertionError("Reference coverage flag is not true.")

        eq_rows = [r for r in got["results"] if r["contrast"] == "delta_exec_eq"]
        if len(eq_rows) != 2 or any(r["estimate"] != 0.0 for r in eq_rows):
            raise AssertionError("Execution-equivalence diagnostic is not exactly zero.")

        print("PASS: released reference implementation reproduced successfully.")
        print("All released JSON values match within absolute tolerance 1e-12.")
        print("All reference values are covered, and both execution-equivalence estimates are exactly zero.")
    finally:
        shutil.rmtree(temp, ignore_errors=True)


if __name__ == "__main__":
    main()
