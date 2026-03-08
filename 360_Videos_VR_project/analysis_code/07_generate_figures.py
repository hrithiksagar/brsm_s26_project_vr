# =============================================================================
# 07_generate_figures.py
# PURPOSE : Reproduce all 4 publication-quality figures used in Report 1.
#           Run this script to regenerate figures after any data change.
# OUTPUT  : outputs/fig1_demographics.png
#           outputs/fig2_correlations.png
#           outputs/fig3_video_ratings.png
#           outputs/fig4_mood_valence.png
# RUN     : python 07_generate_figures.py
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
from matplotlib.patches import Patch
from config import DATA_PATH, OUTPUT_DIR, GROUP_ORDER, GROUP_COLORS, VIDEO_COLORS

df = pd.read_excel(DATA_PATH)

def assign_phq_group(score):
    if score <= 4:  return "Minimal"
    if score <= 9:  return "Mild"
    return "Moderate-Severe"

df["depression_group"] = df["score_phq"].apply(assign_phq_group)

# ── Shared style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":  "sans-serif",
    "font.size":    11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":    False,
})
palette = GROUP_COLORS

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Demographics & Score Distributions
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Figure 1 ...")
fig = plt.figure(figsize=(14, 10))
fig.suptitle("Figure 1: Participant Demographics and Score Distributions",
             fontsize=14, fontweight="bold", y=1.01)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

# PHQ-9
ax = fig.add_subplot(gs[0, 0])
ax.hist(df["score_phq"], bins=10, color="steelblue", edgecolor="white", lw=0.8)
ax.axvline(df["score_phq"].mean(), color="red", ls="--",
           label=f"M = {df['score_phq'].mean():.1f}")
ax.set_title("PHQ-9 Distribution", fontweight="bold")
ax.set_xlabel("PHQ-9 Score"); ax.set_ylabel("Count"); ax.legend(fontsize=9)

# GAD-7
ax = fig.add_subplot(gs[0, 1])
ax.hist(df["score_gad"], bins=10, color="coral", edgecolor="white", lw=0.8)
ax.axvline(df["score_gad"].mean(), color="darkred", ls="--",
           label=f"M = {df['score_gad'].mean():.1f}")
ax.set_title("GAD-7 Distribution", fontweight="bold")
ax.set_xlabel("GAD-7 Score"); ax.set_ylabel("Count"); ax.legend(fontsize=9)

# STAI-T
ax = fig.add_subplot(gs[0, 2])
ax.hist(df["score_stai_t"], bins=10, color="mediumseagreen", edgecolor="white", lw=0.8)
ax.axvline(df["score_stai_t"].mean(), color="darkgreen", ls="--",
           label=f"M = {df['score_stai_t'].mean():.1f}")
ax.set_title("STAI-T Distribution", fontweight="bold")
ax.set_xlabel("STAI-T Score"); ax.set_ylabel("Count"); ax.legend(fontsize=9)

# Depression groups bar
ax = fig.add_subplot(gs[1, 0])
counts = df["depression_group"].value_counts().reindex(GROUP_ORDER)
bars = ax.bar(counts.index, counts.values,
              color=[palette[g] for g in GROUP_ORDER], edgecolor="white")
for bar, val in zip(bars, counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            str(val), ha="center", va="bottom", fontsize=11)
ax.set_title("Depression Groups (PHQ-9 cut-offs)", fontweight="bold")
ax.set_ylabel("Count"); ax.set_xlabel("Group")

# Gender pie
ax = fig.add_subplot(gs[1, 1])
ax.pie([df["gender"].eq(1).sum(), df["gender"].eq(2).sum()],
       labels=["Male", "Female"], autopct="%1.0f%%",
       colors=["#5C85D6", "#E88E8E"], startangle=90)
ax.set_title("Gender Distribution", fontweight="bold")

# Age histogram
ax = fig.add_subplot(gs[1, 2])
ax.hist(df["age"], bins=8, color="mediumpurple", edgecolor="white", lw=0.8)
ax.set_title("Age Distribution", fontweight="bold")
ax.set_xlabel("Age"); ax.set_ylabel("Count")

path = f"{OUTPUT_DIR}/fig1_demographics.png"
plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
print(f"  Saved → {path}")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Correlations
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Figure 2 ...")
fig = plt.figure(figsize=(14, 10))
fig.suptitle("Figure 2: Score Comparisons Across Depression Groups & Correlations",
             fontsize=14, fontweight="bold")
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

def make_boxplot(ax, col, title, ylabel):
    data = [df[df["depression_group"] == g][col].values for g in GROUP_ORDER]
    bp = ax.boxplot(data, tick_labels=["Minimal", "Mild", "Mod-Sev"],
                    patch_artist=True)
    for patch, g in zip(bp["boxes"], GROUP_ORDER):
        patch.set_facecolor(palette[g]); patch.set_alpha(0.7)
    ax.set_title(title, fontweight="bold"); ax.set_ylabel(ylabel)

make_boxplot(fig.add_subplot(gs[0, 0]), "score_gad",
             "GAD-7 by Depression Group", "GAD-7 Score")
make_boxplot(fig.add_subplot(gs[0, 1]), "score_stai_t",
             "STAI-T by Depression Group", "STAI-T Score")

xfit = np.linspace(0, 20, 100)
def scatter_with_reg(ax, xcol, ycol, xlabel, ylabel, title):
    for g, c in palette.items():
        sub = df[df["depression_group"] == g]
        ax.scatter(sub[xcol], sub[ycol], color=c, label=g, alpha=0.7, s=50)
    m, b, r, p, _ = stats.linregress(df[xcol], df[ycol])
    ax.plot(xfit, m*xfit+b, "k--", lw=1.5,
            label=f"r = {r:.2f}, p < .001")
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.legend(fontsize=7)

scatter_with_reg(fig.add_subplot(gs[0, 2]),
                 "score_phq", "score_gad", "PHQ-9", "GAD-7", "PHQ-9 vs GAD-7")
scatter_with_reg(fig.add_subplot(gs[1, 0]),
                 "score_phq", "score_stai_t", "PHQ-9", "STAI-T", "PHQ-9 vs STAI-T")

# Correlation heatmap
ax = fig.add_subplot(gs[1, 1:])
corr_cols = ["score_phq","score_gad","score_stai_t",
             "positive_affect_start","negative_affect_start",
             "positive_affect_end","negative_affect_end"]
labels = ["PHQ-9","GAD-7","STAI-T","PA-Pre","NA-Pre","PA-Post","NA-Post"]
corr_mat = df[corr_cols].corr()
corr_mat.index = labels; corr_mat.columns = labels
mask = np.triu(np.ones_like(corr_mat, dtype=bool))
sns.heatmap(corr_mat, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
            center=0, ax=ax, annot_kws={"size": 9}, cbar_kws={"shrink": 0.8})
ax.set_title("Spearman Correlation Matrix", fontweight="bold")

path = f"{OUTPUT_DIR}/fig2_correlations.png"
plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
print(f"  Saved → {path}")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Per-video ratings
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Figure 3 ...")
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
fig.suptitle("Figure 3: Per-Video Subjective Ratings (Valence, Arousal, Immersion)",
             fontsize=13, fontweight="bold")

dims = [("valence",   "Mean Valence (1–9)",    0, 10),
        ("arousal",   "Mean Arousal (1–9)",     0, 10),
        ("immersion", "Mean Immersion Score",   0, 42)]

for ax, (dim, ylabel, ymin, ymax) in zip(axes, dims):
    means = [df[f"{dim}_v{i}"].mean() for i in range(1, 6)]
    sds   = [df[f"{dim}_v{i}"].std()  for i in range(1, 6)]
    ax.bar(range(1, 6), means, yerr=sds, color=VIDEO_COLORS,
           capsize=4, edgecolor="white")
    ax.set_xticks(range(1, 6))
    ax.set_xticklabels([f"V{i}" for i in range(1, 6)])
    ax.set_title(ylabel, fontweight="bold")
    ax.set_xlabel("Video"); ax.set_ylabel(ylabel)
    ax.set_ylim(ymin, ymax)
    if dim == "valence":
        ax.axhline(5, color="gray", ls=":", alpha=0.5, label="Neutral = 5")
        ax.legend(fontsize=8)

plt.tight_layout()
path = f"{OUTPUT_DIR}/fig3_video_ratings.png"
plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
print(f"  Saved → {path}")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — PANAS mood shift + valence by group
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Figure 4 ...")
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
fig.suptitle("Figure 4: Mood (PANAS) Shift & Valence Ratings by Depression Group",
             fontsize=13, fontweight="bold")

x = np.arange(len(GROUP_ORDER)); w = 0.35

def grouped_bar(ax, pre_col, post_col, title, pre_color, post_color):
    pre_m  = df.groupby("depression_group")[pre_col].mean().reindex(GROUP_ORDER)
    post_m = df.groupby("depression_group")[post_col].mean().reindex(GROUP_ORDER)
    ax.bar(x - w/2, pre_m,  w, label="Before VR", color=pre_color,  edgecolor="white")
    ax.bar(x + w/2, post_m, w, label="After VR",  color=post_color, edgecolor="white")
    ax.set_title(title, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(["Min","Mild","Mod-Sev"], fontsize=9)
    ax.set_ylabel("PANAS Score"); ax.legend(fontsize=9)

grouped_bar(axes[0], "positive_affect_start", "positive_affect_end",
            "Positive Affect: Before vs After", "#56B4E9", "#009E73")
grouped_bar(axes[1], "negative_affect_start", "negative_affect_end",
            "Negative Affect: Before vs After", "#E69F00", "#D55E00")

# V4 vs V2 valence by group
pos = [1, 2, 3]
v4_by_group = [df[df["depression_group"] == g]["valence_v4"].values for g in GROUP_ORDER]
v2_by_group = [df[df["depression_group"] == g]["valence_v2"].values for g in GROUP_ORDER]
bp1 = axes[2].boxplot(v4_by_group, positions=[p - 0.2 for p in pos],
                       widths=0.35, patch_artist=True,
                       boxprops=dict(facecolor="#D55E00", alpha=0.7))
bp2 = axes[2].boxplot(v2_by_group, positions=[p + 0.2 for p in pos],
                       widths=0.35, patch_artist=True,
                       boxprops=dict(facecolor="#56B4E9", alpha=0.7))
axes[2].set_title("Valence: Horror (V4) vs Beach (V2)", fontweight="bold")
axes[2].set_xticks(pos)
axes[2].set_xticklabels(["Min","Mild","Mod-Sev"], fontsize=9)
axes[2].set_ylabel("Valence Score")
axes[2].legend([Patch(facecolor="#D55E00", alpha=0.7),
                Patch(facecolor="#56B4E9", alpha=0.7)],
               ["V4: Horror", "V2: Beach"], fontsize=9)

plt.tight_layout()
path = f"{OUTPUT_DIR}/fig4_mood_valence.png"
plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
print(f"  Saved → {path}")

print("\nAll figures saved to outputs/")
