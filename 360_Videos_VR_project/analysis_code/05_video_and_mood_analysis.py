"""
05_video_and_mood_analysis.py
PURPOSE : Analyse per-video subjective ratings (valence, arousal, immersion)
          and PANAS mood change (pre vs post VR). Includes Wilcoxon signed-
          rank tests for video comparisons and paired t-tests for PANAS.
OUTPUT  : outputs/video_stats.csv
          Console printout
RUN     : python 05_video_and_mood_analysis.py
"""

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

VIDEO_NAMES = {
    1: "Abandoned Buildings",
    2: "Evening at Beach",
    3: "Campus",
    4: "The Nun (Horror)",
    5: "Tahiti Surf",
}

# PART A: Per-video descriptive stats + Friedman test
print("=" * 65)
print("PART A: Per-Video Descriptive Statistics")
print("=" * 65)

video_rows = []
for dim in ["valence", "arousal", "immersion"]:
    print(f"\n  {dim.capitalize()}:")
    print(f"  {'Video':<28} {'Mean':>7} {'SD':>7} {'Median':>8} {'Min':>6} {'Max':>6}")
    print("  " + "-" * 66)
    vals_all = []
    for i in range(1, 6):
        col = f"{dim}_v{i}"
        s = df[col]
        vals_all.append(s.values)
        print(f"  V{i}: {VIDEO_NAMES[i]:<24} {s.mean():>7.2f} {s.std():>7.2f} "
              f"{s.median():>8.2f} {s.min():>6.0f} {s.max():>6.0f}")
        video_rows.append({
            "Dimension": dim, "Video": f"V{i}", "Name": VIDEO_NAMES[i],
            "Mean": round(s.mean(), 3), "SD": round(s.std(), 3),
            "Median": s.median(), "Min": s.min(), "Max": s.max(),
        })

    # Friedman test — are there differences across all 5 videos?
    F_stat, p = stats.friedmanchisquare(*vals_all)
    sig = "SIGNIFICANT *" if p < 0.05 else "not significant"
    print(f"\n  Friedman test across videos: χ²({5-1}) = {F_stat:.3f}, "
          f"p = {p:.4f}  →  {sig}")

pd.DataFrame(video_rows).to_csv(f"{OUTPUT_DIR}/video_stats.csv", index=False)
print(f"\n  Saved → {OUTPUT_DIR}/video_stats.csv")

# PART B: Pairwise video comparisons (Wilcoxon signed-rank)
print("\n" + "=" * 65)
print("PART B: Pairwise Video Comparisons — Valence (Wilcoxon Signed-Rank)")
print("=" * 65)
print("  Key comparisons of interest:\n")

pairs = [
    (4, 1, "Horror vs Abandoned Buildings"),
    (4, 2, "Horror vs Beach"),
    (4, 3, "Horror vs Campus"),
    (4, 5, "Horror vs Surf"),
    (2, 5, "Beach vs Surf"),
    (1, 3, "Buildings vs Campus"),
]

print(f"  {'Comparison':<35} {'W':>8} {'p':>10}  {'Sig':>5}")
print("  " + "-" * 62)
for v1, v2, label in pairs:
    W, p = stats.wilcoxon(df[f"valence_v{v1}"], df[f"valence_v{v2}"])
    sig = "*" if p < 0.05 else ""
    print(f"  {label:<35} {W:>8.1f} {p:>10.4f}  {sig:>5}")

# Arousal pairwise
print("\n  Key comparisons — Arousal:\n")
for v1, v2, label in [(4, 2, "Horror vs Beach"), (5, 2, "Surf vs Beach"),
                       (4, 3, "Horror vs Campus")]:
    W, p = stats.wilcoxon(df[f"arousal_v{v1}"], df[f"arousal_v{v2}"])
    sig = "*" if p < 0.05 else ""
    print(f"  {label:<35} {W:>8.1f} {p:>10.4f}  {sig:>5}")

# PART C: Valence & Arousal by depression group (Kruskal-Wallis per video)
print("\n" + "=" * 65)
print("PART C: Valence by Depression Group (Kruskal-Wallis, per video)")
print("=" * 65)
print("  Tests whether depression group affects video valence ratings.\n")
print(f"  {'Video':<28} {'H':>8} {'p':>10}  {'Sig':>5}")
print("  " + "-" * 56)
for i in range(1, 6):
    groups = [df[df["depression_group"] == g][f"valence_v{i}"].values
              for g in GROUP_ORDER]
    H, p = stats.kruskal(*groups)
    sig = "*" if p < 0.05 else ""
    print(f"  V{i}: {VIDEO_NAMES[i]:<24} {H:>8.3f} {p:>10.4f}  {sig:>5}")

# PART D: PANAS pre vs post VR (paired t-test)
print("\n" + "=" * 65)
print("PART D: PANAS Mood Change — Pre vs Post VR (Paired t-test)")
print("=" * 65)
print("  WHY t-test? PANAS difference scores passed Shapiro-Wilk (p > .10).\n")

for label, pre_col, post_col in [
    ("Positive Affect", "positive_affect_start", "positive_affect_end"),
    ("Negative Affect", "negative_affect_start", "negative_affect_end"),
]:
    pre  = df[pre_col]
    post = df[post_col]
    diff = post - pre

    # Check normality of difference scores
    W_diff, p_diff = stats.shapiro(diff)
    t, p = stats.ttest_rel(pre, post)

    # Cohen's d for paired data
    d = diff.mean() / diff.std()

    print(f"  {label}")
    print(f"    Pre  : M = {pre.mean():.2f},  SD = {pre.std():.2f}")
    print(f"    Post : M = {post.mean():.2f},  SD = {post.std():.2f}")
    print(f"    Diff : M = {diff.mean():.2f},  SD = {diff.std():.2f}  "
          f"[Normality: W={W_diff:.3f}, p={p_diff:.3f}]")
    print(f"    t({len(df)-1}) = {t:.3f},  p = {p:.4f},  Cohen's d = {d:.3f}")
    sig = "SIGNIFICANT *" if p < 0.05 else "not significant"
    print(f"    → {sig}\n")

# PANAS by depression group
print("  Positive Affect change by depression group:")
print(f"  {'Group':<22} {'Pre M':>8} {'Post M':>8} {'Diff M':>8}")
print("  " + "-" * 52)
for g in GROUP_ORDER:
    sub = df[df["depression_group"] == g]
    pre_m  = sub["positive_affect_start"].mean()
    post_m = sub["positive_affect_end"].mean()
    diff_m = post_m - pre_m
    print(f"  {g:<22} {pre_m:>8.2f} {post_m:>8.2f} {diff_m:>8.2f}")

print("\nDone.")
