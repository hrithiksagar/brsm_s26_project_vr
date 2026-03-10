"""
03_grouping_and_descriptives.py
PURPOSE : Assign PHQ-9 depression severity groups, compute full descriptive
          statistics per group, and save a summary CSV.
OUTPUT  : outputs/descriptive_stats.csv
          outputs/group_stats.csv
RUN     : python 03_grouping_and_descriptives.py
"""

import pandas as pd
import numpy as np
from scipy import stats
from config import DATA_PATH, OUTPUT_DIR, PHQ_GROUPS, GROUP_ORDER

df = pd.read_excel(DATA_PATH)

# 1. Assign depression groups
def assign_phq_group(score):
    """
    Assigns a PHQ-9 severity label using validated cut-offs from
    Kroenke et al. (2001), Journal of General Internal Medicine, 16(9), 606-613.
    """
    for label, (lo, hi) in PHQ_GROUPS.items():
        if lo <= score <= hi:
            return label
    return "Unknown"

df["depression_group"] = df["score_phq"].apply(assign_phq_group)

print("=" * 65)
print("Depression Group Counts")
print("=" * 65)
for g in GROUP_ORDER:
    n = (df["depression_group"] == g).sum()
    pct = n / len(df) * 100
    print(f"  {g:<22}: n={n:>3}  ({pct:.1f}%)")
print(f"  {'TOTAL':<22}: n={len(df)}")

# 2. Full descriptive statistics (all participants)
desc_cols = [
    "age", "score_phq", "score_gad", "score_stai_t",
    "positive_affect_start", "positive_affect_end",
    "negative_affect_start", "negative_affect_end",
]

def describe_col(series):
    """Returns a dict with common descriptive stats + skewness + kurtosis."""
    return {
        "N":        len(series),
        "Mean":     round(series.mean(), 2),
        "SD":       round(series.std(), 2),
        "Median":   round(series.median(), 2),
        "Min":      series.min(),
        "Max":      series.max(),
        "Q1":       round(series.quantile(0.25), 2),
        "Q3":       round(series.quantile(0.75), 2),
        "Skewness": round(stats.skew(series), 3),
        "Kurtosis": round(stats.kurtosis(series), 3),
    }

rows = []
for col in desc_cols:
    d = describe_col(df[col])
    d["Variable"] = col
    rows.append(d)

desc_df = pd.DataFrame(rows).set_index("Variable")
print("\n── Full Descriptive Statistics ──")
print(desc_df.to_string())

desc_df.to_csv(f"{OUTPUT_DIR}/descriptive_stats.csv")
print(f"\n  Saved → {OUTPUT_DIR}/descriptive_stats.csv")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Group-level descriptive statistics
# ─────────────────────────────────────────────────────────────────────────────
group_cols = ["score_phq", "score_gad", "score_stai_t",
              "positive_affect_start", "negative_affect_start"]

print("\n── Descriptive Stats by Depression Group ──")
group_rows = []
for g in GROUP_ORDER:
    sub = df[df["depression_group"] == g]
    row = {"Group": g, "n": len(sub)}
    for col in group_cols:
        row[f"{col}_M"]  = round(sub[col].mean(), 2)
        row[f"{col}_SD"] = round(sub[col].std(),  2)
    group_rows.append(row)

group_df = pd.DataFrame(group_rows)
print(group_df.to_string(index=False))
group_df.to_csv(f"{OUTPUT_DIR}/group_stats.csv", index=False)
print(f"\n  Saved → {OUTPUT_DIR}/group_stats.csv")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Per-video descriptive stats
# ─────────────────────────────────────────────────────────────────────────────
print("\n── Per-Video Descriptive Stats ──")
print(f"  {'Video':<6} {'Valence M':>10} {'Val SD':>8} "
      f"{'Arousal M':>10} {'Aro SD':>8} {'Immersion M':>13} {'Imm SD':>8}")
for i in range(1, 6):
    vm = df[f"valence_v{i}"].mean();   vs = df[f"valence_v{i}"].std()
    am = df[f"arousal_v{i}"].mean();   as_ = df[f"arousal_v{i}"].std()
    im = df[f"immersion_v{i}"].mean(); is_ = df[f"immersion_v{i}"].std()
    print(f"  V{i:<5} {vm:>10.2f} {vs:>8.2f} {am:>10.2f} {as_:>8.2f} "
          f"{im:>13.2f} {is_:>8.2f}")

print("\nDone.")
