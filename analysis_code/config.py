# config.py
import os

# ── File Paths 
DATA_PATH     = "/Users/bharatgen-hyd-202538/Downloads/brsm_s26_project_vr/360 Videos VR project/data/data.xlsx"

# Head-tracking CSVs organised in per-video sub-folders:
#   headtracking-data/v1/data_video1_<ts>.csv
#   headtracking-data/v2/data_video2_<ts>.csv  ... v5
HEADTRACK_DIR = "/Users/bharatgen-hyd-202538/Downloads/brsm_s26_project_vr/360 Videos VR project/data/headtracking-data"
OUTPUT_DIR    = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

"""
── CSV Column Names 
Pre-computed per-frame columns present in every head-tracking CSV:
  Time               – seconds since session start
  RotationChangeY    – cumulative yaw (deg); positive = right
  RotationSpeedY     – instantaneous yaw angular speed (deg/s)  ← PRIMARY
  RotationSpeedTotal – magnitude of full 3-D rotation speed (deg/s)
  RotationSpeedX     – pitch speed (up/down)
  RotationSpeedZ     – roll speed (tilt)
"""
CSV_TIME_COL    = "Time"
CSV_YAW_SPEED   = "RotationSpeedY"     # primary metric (Srivastava & Lahane 2025)
CSV_TOTAL_SPEED = "RotationSpeedTotal"
CSV_PITCH_SPEED = "RotationSpeedX"
CSV_ROLL_SPEED  = "RotationSpeedZ"

# ── PHQ-9 Group Definitions 
# Kroenke et al. (2001) cut-offs
PHQ_GROUPS = {
    "Minimal":         (0,  4),
    "Mild":            (5,  9),
    "Moderate-Severe": (10, 27),
}
GROUP_ORDER  = ["Minimal", "Mild", "Moderate-Severe"]
GROUP_COLORS = {
    "Minimal":         "#2196F3",
    "Mild":            "#FF9800",
    "Moderate-Severe": "#F44336",
}

# ── Video Metadata 
VIDEO_NAMES = {
    1: "Abandoned Buildings",
    2: "Evening at Beach",
    3: "Campus",
    4: "The Nun (Horror)",
    5: "Tahiti Surf",
}
VIDEO_COLORS = ["#5C85D6", "#56B4E9", "#009E73", "#D55E00", "#CC79A7"]

# ── Questionnaire Columns 
QUESTIONNAIRE_COLS = {
    "score_phq":    "PHQ-9",
    "score_gad":    "GAD-7",
    "score_stai_t": "STAI-T",
}

# ── Statistical Thresholds 
ALPHA          = 0.05
ZSCORE_THRESH  = 2.5
IQR_MULTIPLIER = 1.5
