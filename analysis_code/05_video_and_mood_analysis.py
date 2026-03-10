"""
05_video_and_mood_analysis.py
PURPOSE : Analyse per-video subjective ratings (valence, arousal, immersion)
          and PANAS mood change (pre vs post VR).
          Methods used: descriptive statistics, paired t-test (PANAS),
          Kruskal-Wallis (group comparisons on video ratings).
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

# ─────────────────────────────────────────────────────────────────────────────
# PART A: Per-video descriptive stats
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("PART A: Per-Video Descriptive Statistics")
print("=" * 65)

video_rows = []
for dim in ["valence", "arousal", "immersion"]:
    print(f"\n  {dim.capitalize()}:")
    print(f"  {'Video':<28} {'Mean':>7} {'SD':>7} {'Median':>8} {'Min':>6} {'Max':>6}")
    print("  " + "-" * 66)
    for i in range(1, 6):
        col = f"{dim}_v{i}"
        s = df[col]
        print(f"  V{i}: {VIDEO_NAMES[i]:<24} {s.mean():>7.2f} {s.std():>7.2f} "
              f"{s.median():>8.2f} {s.min():>6.0f} {s.max():>6.0f}")
        video_rows.append({
            "Dimension": dim, "Video": f"V{i}", "Name": VIDEO_NAMES[i],
            "Mean": round(s.mean(), 3), "SD": round(s.std(), 3),
            "Median": s.median(), "Min": s.min(), "Max": s.max(),
        })

pd.DataFrame(video_rows).to_csv(f"{OUTPUT_DIR}/video_stats.csv", index=False)
print(f"\n  Saved → {OUTPUT_DIR}/video_stats.csv")

# PART B: Valence & Arousal by depression group (Kruskal-Wallis per video)
# Used because PHQ-9 groups violate normality (Shapiro-Wilk p < .05). This matches the approach of Srivastava & Lahane (2025).
print("\n" + "=" * 65)
print("PART B: Valence by Depression Group (Kruskal-Wallis, per video)")
print("=" * 65)
print("  Tests whether depression group affects video valence ratings.")
print("  Used because data violates normality (Shapiro-Wilk p < .05).\n")
print(f"  {'Video':<28} {'H':>8} {'p':>10}  {'Sig':>5}")
print("  " + "-" * 56)
for i in range(1, 6):
    groups = [df[df["depression_group"] == g][f"valence_v{i}"].values
              for g in GROUP_ORDER]
    H, p = stats.kruskal(*groups)
    sig = "*" if p < 0.05 else ""
    print(f"  V{i}: {VIDEO_NAMES[i]:<24} {H:>8.3f} {p:>10.4f}  {sig:>5}")

# PART C: PANAS pre vs post VR (paired t-test)
print("\n" + "=" * 65)
print("PART C: PANAS Mood Change — Pre vs Post VR (Paired t-test)")
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
