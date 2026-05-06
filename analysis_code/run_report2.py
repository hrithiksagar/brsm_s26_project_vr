"""
run_report2.py  [Report 2 — master runner]
─────────────────────────────────────────────────────────────────────────────
Executes all Report 2 analysis scripts in the correct dependency order.
Run from the analysis_code/ directory:

    python run_report2.py

Scripts run:
    09_extended_headtracking.py  — pitch / roll / total speed analyses
    10_ancova.py                 — ANCOVA per video
    11_regression.py             — multiple regression per video
    12_glm.py                    — GLM pooled across videos
    13_figures_report2.py        — Figures 6, 7, 8

To run only Report 1 scripts, use run_all.py (the original runner).
To run everything (Report 1 + Report 2), run run_all.py then run_report2.py.
"""

import subprocess
import sys
import time

SCRIPTS = [
    ("09_extended_headtracking.py", "Extended head-tracking (pitch/roll/total)"),
    ("10_ancova.py",                "ANCOVA: yaw ~ group + anxiety covariates"),
    ("11_regression.py",            "Multiple regression: yaw ~ PHQ9 + covariates + immersion"),
    ("12_glm.py",                   "GLM: yaw ~ group × video + covariates"),
    ("13_figures_report2.py",       "Figures 6, 7, 8"),
]

SEP = "=" * 65

def run(script: str, label: str) -> bool:
    print(f"\n{SEP}")
    print(f"  Running: {script}")
    print(f"  ({label})")
    print(SEP)
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False,   # let stdout/stderr stream to terminal
    )
    elapsed = time.time() - t0
    ok = result.returncode == 0
    status = "✓ OK" if ok else f"✗ FAILED (exit {result.returncode})"
    print(f"\n  [{status}]  {elapsed:.1f}s")
    return ok


if __name__ == "__main__":
    print(SEP)
    print("  Report 2 — full analysis pipeline")
    print(SEP)
    t_total = time.time()
    failures = []

    for script, label in SCRIPTS:
        ok = run(script, label)
        if not ok:
            failures.append(script)

    elapsed_total = time.time() - t_total
    print(f"\n{SEP}")
    if failures:
        print(f"  DONE with errors ({elapsed_total:.1f}s total)")
        print(f"  Failed scripts: {', '.join(failures)}")
        sys.exit(1)
    else:
        print(f"  ALL DONE ({elapsed_total:.1f}s total)")
        print(f"  Outputs written to: outputs/")
        print(SEP)
