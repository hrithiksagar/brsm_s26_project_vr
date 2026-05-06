"""
11_regression.py  [Report 2]
─────────────────────────────────────────────────────────────────────────────
Multiple regression: predicting yaw scanning speed from PHQ-9 (continuous),
GAD-7, STAI-T, and per-video immersion rating.

For each of the five videos, two OLS models are estimated:
  Model 0 (covariates):  yaw ~ GAD7 + STAI-T + immersion
  Model 1 (full):        yaw ~ PHQ9 + GAD7 + STAI-T + immersion

The unique variance contributed by PHQ-9 is ΔR² = R²(M1) − R²(M0).
A partial regression (component-plus-residual) plot is also available for
video V5, the only model that reached overall significance.

OUTPUT
  outputs/report2_regression.csv       — per-video model fit
  outputs/report2_regression_coef.csv  — per-video coefficients (full model)
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from scipy import stats

from config import GROUP_ORDER, VIDEO_NAMES, OUTPUT_DIR
from data_loader import build_headtrack

# ── Load data ─────────────────────────────────────────────────────────────────
print("=" * 65)
print("11  Multiple Regression: Yaw ~ PHQ-9 + GAD-7 + STAI-T + Immersion")
print("=" * 65)

ht = build_headtrack()
print(f"  N = {len(ht)} participants\n")

# ── Per-video regression ──────────────────────────────────────────────────────
summary_rows = []
coef_rows    = []

for v in range(1, 6):
    yaw_col = f"v{v}_mean_yaw"
    imm_col = f"immersion_v{v}"
    tmp = ht[[yaw_col, "score_phq", "score_gad",
              "score_stai_t", imm_col]].dropna().copy()
    tmp.columns = ["yaw", "phq", "gad", "stai", "imm"]

    print(f"\n{'─'*65}")
    print(f"  V{v}: {VIDEO_NAMES[v]}   (N = {len(tmp)})")
    print(f"{'─'*65}")

    m0 = smf.ols("yaw ~ gad + stai + imm",       data=tmp).fit()   # covariates only
    m1 = smf.ols("yaw ~ phq + gad + stai + imm", data=tmp).fit()   # full model

    delta_r2 = m1.rsquared - m0.rsquared

    sig = ("***" if m1.f_pvalue < .001 else "**" if m1.f_pvalue < .01
           else "*" if m1.f_pvalue < .05 else "ns")

    print(f"  Covariates-only R² = {m0.rsquared:.4f}")
    print(f"  Full model      R² = {m1.rsquared:.4f},  "
          f"adj-R² = {m1.rsquared_adj:.4f}")
    print(f"  ΔR²(PHQ-9 unique) = {delta_r2:.4f}")
    print(f"  F({m1.df_model:.0f},{m1.df_resid:.0f}) = {m1.fvalue:.3f}, "
          f"p = {m1.f_pvalue:.4f}  {sig}")
    print()

    # Coefficients
    print(f"  {'Predictor':<14} {'β':>9} {'SE':>9} {'p':>9}  Sig")
    print(f"  {'─'*55}")
    for pname in m1.params.index:
        beta = m1.params[pname]
        se   = m1.bse[pname]
        pval = m1.pvalues[pname]
        ps   = ("***" if pval < .001 else "**" if pval < .01
                else "*" if pval < .05 else "ns")
        print(f"  {pname:<14} {beta:>9.4f} {se:>9.4f} {pval:>9.4f}  {ps}")
        coef_rows.append({
            "video":     f"V{v}",
            "predictor": pname,
            "beta":      round(float(beta), 4),
            "SE":        round(float(se),   4),
            "p":         round(float(pval), 4),
            "sig":       ps,
        })

    summary_rows.append({
        "video":          f"V{v}",
        "video_name":     VIDEO_NAMES[v],
        "N":              len(tmp),
        "R2_cov_only":    round(m0.rsquared,     4),
        "R2_full":        round(m1.rsquared,     4),
        "adj_R2_full":    round(m1.rsquared_adj, 4),
        "delta_R2_phq":   round(delta_r2,        4),
        "F":              round(m1.fvalue,        4),
        "df_model":       int(m1.df_model),
        "df_resid":       int(m1.df_resid),
        "p":              round(m1.f_pvalue,      4),
        "sig":            sig,
        # PHQ-9 specific
        "beta_phq":       round(float(m1.params.get("phq", np.nan)), 4),
        "p_phq":          round(float(m1.pvalues.get("phq", np.nan)), 4),
        # Immersion specific
        "beta_imm":       round(float(m1.params.get("imm", np.nan)), 4),
        "p_imm":          round(float(m1.pvalues.get("imm", np.nan)), 4),
    })

    # Partial regression: residualise yaw and phq on covariates (reported in text for V5)
    if v == 5:
        m_y_res   = smf.ols("yaw ~ gad + stai + imm", data=tmp).fit()
        m_phq_res = smf.ols("phq ~ gad + stai + imm", data=tmp).fit()
        r_partial, p_partial = stats.pearsonr(m_phq_res.resid, m_y_res.resid)
        print(f"\n  Partial correlation (PHQ-9 ↔ yaw, V5, after removing GAD/STAI/Imm):")
        print(f"    r = {r_partial:.4f}, p = {p_partial:.4f}")
        summary_rows[-1]["partial_r_phq_v5"]   = round(r_partial, 4)
        summary_rows[-1]["partial_p_phq_v5"]   = round(p_partial, 4)

# ── Save ──────────────────────────────────────────────────────────────────────
summary_path = f"{OUTPUT_DIR}/report2_regression.csv"
coef_path    = f"{OUTPUT_DIR}/report2_regression_coef.csv"
pd.DataFrame(summary_rows).to_csv(summary_path, index=False)
pd.DataFrame(coef_rows).to_csv(coef_path, index=False)
print(f"\n  → Saved: {summary_path}")
print(f"  → Saved: {coef_path}")

# ── Console summary ───────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  Summary: Regression fit per video")
print("=" * 65)
print(f"  {'Video':<26} {'R²':>6} {'adj-R²':>8} {'ΔR²_PHQ':>9} {'F':>8} {'p':>8}  Sig")
print(f"  {'─'*75}")
for r in summary_rows:
    print(f"  {r['video']}: {r['video_name']:<22} {r['R2_full']:>6.4f}"
          f" {r['adj_R2_full']:>8.4f} {r['delta_R2_phq']:>9.4f}"
          f" {r['F']:>8.3f} {r['p']:>8.4f}  {r['sig']}")

print("\nDone — 11_regression.py")
