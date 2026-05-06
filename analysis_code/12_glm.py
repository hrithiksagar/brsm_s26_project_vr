"""
12_glm.py  [Report 2]
─────────────────────────────────────────────────────────────────────────────
General Linear Model (GLM) in long format, pooling all five videos.

Two OLS models are fitted:
  Interaction model:   yaw ~ C(depression_group) * C(video) + GAD7 + STAI-T
  Main effects model:  yaw ~ C(depression_group) + C(video) + GAD7 + STAI-T

Reference levels: Minimal depression group, V1 (Abandoned Buildings).

For both models the script produces:
  • Model fit statistics (R², adj-R², F, p)
  • Type II ANOVA table (statsmodels anova_lm, typ=2)
  • Regression coefficients for the main-effects model
  • Interaction F-test comparison

OUTPUT
  outputs/report2_glm_fit.csv         — model fit comparison
  outputs/report2_glm_anova.csv       — Type II ANOVA table (interaction model)
  outputs/report2_glm_coef.csv        — coefficients (main-effects model)
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

from config import GROUP_ORDER, VIDEO_NAMES, OUTPUT_DIR
from data_loader import build_headtrack, build_long

# ── Load data ─────────────────────────────────────────────────────────────────
print("=" * 65)
print("12  GLM: Yaw ~ Video × Depression Group + GAD-7 + STAI-T")
print("=" * 65)

ht   = build_headtrack()
long = build_long(ht)
print(f"  Long-format table: {len(long)} rows "
      f"({len(ht)} participants × 5 videos)\n")

# ── Model formulae ────────────────────────────────────────────────────────────
FORMULA_INT  = ("yaw ~ C(depression_group, Treatment('Minimal'))"
                " * C(video, Treatment('V1'))"
                " + score_gad + score_stai_t")

FORMULA_MAIN = ("yaw ~ C(depression_group, Treatment('Minimal'))"
                " + C(video, Treatment('V1'))"
                " + score_gad + score_stai_t")

# ── Fit models ────────────────────────────────────────────────────────────────
m_int  = smf.ols(FORMULA_INT,  data=long).fit()
m_main = smf.ols(FORMULA_MAIN, data=long).fit()

# ── Model fit summary ─────────────────────────────────────────────────────────
print("  ── Model Fit ──────────────────────────────────────────────")
for label, m in [("Interaction model", m_int), ("Main effects model", m_main)]:
    print(f"\n  {label}")
    print(f"    N = {len(long)}")
    print(f"    R²     = {m.rsquared:.4f}")
    print(f"    adj-R² = {m.rsquared_adj:.4f}")
    print(f"    F({m.df_model:.0f},{m.df_resid:.0f}) = {m.fvalue:.3f}, p = {m.f_pvalue:.6f}")

fit_rows = [
    {
        "model":      label,
        "N":          len(long),
        "R2":         round(m.rsquared,     4),
        "adj_R2":     round(m.rsquared_adj, 4),
        "F":          round(m.fvalue,       4),
        "df_model":   int(m.df_model),
        "df_resid":   int(m.df_resid),
        "p":          round(m.f_pvalue,     6),
    }
    for label, m in [("interaction", m_int), ("main_effects", m_main)]
]

# ── Type II ANOVA table — interaction model ───────────────────────────────────
print("\n\n  ── Type II ANOVA: Interaction Model ───────────────────────")
at_int = anova_lm(m_int, typ=2)
print(at_int.to_string())

# ── Type II ANOVA table — main effects model ──────────────────────────────────
print("\n\n  ── Type II ANOVA: Main Effects Model ──────────────────────")
at_main = anova_lm(m_main, typ=2)
print(at_main.to_string())

# ── Coefficients — main effects model ────────────────────────────────────────
print("\n\n  ── Coefficients: Main Effects Model ───────────────────────")
print(f"  Reference: Minimal group, V1 (Abandoned Buildings)\n")
print(f"  {'Predictor':<52} {'β':>8} {'SE':>8} {'p':>8}  Sig")
print(f"  {'─'*85}")

coef_rows = []
for pname in m_main.params.index:
    beta = m_main.params[pname]
    se   = m_main.bse[pname]
    pval = m_main.pvalues[pname]
    sig  = ("***" if pval < .001 else "**" if pval < .01
            else "*" if pval < .05 else "†" if pval < .10 else "ns")
    print(f"  {pname:<52} {beta:>8.4f} {se:>8.4f} {pval:>8.4f}  {sig}")
    coef_rows.append({
        "predictor": pname,
        "beta":      round(float(beta), 4),
        "SE":        round(float(se),   4),
        "p":         round(float(pval), 4),
        "sig":       sig,
    })

# ── F-test: does adding the interaction improve fit? ─────────────────────────
print("\n\n  ── Model Comparison: Interaction vs Main Effects ──────────")
f_test = m_main.compare_f_test(m_int)
# compare_f_test returns (F, p, df_diff) when comparing nested models
# Note: direction is M_main vs M_int; M_int is the unrestricted model
print(f"  F-change = {f_test[0]:.4f},  df = {f_test[2]:.0f},  p = {f_test[1]:.4f}")
print(f"  → Interaction term {'does NOT improve' if f_test[1] > 0.05 else 'DOES improve'} "
      f"model fit beyond main effects (p = {f_test[1]:.4f})")

# ── Save ──────────────────────────────────────────────────────────────────────
fit_path  = f"{OUTPUT_DIR}/report2_glm_fit.csv"
anov_path = f"{OUTPUT_DIR}/report2_glm_anova.csv"
coef_path = f"{OUTPUT_DIR}/report2_glm_coef.csv"

pd.DataFrame(fit_rows).to_csv(fit_path, index=False)
at_int.reset_index().rename(columns={"index": "source"}).to_csv(anov_path, index=False)
pd.DataFrame(coef_rows).to_csv(coef_path, index=False)

print(f"\n  → Saved: {fit_path}")
print(f"  → Saved: {anov_path}")
print(f"  → Saved: {coef_path}")

# ── Key numbers for Report 2 write-up ────────────────────────────────────────
print("\n" + "=" * 65)
print("  Key numbers for report write-up")
print("=" * 65)
for row in at_int.itertuples():
    src = row.Index
    print(f"  {src:<55} F={row.F:.3f}  p={row._4:.4f}")

print(f"\n  Mild vs Minimal (main effects model):")
mild_key = [k for k in m_main.params.index if "Mild" in k and "Moderate" not in k]
ms_key   = [k for k in m_main.params.index if "Moderate" in k]
if mild_key:
    k = mild_key[0]
    print(f"    β = {m_main.params[k]:.4f}, SE = {m_main.bse[k]:.4f}, "
          f"p = {m_main.pvalues[k]:.4f}")
if ms_key:
    k = ms_key[0]
    print(f"  Mod-Sev vs Minimal:")
    print(f"    β = {m_main.params[k]:.4f}, SE = {m_main.bse[k]:.4f}, "
          f"p = {m_main.pvalues[k]:.4f}")

print("\nDone — 12_glm.py")
