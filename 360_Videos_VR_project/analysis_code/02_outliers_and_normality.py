"""
02_outliers_and_normality.py
PURPOSE : Test normality of all key variables (Shapiro-Wilk), detect
          outliers via IQR and z-score methods, and print a decision
          rationale for inclusion/exclusion.
OUTPUT  : Console printout
RUN     : python 02_outliers_and_normality.py
"""

import pandas as pd
import numpy as np
from scipy import stats
from config import DATA_PATH, QUESTIONNAIRE_COLS, ALPHA, ZSCORE_THRESH, IQR_MULTIPLIER

df = pd.read_excel(DATA_PATH)

# PART A: Shapiro-Wilk Normality Tests
print("=" * 65)
print("PART A: Shapiro-Wilk Normality Tests")
print("=" * 65)
print(f"  H0: Data is normally distributed")
print(f"  Reject H0 if p < {ALPHA}\n")

# Columns to test
test_cols = {
    **QUESTIONNAIRE_COLS,
    "positive_affect_start": "PANAS Positive (Pre)",
    "positive_affect_end":   "PANAS Positive (Post)",
    "negative_affect_start": "PANAS Negative (Pre)",
    "negative_affect_end":   "PANAS Negative (Post)",
    "age":                   "Age",
}

print(f"  {'Variable':<25} {'W':>8} {'p-value':>10} {'Normal?':>10}")
print("  " + "-" * 55)
for col, label in test_cols.items():
    W, p = stats.shapiro(df[col])
    normal = "YES" if p >= ALPHA else "NO *"
    print(f"  {label:<25} {W:>8.3f} {p:>10.4f} {normal:>10}")

print("\n  * p < .05 → normality assumption violated → use non-parametric tests")

# PART B: Outlier Detection
print("\n" + "=" * 65)
print("PART B: Outlier Detection")
print("=" * 65)

outlier_cols = list(QUESTIONNAIRE_COLS.keys())

for col in outlier_cols:
    label = QUESTIONNAIRE_COLS[col]
    series = df[col]

    # Method 1: IQR
    Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - IQR_MULTIPLIER * IQR
    upper = Q3 + IQR_MULTIPLIER * IQR
    iqr_outliers = df[(series < lower) | (series > upper)]

    # Method 2: Z-score
    z_scores = np.abs(stats.zscore(series))
    z_outliers = df[z_scores > ZSCORE_THRESH]

    print(f"\n  {label}")
    print(f"    IQR range  : [{lower:.1f}, {upper:.1f}]")
    print(f"    IQR method : {len(iqr_outliers)} outlier(s)  "
          f"→ scores: {sorted(iqr_outliers[col].tolist())}")
    print(f"    Z-score    : {len(z_outliers)} outlier(s) (|z|>{ZSCORE_THRESH})  "
          f"→ scores: {sorted(z_outliers[col].tolist())}")

# PART C: Decision Rationale
print("\n" + "=" * 65)
print("PART C: Inclusion / Exclusion Decision")
print("=" * 65)
print("""
  DECISION: RETAIN all participants (no exclusions).

  REASONING:
  1. All flagged values fall within the valid PHQ-9 range (0–27) and
     GAD-7 range (0–21). They are extreme but not impossible or erroneous.

  2. The flagged participants belong to the Moderate-Severe depression
     group — the most clinically important subgroup for the core hypothesis.
     Removing them would eliminate the very cases the study is designed
     to examine, leaving only n=8 and severely reducing statistical power.

  3. Tabachnick & Fidell (2019) advise against removing extreme scores
     when they carry substantive meaning. The PHQ-9 scale was designed
     to detect high-severity cases; a score of 18 is a real data point,
     not a measurement error.

  4. The original paper (Srivastava & Lahane, 2025) retained all
     participants. Excluding any would undermine direct replication.

  5. The unequal group sizes (Minimal n=20, Mild n=12, Mod-Severe n=8)
     will be acknowledged as a limitation and handled in Report 2 via
     appropriate effect-size measures (eta-squared, Cohen's d) rather
     than by artificially balancing through exclusion.
""")
print("Done.")
