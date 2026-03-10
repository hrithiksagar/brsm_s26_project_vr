# =============================================================================
# 06_head_tracking_analysis.py   [Report 1 — descriptive head-tracking]
# =============================================================================
# PURPOSE:
#   Load every participant's head-tracking CSV for each of the 5 videos,
#   compute per-participant × per-video summary metrics, and run
#   descriptive + basic inferential statistics (Kruskal-Wallis, Spearman).
#
# PRIMARY METRIC: mean RotationSpeedY  (yaw angular speed, deg/s)
#   This matches the "head scanning speed" metric of Srivastava & Lahane (2025).
#
# FOLDER STRUCTURE EXPECTED:
#   <HEADTRACK_DIR>/
#       v1/  data_video1_*.csv   (one file per participant)
#       v2/  data_video2_*.csv
#       v3/  data_video3_*.csv
#       v4/  data_video4_*.csv
#       v5/  data_video5_*.csv
#
# CSV FORMAT:
#   Columns: Time, PositionChangeX/Y/Z, RotationChangeX/Y/Z,
#            RotationSpeedX, RotationSpeedY, RotationSpeedZ, RotationSpeedTotal
#   Last row: "Circular Averages,..." — skipped automatically.
#
# OUTPUTS:
#   outputs/headtrack_summary.csv     — one row per participant per video
#   outputs/headtrack_group_stats.csv — group-level means & SDs
#   outputs/fig5_headtracking.png     — Figure 5
# =============================================================================

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats

from config import (DATA_PATH, OUTPUT_DIR, HEADTRACK_DIR,
                    GROUP_ORDER, GROUP_COLORS, VIDEO_NAMES, VIDEO_COLORS,
                    CSV_TIME_COL, CSV_YAW_SPEED, CSV_TOTAL_SPEED, CSV_PITCH_SPEED)

# ── Load main data ─────────────────────────────────────────────────────────────
df = pd.read_excel(DATA_PATH)

def assign_group(score):
    if score <= 4:  return "Minimal"
    if score <= 9:  return "Mild"
    return "Moderate-Severe"

df["depression_group"] = df["score_phq"].apply(assign_group)

# PART A: Parse CSVs → compute summary metrics

def load_csv(path):
    """Read one head-tracking CSV, skip the trailing summary row."""
    raw = pd.read_csv(path, on_bad_lines="skip")
    raw = raw[pd.to_numeric(raw[CSV_TIME_COL], errors="coerce").notna()].copy()
    for col in raw.columns:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    return raw.dropna(subset=[CSV_YAW_SPEED])


def compute_metrics(path):
    """Return dict of summary metrics for one file, or None if unreadable."""
    try:
        raw = load_csv(path)
        if len(raw) < 10:
            return None
        yaw   = raw[CSV_YAW_SPEED].values
        total = raw[CSV_TOTAL_SPEED].values
        pitch = raw[CSV_PITCH_SPEED].values
        dur   = raw[CSV_TIME_COL].max() - raw[CSV_TIME_COL].min()
        return {
            "duration_s":       round(float(dur), 2),
            "n_frames":         len(raw),
            "mean_yaw_speed":   round(float(np.mean(yaw)),   4),
            "std_yaw_speed":    round(float(np.std(yaw)),    4),
            "median_yaw_speed": round(float(np.median(yaw)), 4),
            "mean_total_speed": round(float(np.mean(total)), 4),
            "mean_pitch_speed": round(float(np.mean(pitch)), 4),
        }
    except Exception as e:
        print(f"  [ERROR] {path}: {e}")
        return None


print("=" * 65)
print("PART A: Loading head-tracking CSVs")
print("=" * 65)

METRIC_KEYS = ["duration_s","n_frames","mean_yaw_speed","std_yaw_speed",
               "median_yaw_speed","mean_total_speed","mean_pitch_speed"]

records = []
for _, row in df.iterrows():
    pid = row["participant"]
    rec = {
        "participant":    pid,
        "depression_group": row["depression_group"],
        "score_phq":      row["score_phq"],
        "score_gad":      row["score_gad"],
        "score_stai_t":   row["score_stai_t"],
    }
    for v in range(1, 6):
        csv_name = row[f"v{v}"]
        # Try sub-folder structure first, then flat fallback
        path = os.path.join(HEADTRACK_DIR, f"v{v}", csv_name)
        if not os.path.exists(path):
            path = os.path.join(HEADTRACK_DIR, csv_name)

        m = compute_metrics(path) if os.path.exists(path) else None
        for k in METRIC_KEYS:
            rec[f"v{v}_{k}"] = m[k] if m else np.nan

    records.append(rec)
    speeds = "  ".join(f"V{v}={rec.get(f'v{v}_mean_yaw_speed', float('nan')):.1f}"
                       for v in range(1, 6))
    print(f"  {pid[-15:]}  |  {speeds}")

speed_df = pd.DataFrame(records)
speed_df.to_csv(f"{OUTPUT_DIR}/headtrack_summary.csv", index=False)
print(f"\n  → Saved: {OUTPUT_DIR}/headtrack_summary.csv  ({len(speed_df)} rows)\n")

# PART B: Descriptive statistics per video
print("=" * 65)
print("PART B: Descriptive Statistics — Yaw Speed per Video")
print("=" * 65)
print(f"\n  {'Video':<28} {'N':>4} {'Mean':>8} {'SD':>8} {'Median':>8} {'Min':>8} {'Max':>8}")
print("  " + "-" * 68)

for v in range(1, 6):
    col = f"v{v}_mean_yaw_speed"
    s = speed_df[col].dropna()
    print(f"  V{v}: {VIDEO_NAMES[v]:<24} {len(s):>4} {s.mean():>8.2f} "
          f"{s.std():>8.2f} {s.median():>8.2f} {s.min():>8.2f} {s.max():>8.2f}")

# Group-level means
print(f"\n  Group means (M ± SD):\n")
print(f"  {'Video':<28} {'Minimal':>15} {'Mild':>15} {'Mod-Severe':>15}")
print("  " + "-" * 73)
group_rows = []
for v in range(1, 6):
    col = f"v{v}_mean_yaw_speed"
    row_out = {"video": f"V{v}", "video_name": VIDEO_NAMES[v]}
    parts = []
    for g in GROUP_ORDER:
        sub = speed_df[speed_df["depression_group"] == g][col].dropna()
        parts.append(f"{sub.mean():.2f} ({sub.std():.2f})")
        row_out[f"{g}_M"] = round(sub.mean(), 3)
        row_out[f"{g}_SD"] = round(sub.std(), 3)
    print(f"  V{v}: {VIDEO_NAMES[v]:<24} " +
          "  ".join(f"{p:>15}" for p in parts))
    group_rows.append(row_out)

pd.DataFrame(group_rows).to_csv(
    f"{OUTPUT_DIR}/headtrack_group_stats.csv", index=False)
print(f"\n  → Saved: {OUTPUT_DIR}/headtrack_group_stats.csv")

# PART C: Kruskal-Wallis — yaw speed across depression groups
print("\n" + "=" * 65)
print("PART C: Kruskal-Wallis H — Yaw Speed by Depression Group")
print("=" * 65)
print("  H0: No difference in yaw speed across Minimal / Mild / Mod-Severe\n")
print(f"  {'Video':<28} {'H':>7} {'p':>9}  {'Sig':>4}  {'Direction'}")
print("  " + "-" * 65)

for v in range(1, 6):
    col = f"v{v}_mean_yaw_speed"
    groups = [speed_df[speed_df["depression_group"] == g][col].dropna().values
              for g in GROUP_ORDER]
    if all(len(g) >= 3 for g in groups):
        H, p = stats.kruskal(*groups)
        sig = "***" if p < .001 else ("**" if p < .01 else ("*" if p < .05 else "ns"))
        means = [g.mean() for g in groups]
        direction = ("Mod-Sev < Minimal" if means[2] < means[0]
                     else "Mod-Sev >= Minimal")
        print(f"  V{v}: {VIDEO_NAMES[v]:<24} {H:>7.3f} {p:>9.4f}  {sig:>4}  {direction}")

# PART D: Spearman — PHQ-9 vs yaw speed
print("\n" + "=" * 65)
print("PART D: Spearman Correlation — PHQ-9 vs Mean Yaw Speed")
print("=" * 65)
print("  (Spearman used because PHQ-9 violates normality, SW p = .002)\n")
print(f"  {'Video':<28} {'rho':>7} {'p':>9}  {'Sig':>4}")
print("  " + "-" * 52)

for v in range(1, 6):
    col = f"v{v}_mean_yaw_speed"
    sub = speed_df[["score_phq", col]].dropna()
    if len(sub) >= 10:
        rho, p = stats.spearmanr(sub["score_phq"], sub[col])
        sig = "***" if p < .001 else ("**" if p < .01 else ("*" if p < .05 else "ns"))
        print(f"  V{v}: {VIDEO_NAMES[v]:<24} {rho:>7.3f} {p:>9.4f}  {sig:>4}")

# PART E: Figure 5
print("\n" + "=" * 65)
print("PART E: Generating Figure 5")
print("=" * 65)

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
})

fig = plt.figure(figsize=(14, 10))
fig.suptitle("Figure 5: Head Scanning Speed (Yaw Angular Velocity) — Descriptive Overview",
             fontsize=14, fontweight="bold")
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.35)

# A: Mean per video bar chart
ax1 = fig.add_subplot(gs[0, 0])
vnames_short = [f"V{v}\n{VIDEO_NAMES[v].split()[0]}" for v in range(1, 6)]
means = [speed_df[f"v{v}_mean_yaw_speed"].mean() for v in range(1, 6)]
sds   = [speed_df[f"v{v}_mean_yaw_speed"].std()  for v in range(1, 6)]
bars  = ax1.bar(range(5), means, yerr=sds, color=VIDEO_COLORS, capsize=4,
                edgecolor="white", width=0.6)
ax1.set_xticks(range(5))
ax1.set_xticklabels(vnames_short, fontsize=9)
ax1.set_title("A. Mean Yaw Speed per Video", fontweight="bold")
ax1.set_ylabel("Yaw Speed (deg/s)")
for bar, m in zip(bars, means):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{m:.1f}", ha="center", va="bottom", fontsize=9)

# B: Boxplot per video
ax2 = fig.add_subplot(gs[0, 1])
data_all = [speed_df[f"v{v}_mean_yaw_speed"].dropna().values for v in range(1, 6)]
bp = ax2.boxplot(data_all, tick_labels=[f"V{v}" for v in range(1, 6)],
                 patch_artist=True, widths=0.5)
for patch, c in zip(bp["boxes"], VIDEO_COLORS):
    patch.set_facecolor(c); patch.set_alpha(0.75)
ax2.set_title("B. Distribution per Video", fontweight="bold")
ax2.set_ylabel("Yaw Speed (deg/s)")

# C: Grouped bars — group means per video
ax3 = fig.add_subplot(gs[1, 0])
x = np.arange(5); w = 0.25
for i, g in enumerate(GROUP_ORDER):
    sub = speed_df[speed_df["depression_group"] == g]
    gm  = [sub[f"v{v}_mean_yaw_speed"].mean() for v in range(1, 6)]
    ax3.bar(x + i*w, gm, w, label=g, color=GROUP_COLORS[g],
            edgecolor="white", alpha=0.85)
ax3.set_xticks(x + w)
ax3.set_xticklabels([f"V{v}" for v in range(1, 6)])
ax3.set_title("C. Mean Yaw Speed by Depression Group", fontweight="bold")
ax3.set_ylabel("Yaw Speed (deg/s)")
ax3.legend(fontsize=9)

# D: PHQ-9 vs yaw speed scatter (V3)
ax4 = fig.add_subplot(gs[1, 1])
for g, c in GROUP_COLORS.items():
    pts = speed_df[speed_df["depression_group"] == g]
    ax4.scatter(pts["score_phq"], pts["v3_mean_yaw_speed"], color=c,
                label=g, alpha=0.75, s=55, edgecolors="white", lw=0.5)
sub = speed_df[["score_phq", "v3_mean_yaw_speed"]].dropna()
m, b = np.polyfit(sub["score_phq"], sub["v3_mean_yaw_speed"], 1)
xfit = np.linspace(0, 19, 100)
rho, p_rho = stats.spearmanr(sub["score_phq"], sub["v3_mean_yaw_speed"])
ax4.plot(xfit, m*xfit + b, "k--", lw=1.5,
         label=f"ρ = {rho:.2f}  (p = {p_rho:.3f})")
ax4.set_title("D. PHQ-9 vs Yaw Speed (V3: Campus)", fontweight="bold")
ax4.set_xlabel("PHQ-9 Score")
ax4.set_ylabel("Mean Yaw Speed (deg/s)")
ax4.legend(fontsize=8)

plt.savefig(f"{OUTPUT_DIR}/fig5_headtracking.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  → Saved: {OUTPUT_DIR}/fig5_headtracking.png")
print("\nDone.")
