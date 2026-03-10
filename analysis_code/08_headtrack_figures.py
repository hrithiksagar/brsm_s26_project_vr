"""
08_headtrack_figures.py
PURPOSE : Generate figures for head-tracking analysis (Report 2).
          Requires outputs/headtrack_summary.csv to exist first.
          Run 06_head_tracking_analysis.py before this script.
OUTPUT  : outputs/fig5_speed_by_group.png
          outputs/fig6_speed_by_video.png
          outputs/fig7_phq_vs_speed.png
RUN     : python 08_headtrack_figures.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
from config import OUTPUT_DIR, GROUP_ORDER, GROUP_COLORS, VIDEO_COLORS

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size":   11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

summary_path = f"{OUTPUT_DIR}/headtrack_summary.csv"
try:
    speed_df = pd.read_csv(summary_path)
except FileNotFoundError:
    print(f"ERROR: {summary_path} not found.")
    print("Run 06_head_tracking_analysis.py first.")
    exit(1)

palette = GROUP_COLORS
VIDEO_NICE = ["Abandoned\nBuildings", "Evening\nat Beach", "Campus",
              "The Nun\n(Horror)", "Tahiti\nSurf"]

# FIGURE 5 — Scanning speed by depression group (boxplot per video)
print("Generating Figure 5 ...")
fig, axes = plt.subplots(1, 5, figsize=(16, 5), sharey=False)
fig.suptitle("Figure 5: Head Scanning Speed (deg/s) by Depression Group per Video",
             fontsize=13, fontweight="bold")

for i, ax in enumerate(axes, 1):
    col = f"v{i}_mean_yaw_speed"
    data_per_group = [speed_df[speed_df["depression_group"] == g][col].dropna().values
                      for g in GROUP_ORDER]
    bp = ax.boxplot(data_per_group, tick_labels=["Min","Mild","Mod-Sev"],
                    patch_artist=True, widths=0.5)
    for patch, g in zip(bp["boxes"], GROUP_ORDER):
        patch.set_facecolor(palette[g]); patch.set_alpha(0.75)
    ax.set_title(f"V{i}: {VIDEO_NICE[i-1]}", fontweight="bold", fontsize=10)
    ax.set_ylabel("Scanning Speed (deg/s)" if i == 1 else "")
    ax.set_xlabel("")

    # Add mean markers
    for j, grp_data in enumerate(data_per_group, 1):
        if len(grp_data) > 0:
            ax.scatter(j, np.mean(grp_data), color="black", s=40, zorder=5,
                       marker="D")

plt.tight_layout()
path = f"{OUTPUT_DIR}/fig5_speed_by_group.png"
plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
print(f"  Saved → {path}")

# FIGURE 6 — Mean speed per video (bar) + breakdown by depression group
print("Generating Figure 6 ...")
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Figure 6: Head Scanning Speed — Video and Group Overview",
             fontsize=13, fontweight="bold")

# Panel A: mean speed per video
means = [speed_df[f"v{i}_mean_yaw_speed"].mean() for i in range(1,6)]
sds   = [speed_df[f"v{i}_mean_yaw_speed"].std()  for i in range(1,6)]
axes[0].bar(range(1, 6), means, yerr=sds, color=VIDEO_COLORS,
            capsize=5, edgecolor="white")
axes[0].set_xticks(range(1, 6))
axes[0].set_xticklabels([f"V{i}" for i in range(1, 6)])
axes[0].set_title("Mean Scanning Speed per Video", fontweight="bold")
axes[0].set_ylabel("RotationSpeedTotal (deg/s)")
axes[0].set_xlabel("Video")

# Panel B: mean speed per group per video (line plot)
for g, color in palette.items():
    group_means = [speed_df[speed_df["depression_group"] == g]
                   [f"v{i}_mean_yaw_speed"].mean()
                   for i in range(1, 6)]
    axes[1].plot(range(1, 6), group_means, marker="o", color=color,
                 label=g, linewidth=2, markersize=7)

axes[1].set_xticks(range(1, 6))
axes[1].set_xticklabels([f"V{i}" for i in range(1, 6)])
axes[1].set_title("Scanning Speed per Group × Video", fontweight="bold")
axes[1].set_ylabel("Mean Scanning Speed (deg/s)")
axes[1].set_xlabel("Video")
axes[1].legend(title="Depression Group", fontsize=9)

plt.tight_layout()
path = f"{OUTPUT_DIR}/fig6_speed_by_video.png"
plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
print(f"  Saved → {path}")

# FIGURE 7 — PHQ-9 vs scanning speed scatter (one panel per video)
print("Generating Figure 7 ...")
fig, axes = plt.subplots(1, 5, figsize=(16, 4), sharey=False)
fig.suptitle("Figure 7: PHQ-9 Score vs Head Scanning Speed per Video",
             fontsize=13, fontweight="bold")

for i, ax in enumerate(axes, 1):
    col = f"v{i}_mean_yaw_speed"
    sub = speed_df[["score_phq","depression_group",col]].dropna()

    for g, c in palette.items():
        mask = sub["depression_group"] == g
        ax.scatter(sub[mask]["score_phq"], sub[mask][col],
                   color=c, alpha=0.7, s=45, label=g)

    # Regression line
    m, b, r, p, _ = stats.linregress(sub["score_phq"], sub[col])
    xfit = np.linspace(sub["score_phq"].min(), sub["score_phq"].max(), 100)
    p_str = f"{p:.3f}" if p >= 0.001 else "<.001"
    ax.plot(xfit, m*xfit+b, "k--", lw=1.5,
            label=f"r={r:.2f}\np={p_str}")

    ax.set_title(f"V{i}: {VIDEO_NICE[i-1]}", fontweight="bold", fontsize=10)
    ax.set_xlabel("PHQ-9 Score")
    ax.set_ylabel("Speed (deg/s)" if i == 1 else "")
    ax.legend(fontsize=7, loc="upper right")

plt.tight_layout()
path = f"{OUTPUT_DIR}/fig7_phq_vs_speed.png"
plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
print(f"  Saved → {path}")

print("\nAll head-tracking figures saved to outputs/")
