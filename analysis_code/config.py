# config.py
# ─────────────────────────────────────────────────────────────────────────────
# Shared configuration for all analysis scripts (Report 1 + Report 2).
# Update DATA_PATH and CSV_DIR to match your local folder layout before running.
# ─────────────────────────────────────────────────────────────────────────────

import os

# ── File Paths ────────────────────────────────────────────────────────────────
DATA_PATH  = "/Users/bharatgen-hyd-202538/Downloads/brsm_s26_project_vr/360_Videos_VR_project/data/data.xlsx"
CSV_DIR    = "/Users/bharatgen-hyd-202538/Downloads/brsm_s26_project_vr/360_Videos_VR_project/data/headtracking-data"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── CSV Column Names ──────────────────────────────────────────────────────────
CSV_TIME_COL    = "Time"
CSV_YAW_SPEED   = "RotationSpeedY"      # primary — matches Srivastava & Lahane 2025
CSV_PITCH_SPEED = "RotationSpeedX"
CSV_ROLL_SPEED  = "RotationSpeedZ"
CSV_TOTAL_SPEED = "RotationSpeedTotal"

# All rotation axes used in Report 2
CSV_AXES = {
    "yaw":   "RotationSpeedY",
    "pitch": "RotationSpeedX",
    "roll":  "RotationSpeedZ",
    "total": "RotationSpeedTotal",
}

# ── PHQ-9 Group Definitions (Kroenke et al. 2001) ────────────────────────────
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

# ── Video Metadata ────────────────────────────────────────────────────────────
VIDEO_NAMES = {
    1: "Abandoned Buildings",
    2: "Evening at Beach",
    3: "Campus",
    4: "The Nun (Horror)",
    5: "Tahiti Surf",
}
VIDEO_SHORT = {
    1: "V1\nAbandoned", 2: "V2\nBeach", 3: "V3\nCampus",
    4: "V4\nHorror",    5: "V5\nSurf",
}
VIDEO_COLORS = ["#5C85D6", "#56B4E9", "#009E73", "#D55E00", "#CC79A7"]

# ── Questionnaire Columns ─────────────────────────────────────────────────────
QUESTIONNAIRE_COLS = {
    "score_phq":    "PHQ-9",
    "score_gad":    "GAD-7",
    "score_stai_t": "STAI-T",
}

# ── Statistical Thresholds ────────────────────────────────────────────────────
ALPHA          = 0.05
ZSCORE_THRESH  = 2.5
IQR_MULTIPLIER = 1.5
