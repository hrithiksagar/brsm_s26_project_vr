"""
run_all.py  —  Run all Report 1 analysis scripts in sequence
Usage:
  python run_all.py
"""

import subprocess, sys, time

SCRIPTS = [
    "01_data_exploration.py",
    "02_outliers_and_normality.py",
    "03_grouping_and_descriptives.py",
    "04_correlation_analysis.py",
    "05_video_and_mood_analysis.py",
    "06_head_tracking_analysis.py",
    "07_generate_figures.py",
]

print("=" * 60)
print("VR Depression Study — Report 1 Analysis Pipeline")
print("=" * 60)

for i, script in enumerate(SCRIPTS, 1):
    print(f"\n[{i}/{len(SCRIPTS)}] {script}")
    print("-" * 45)
    t0 = time.time()
    result = subprocess.run([sys.executable, script])
    elapsed = time.time() - t0
    if result.returncode == 0:
        print(f"  ✓  Done in {elapsed:.1f}s")
    else:
        print(f"  ✗  FAILED (exit {result.returncode}) — stopping.")
        sys.exit(1)

print("\n" + "=" * 60)
print("All scripts completed. Results saved to: outputs/")
print("=" * 60)
