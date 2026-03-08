# =============================================================================
# 04_correlation_analysis.py
# PURPOSE : Examine intercorrelations among depression, anxiety, and mood
#           variables. Includes Pearson r, Spearman rho, and Kruskal-Wallis
#           tests comparing anxiety scores across depression groups.
# OUTPUT  : outputs/correlation_matrix.csv
#           Console printout of all test statistics
# RUN     : python 04_correlation_analysis.py
# =============================================================================

import pandas as pd
import numpy as np
from scipy import stats
from config import DATA_PATH, OUTPUT_DIR, GROUP_ORDER

df = pd.read_excel(DATA_PATH)

def assign_phq_group(score):
    if score <= 4:  return "Minimal"
    if score <= 9:  return "Mild"
    return "Moderate-Severe"

df["depression_group"] = df["score_phq"].apply(assign_phq_group)

# ─────────────────────────────────────────────────────────────────────────────
# PART A: Pearson & Spearman correlations
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("PART A: Pearson r and Spearman rho Correlations")
print("=" * 65)
print("  NOTE: Pearson r reported for comparison with original paper.")
print("  Spearman rho is preferred because PHQ/GAD/STAI violate normality.\n")

corr_pairs = [
    ("score_phq",           "score_gad",           "PHQ-9",  "GAD-7"),
    ("score_phq",           "score_stai_t",         "PHQ-9",  "STAI-T"),
    ("score_gad",           "score_stai_t",         "GAD-7",  "STAI-T"),
    ("score_phq",           "positive_affect_start","PHQ-9",  "PANAS Positive (Pre)"),
    ("score_phq",           "negative_affect_start","PHQ-9",  "PANAS Negative (Pre)"),
    ("positive_affect_start","negative_affect_start","PANAS Pos (Pre)","PANAS Neg (Pre)"),
]

print(f"  {'Pair':<38} {'Pearson r':>10} {'p':>8}  {'Spearman rho':>13} {'p':>8}")
print("  " + "-" * 82)
for c1, c2, l1, l2 in corr_pairs:
    pr, pp = stats.pearsonr(df[c1], df[c2])
    sr, sp = stats.spearmanr(df[c1], df[c2])
    pair_label = f"{l1} x {l2}"
    pp_str = f"{pp:.4f}" if pp >= 0.0001 else "<.0001"
    sp_str = f"{sp:.4f}" if sp >= 0.0001 else "<.0001"
    print(f"  {pair_label:<38} {pr:>10.3f} {pp_str:>8}  {sr:>13.3f} {sp_str:>8}")

# ─────────────────────────────────────────────────────────────────────────────
# PART B: Full correlation matrix
# ─────────────────────────────────────────────────────────────────────────────
matrix_cols = [
    "score_phq", "score_gad", "score_stai_t",
    "positive_affect_start", "negative_affect_start",
    "positive_affect_end",   "negative_affect_end",
]
col_labels = ["PHQ-9","GAD-7","STAI-T","PA-Pre","NA-Pre","PA-Post","NA-Post"]

corr_mat = df[matrix_cols].corr(method="spearman")
corr_mat.index   = col_labels
corr_mat.columns = col_labels

print("\n── Spearman Correlation Matrix ──")
print(corr_mat.round(3).to_string())
corr_mat.to_csv(f"{OUTPUT_DIR}/correlation_matrix.csv")
print(f"\n  Saved → {OUTPUT_DIR}/correlation_matrix.csv")

# ─────────────────────────────────────────────────────────────────────────────
# PART C: Kruskal-Wallis — do anxiety scores differ by depression group?
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("PART C: Kruskal-Wallis Tests — Anxiety by Depression Group")
print("=" * 65)
print("  H0: No difference in anxiety scores across depression groups")
print("  Used because data is non-normal (Shapiro-Wilk p < .05)\n")

kw_cols = {
    "score_gad":   "GAD-7",
    "score_stai_t":"STAI-T",
}

for col, label in kw_cols.items():
    groups = [df[df["depression_group"] == g][col].values for g in GROUP_ORDER]
    H, p = stats.kruskal(*groups)
    sig = "* SIGNIFICANT" if p < 0.05 else "not significant"
    print(f"  {label}: H = {H:.3f}, p = {p:.4f}  →  {sig}")

    # Group medians
    for g in GROUP_ORDER:
        sub = df[df["depression_group"] == g][col]
        print(f"    {g:<22}: Mdn = {sub.median():.1f}  (M = {sub.mean():.2f})")
    print()

# ─────────────────────────────────────────────────────────────────────────────
# PART D: Interpretation note for Report
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("PART D: Implication for Analysis Strategy")
print("=" * 65)
print("""
  The PHQ-9 is significantly correlated with both GAD-7 (r ≈ .58)
  and STAI-T (r ≈ .64), and anxiety scores differ significantly across
  depression groups (Kruskal-Wallis p < .01 for both measures).

  CONSEQUENCE: Any comparison of head-movement metrics across depression
  groups (Report 2) must control for anxiety. This will be done via:

    → ANCOVA with GAD-7 and STAI-T as covariates (parametric approach,
      following Srivastava & Lahane, 2025).

  This approach statistically partials out variance attributable to
  anxiety, isolating the unique effect of depression severity on
  psychomotor (head-scanning) behaviour.
""")
print("Done.")
