"""
10_ancova.py  [Report 2]
─────────────────────────────────────────────────────────────────────────────
ANCOVA: does depression group predict yaw scanning speed after statistically
removing the shared variance with anxiety (GAD-7, STAI-T)?

For each of the five videos a separate OLS model is fitted:
  yaw_speed ~ C(depression_group) + GAD7 + STAI-T

Reference group: Minimal depression (treatment coding).

For each model the script reports:
  • Overall F-ratio and p-value
  • ΔR² attributable to the group factor (above covariates-only model)
  • Individual regression coefficients (β, SE, p)
  • Anxiety-adjusted (LS/marginal) means per group, evaluated at the
    grand-mean of GAD-7 and STAI-T

OUTPUT
  outputs/report2_ancova.csv    — full results table
  outputs/report2_ancova_coef.csv — coefficient table (all videos)
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from scipy import stats

from config import GROUP_ORDER, VIDEO_NAMES, OUTPUT_DIR
from data_loader import build_headtrack

# ── Load data ─────────────────────────────────────────────────────────────────
print("=" * 65)
print("10  ANCOVA: Yaw Speed ~ Depression Group + GAD-7 + STAI-T")
print("=" * 65)

ht = build_headtrack()
print(f"  N = {len(ht)} participants\n")

# ── Per-video ANCOVA ──────────────────────────────────────────────────────────
summary_rows = []
coef_rows    = []

for v in range(1, 6):
    yaw_col = f"v{v}_mean_yaw"
    tmp = ht[["depression_group", "score_gad", "score_stai_t", yaw_col]].dropna().copy()
    tmp.columns = ["group", "gad", "stai", "yaw"]
    tmp["group"] = tmp["group"].astype(str)   # smf needs plain string categories

    print(f"\n{'─'*65}")
    print(f"  V{v}: {VIDEO_NAMES[v]}   (N = {len(tmp)})")
    print(f"{'─'*65}")

    # Covariates-only model (no group)
    m_cov  = smf.ols("yaw ~ gad + stai", data=tmp).fit()

    # Full ANCOVA model
    m_full = smf.ols(
        "yaw ~ C(group, Treatment('Minimal')) + gad + stai", data=tmp
    ).fit()

    delta_r2 = m_full.rsquared - m_cov.rsquared

    print(f"  Covariates-only R² = {m_cov.rsquared:.4f}")
    print(f"  Full model      R² = {m_full.rsquared:.4f}  "
          f"(ΔR²_group = {delta_r2:.4f})")
    print(f"  F({m_full.df_model:.0f},{m_full.df_resid:.0f}) = {m_full.fvalue:.3f}, "
          f"p = {m_full.f_pvalue:.4f}")
    print()

    # Coefficients
    print(f"  {'Predictor':<46} {'β':>8} {'SE':>8} {'p':>8}  Sig")
    print(f"  {'─'*80}")
    for pname in m_full.params.index:
        beta = m_full.params[pname]
        se   = m_full.bse[pname]
        pval = m_full.pvalues[pname]
        sig  = ("***" if pval < .001 else "**" if pval < .01
                else "*" if pval < .05 else "ns")
        print(f"  {pname:<46} {beta:>8.4f} {se:>8.4f} {pval:>8.4f}  {sig}")

        coef_rows.append({
            "video":     f"V{v}",
            "predictor": pname,
            "beta":      round(float(beta), 4),
            "SE":        round(float(se),   4),
            "p":         round(float(pval), 4),
            "sig":       sig,
        })

    # Adjusted (LS) means — evaluate at grand mean of covariates
    gad_mean  = float(tmp["gad"].mean())
    stai_mean = float(tmp["stai"].mean())
    print(f"\n  Adjusted means (at GAD={gad_mean:.2f}, STAI={stai_mean:.2f}):")
    adj_means = {}
    for g in GROUP_ORDER:
        pred_df = pd.DataFrame({
            "group": [g],
            "gad":   [gad_mean],
            "stai":  [stai_mean],
        })
        adj = float(m_full.predict(pred_df).iloc[0])
        raw = float(tmp[tmp["group"] == g]["yaw"].mean()) if g in tmp["group"].values else np.nan
        adj_means[g] = adj
        print(f"    {g:<20}: raw M = {raw:6.2f}   adj M = {adj:6.2f}")

    summary_rows.append({
        "video":            f"V{v}",
        "video_name":       VIDEO_NAMES[v],
        "N":                len(tmp),
        "R2_cov_only":      round(m_cov.rsquared, 4),
        "R2_full":          round(m_full.rsquared, 4),
        "delta_R2_group":   round(delta_r2, 4),
        "F":                round(m_full.fvalue, 4),
        "df_model":         int(m_full.df_model),
        "df_resid":         int(m_full.df_resid),
        "p":                round(m_full.f_pvalue, 4),
        "adj_mean_Minimal":         round(adj_means.get("Minimal", np.nan), 3),
        "adj_mean_Mild":            round(adj_means.get("Mild", np.nan), 3),
        "adj_mean_Moderate_Severe": round(adj_means.get("Moderate-Severe", np.nan), 3),
    })

# ── Save results ──────────────────────────────────────────────────────────────
summary_path = f"{OUTPUT_DIR}/report2_ancova.csv"
coef_path    = f"{OUTPUT_DIR}/report2_ancova_coef.csv"
pd.DataFrame(summary_rows).to_csv(summary_path, index=False)
pd.DataFrame(coef_rows).to_csv(coef_path, index=False)
print(f"\n  → Saved: {summary_path}")
print(f"  → Saved: {coef_path}")

# ── Console summary table ─────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  Summary: ANCOVA per video")
print("=" * 65)
print(f"  {'Video':<26} {'R²':>6} {'ΔR²_grp':>9} {'F':>8} {'p':>8}  Sig")
print(f"  {'─'*65}")
for r in summary_rows:
    sig = ("***" if r["p"] < .001 else "**" if r["p"] < .01
           else "*" if r["p"] < .05 else "ns")
    print(f"  {r['video']}: {r['video_name']:<22} {r['R2_full']:>6.4f}"
          f" {r['delta_R2_group']:>9.4f} {r['F']:>8.3f} {r['p']:>8.4f}  {sig}")

print("\nDone — 10_ancova.py")
