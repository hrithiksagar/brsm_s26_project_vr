"""
01_data_exploration.py
PURPOSE : Load data.xlsx, print an overview of every column, check for
          missing values, and summarise the sample demographics.
OUTPUT  : Console printout (no figures saved)
RUN     : python 01_data_exploration.py
"""
import pandas as pd
import numpy as np
from config import DATA_PATH, QUESTIONNAIRE_COLS

df = pd.read_excel(DATA_PATH)
print("=" * 65)
print(f"Dataset loaded:  {df.shape[0]} rows  x  {df.shape[1]} columns")
print("=" * 65)

# ── 2. Column overview 
print("\n── Column names & dtypes ──")
print(df.dtypes.to_string())

# ── 3. Missing values 
missing = df.isnull().sum()
missing = missing[missing > 0]
print("\n── Missing values ──")
if missing.empty:
    print("  No missing values found in key columns.")
else:
    print(missing.to_string())

# ── 4. Demographics ──
print("\n── Demographics ──")
print(f"  N               : {len(df)}")
print(f"  Age             : M={df['age'].mean():.2f}, SD={df['age'].std():.2f}, "
      f"range {df['age'].min()}–{df['age'].max()}")

gender_map = {1: "Male", 2: "Female", 3: "Other"}
gender_counts = df['gender'].map(gender_map).value_counts()
print(f"  Gender          : {dict(gender_counts)}")

vr_map = {1: "No prior VR experience", 2: "Some VR experience"}
vr_counts = df['vr_experience'].map(vr_map).value_counts()
print(f"  VR Experience   : {dict(vr_counts)}")

# ── 5. Questionnaire score ranges ────────────────────────────────────────────
print("\n── Questionnaire Scores ──")
for col, label in QUESTIONNAIRE_COLS.items():
    s = df[col]
    print(f"  {label:10s}: M={s.mean():.2f}, SD={s.std():.2f}, "
          f"min={s.min():.0f}, max={s.max():.0f}, "
          f"median={s.median():.1f}")

# ── 6. Per-video ratings snapshot ────────────────────────────────────────────
print("\n── Per-Video Mean Ratings ──")
print(f"  {'Video':<6} {'Valence':>10} {'Arousal':>10} {'Immersion':>12}")
for i in range(1, 6):
    v = df[f'valence_v{i}'].mean()
    a = df[f'arousal_v{i}'].mean()
    im = df[f'immersion_v{i}'].mean()
    print(f"  V{i:<5} {v:>10.2f} {a:>10.2f} {im:>12.2f}")

# ── 7. PANAS snapshot 
print("\n── PANAS Mood (Pre vs Post VR) ──")
for label, col in [("Positive Pre ", "positive_affect_start"),
                   ("Positive Post", "positive_affect_end"),
                   ("Negative Pre ", "negative_affect_start"),
                   ("Negative Post", "negative_affect_end")]:
    print(f"  {label}: M={df[col].mean():.2f}, SD={df[col].std():.2f}")

print("\n── Head-Tracking CSV filenames (first 3 participants, V1) ──")
print(df['v1'].head(3).tolist())
print("  (These CSVs need to be placed in the head_tracking_csvs/ folder)")

print("\nDone.")
