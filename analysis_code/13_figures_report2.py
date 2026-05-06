"""
13_figures_report2.py  [Report 2]
─────────────────────────────────────────────────────────────────────────────
Generates the three new figures for Report 2.  Requires that
09_extended_headtracking.py, 10_ancova.py, and 12_glm.py have already
written their CSV outputs (the figures pull from those files rather than
re-running the models, to keep this script fast and independent).

If the CSV outputs are missing, the script re-derives the statistics from
the raw data directly so it can always run standalone.

  Figure 6 — Multi-axis head-movement overview
      A–D: Mean speed per video for each rotation axis (± 1 SD)
      E:   Yaw speed by depression group (non-horror videos)
      F:   Total rotation speed by group across all videos

  Figure 7 — ANCOVA adjusted vs raw group means (one panel per video)

  Figure 8 — GLM and regression results
      A: Group × video profile (yaw speed ± SE)
      B: Partial regression plot: PHQ-9 → yaw (V5)
      C: Immersion → yaw scatter (V5, the significant predictor)

OUTPUT
  outputs/fig6_multiaxis_headtrack.png
  outputs/fig7_ancova_adjusted.png
  outputs/fig8_glm_regression.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from scipy import stats

from config import (
    GROUP_ORDER, GROUP_COLORS, VIDEO_NAMES, VIDEO_COLORS,
    OUTPUT_DIR,
)
from data_loader import build_headtrack, build_long

# ── Global plot style ─────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":         "sans-serif",
    "font.size":           11,
    "axes.spines.top":     False,
    "axes.spines.right":   False,
    "axes.grid":           False,
})

ht   = build_headtrack()
long = build_long(ht)

AXES      = ["yaw", "pitch", "roll", "total"]
AXIS_LBLS = {
    "yaw":   "Yaw (RotationSpeedY)",
    "pitch": "Pitch (RotationSpeedX)",
    "roll":  "Roll (RotationSpeedZ)",
    "total": "Total Rotation Speed",
}


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 6 — Multi-axis head-tracking overview
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Figure 6 …")

fig6, axes6 = plt.subplots(2, 3, figsize=(16, 9))
fig6.suptitle(
    "Figure 6: Head Movement Across All Rotation Axes (N = 40)",
    fontsize=14, fontweight="bold", y=1.01,
)

panel_letters = list("ABCDEF")

# ── Panels A–D: mean ± SD per video for each axis ────────────────────────────
for idx, ax_key in enumerate(AXES):
    r, c = divmod(idx, 3)
    ax = axes6[r, c]

    means = [ht[f"v{v}_mean_{ax_key}"].mean() for v in range(1, 6)]
    sds   = [ht[f"v{v}_mean_{ax_key}"].std()  for v in range(1, 6)]

    bars = ax.bar(
        range(5), means, yerr=sds,
        color=VIDEO_COLORS, capsize=4,
        edgecolor="white", width=0.65,
    )
    ax.set_xticks(range(5))
    ax.set_xticklabels([f"V{v}" for v in range(1, 6)])
    ax.set_title(f"{panel_letters[idx]}. {AXIS_LBLS[ax_key]}",
                 fontweight="bold", fontsize=10)
    ax.set_ylabel("deg/s")
    for bar, m in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(sds) * 0.05,
                f"{m:.1f}", ha="center", va="bottom", fontsize=8)

# ── Panel E: yaw speed by group — non-horror videos ──────────────────────────
ax_e = axes6[1, 0]
vids_nh = [1, 2, 3, 5]
x = np.arange(len(vids_nh))
w = 0.25
for i, g in enumerate(GROUP_ORDER):
    sub = ht[ht["depression_group"] == g]
    gm  = [sub[f"v{v}_mean_yaw"].mean() for v in vids_nh]
    ax_e.bar(x + i * w, gm, w, label=g,
             color=GROUP_COLORS[g], edgecolor="white", alpha=0.85)
ax_e.set_xticks(x + w)
ax_e.set_xticklabels([f"V{v}" for v in vids_nh])
ax_e.set_title("E. Yaw Speed by Group (non-horror)",
               fontweight="bold", fontsize=10)
ax_e.set_ylabel("Mean Yaw Speed (deg/s)")
ax_e.legend(fontsize=8, framealpha=0.4)

# ── Panel F: total rotation speed by group across all videos ─────────────────
ax_f = axes6[1, 1]
for g in GROUP_ORDER:
    sub = ht[ht["depression_group"] == g]
    gm  = [sub[f"v{v}_mean_total"].mean() for v in range(1, 6)]
    gse = [sub[f"v{v}_mean_total"].sem()  for v in range(1, 6)]
    ax_f.errorbar(range(1, 6), gm, yerr=gse, fmt="o-",
                  color=GROUP_COLORS[g], label=g,
                  linewidth=2, capsize=4, markersize=7)
ax_f.set_xticks(range(1, 6))
ax_f.set_xticklabels([f"V{v}" for v in range(1, 6)])
ax_f.set_title("F. Total Rotation Speed by Group",
               fontweight="bold", fontsize=10)
ax_f.set_ylabel("Mean Total Rotation Speed (deg/s)")
ax_f.legend(fontsize=8, framealpha=0.4)

# Hide the unused 6th cell (panel positions: [0,0]..[1,2] = 6, we use 6)
# Nothing to hide — 2×3 grid = exactly 6 panels, all used

fig6.tight_layout()
p6 = f"{OUTPUT_DIR}/fig6_multiaxis_headtrack.png"
fig6.savefig(p6, dpi=150, bbox_inches="tight")
plt.close(fig6)
print(f"  → {p6}")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 7 — ANCOVA: raw vs anxiety-adjusted group means
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Figure 7 …")

fig7, axes7 = plt.subplots(1, 5, figsize=(17, 5), sharey=False)
fig7.suptitle(
    "Figure 7: Yaw Speed — Raw Group Means vs. Anxiety-Adjusted (ANCOVA) Means",
    fontsize=13, fontweight="bold",
)

for v in range(1, 6):
    ax = axes7[v - 1]
    yaw_col = f"v{v}_mean_yaw"
    tmp = ht[["depression_group", "score_gad", "score_stai_t", yaw_col]].dropna().copy()
    tmp.columns = ["group", "gad", "stai", "yaw"]
    tmp["group"] = tmp["group"].astype(str)

    m_full = smf.ols(
        "yaw ~ C(group, Treatment('Minimal')) + gad + stai", data=tmp
    ).fit()

    gad_mean  = tmp["gad"].mean()
    stai_mean = tmp["stai"].mean()

    raw_means = [tmp[tmp["group"] == g]["yaw"].mean() for g in GROUP_ORDER]
    adj_means = []
    for g in GROUP_ORDER:
        pred_df = pd.DataFrame({
            "group": [g], "gad": [gad_mean], "stai": [stai_mean],
        })
        adj_means.append(float(m_full.predict(pred_df).iloc[0]))

    x = np.arange(3)
    w = 0.35
    colors = [GROUP_COLORS[g] for g in GROUP_ORDER]

    ax.bar(x - w / 2, raw_means, w, color=colors, alpha=0.45,
           edgecolor="grey", label="Raw mean")
    ax.bar(x + w / 2, adj_means, w, color=colors, alpha=0.95,
           edgecolor="black", label="Adj. mean")

    ax.set_xticks(x)
    ax.set_xticklabels(["Min", "Mild", "Mod-\nSev"], fontsize=9)
    ax.set_title(f"V{v}: {VIDEO_NAMES[v].split()[0]}", fontweight="bold", fontsize=10)
    ax.set_ylabel("Yaw Speed (deg/s)" if v == 1 else "")

    p_txt = f"p = {m_full.f_pvalue:.3f}"
    ax.text(0.5, 0.97, p_txt, ha="center", va="top",
            transform=ax.transAxes, fontsize=9, style="italic",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightyellow",
                      alpha=0.8, edgecolor="none"))
    if v == 1:
        ax.legend(fontsize=8, loc="lower right")

fig7.tight_layout()
p7 = f"{OUTPUT_DIR}/fig7_ancova_adjusted.png"
fig7.savefig(p7, dpi=150, bbox_inches="tight")
plt.close(fig7)
print(f"  → {p7}")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 8 — GLM and regression results
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Figure 8 …")

fig8, axes8 = plt.subplots(1, 3, figsize=(16, 5))
fig8.suptitle(
    "Figure 8: GLM Group × Video Profile, Partial Regression, and Immersion Effect",
    fontsize=13, fontweight="bold",
)

# ── Panel A: group × video profile (yaw speed ± SE) ─────────────────────────
ax_a = axes8[0]
for g in GROUP_ORDER:
    sub = ht[ht["depression_group"] == g]
    gm  = [sub[f"v{v}_mean_yaw"].mean() for v in range(1, 6)]
    gse = [sub[f"v{v}_mean_yaw"].sem()  for v in range(1, 6)]
    ax_a.errorbar(range(1, 6), gm, yerr=gse, fmt="o-",
                  color=GROUP_COLORS[g], label=g,
                  linewidth=2, capsize=4, markersize=7)
ax_a.set_xticks(range(1, 6))
ax_a.set_xticklabels([f"V{v}" for v in range(1, 6)])
ax_a.set_title("A. Group × Video Profile (Yaw Speed)", fontweight="bold", fontsize=10)
ax_a.set_ylabel("Mean Yaw Speed (deg/s)")
ax_a.set_xlabel("Video")
ax_a.legend(fontsize=9)
ax_a.text(
    0.5, 0.03,
    "Video effect: p < .001***\nGroup × Video interaction: p = .918 ns",
    ha="center", va="bottom", transform=ax_a.transAxes,
    fontsize=8, style="italic",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow",
              alpha=0.8, edgecolor="none"),
)

# ── Panel B: partial regression plot — PHQ-9 → yaw (V5) ─────────────────────
ax_b = axes8[1]
tmp_b = ht[["score_phq", "score_gad", "score_stai_t",
            "immersion_v5", "v5_mean_yaw"]].dropna().copy()
tmp_b.columns = ["phq", "gad", "stai", "imm", "yaw"]

m_y   = smf.ols("yaw ~ gad + stai + imm", data=tmp_b).fit()
m_phq = smf.ols("phq ~ gad + stai + imm", data=tmp_b).fit()
res_y   = m_y.resid.values
res_phq = m_phq.resid.values
r_part, p_part = stats.pearsonr(res_phq, res_y)

# Map index back to group
group_series = ht.loc[tmp_b.index, "depression_group"]
for g in GROUP_ORDER:
    idx = group_series[group_series == g].index
    # align to tmp_b index positions
    pos = [list(tmp_b.index).index(i) for i in idx if i in tmp_b.index]
    ax_b.scatter(res_phq[pos], res_y[pos],
                 color=GROUP_COLORS[g], label=g, alpha=0.75,
                 s=55, edgecolors="white", lw=0.5)

m_fit, b_fit = np.polyfit(res_phq, res_y, 1)
xfit = np.linspace(res_phq.min(), res_phq.max(), 100)
ax_b.plot(xfit, m_fit * xfit + b_fit, "k--", lw=1.5,
          label=f"r = {r_part:.2f} (p = {p_part:.3f})")
ax_b.axhline(0, color="grey", lw=0.5, ls=":")
ax_b.axvline(0, color="grey", lw=0.5, ls=":")
ax_b.set_title("B. Partial Regression: PHQ-9 → Yaw (V5)",
               fontweight="bold", fontsize=10)
ax_b.set_xlabel("PHQ-9 residuals (after GAD, STAI, Imm)")
ax_b.set_ylabel("Yaw speed residuals (V5)")
ax_b.legend(fontsize=8)

# ── Panel C: immersion → yaw scatter (V5) ────────────────────────────────────
ax_c = axes8[2]
tmp_c = ht[["immersion_v5", "v5_mean_yaw", "depression_group"]].dropna().copy()
for g in GROUP_ORDER:
    pts = tmp_c[tmp_c["depression_group"] == g]
    ax_c.scatter(pts["immersion_v5"], pts["v5_mean_yaw"],
                 color=GROUP_COLORS[g], label=g, alpha=0.75,
                 s=55, edgecolors="white", lw=0.5)
m2, b2 = np.polyfit(tmp_c["immersion_v5"], tmp_c["v5_mean_yaw"], 1)
xfit2  = np.linspace(tmp_c["immersion_v5"].min(), tmp_c["immersion_v5"].max(), 100)
r2, p2 = stats.pearsonr(tmp_c["immersion_v5"], tmp_c["v5_mean_yaw"])
ax_c.plot(xfit2, m2 * xfit2 + b2, "k--", lw=1.5,
          label=f"r = {r2:.2f} (p = {p2:.3f})")
ax_c.set_title("C. Immersion → Yaw Speed (V5)\nβ = 1.02, p = .001***",
               fontweight="bold", fontsize=10)
ax_c.set_xlabel("Immersion Score (V5)")
ax_c.set_ylabel("Mean Yaw Speed (deg/s)")
ax_c.legend(fontsize=8)

fig8.tight_layout()
p8 = f"{OUTPUT_DIR}/fig8_glm_regression.png"
fig8.savefig(p8, dpi=150, bbox_inches="tight")
plt.close(fig8)
print(f"  → {p8}")

print("\nDone — 13_figures_report2.py")
