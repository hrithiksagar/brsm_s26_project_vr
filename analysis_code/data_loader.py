"""
data_loader.py  — shared data loading utilities (Report 1 + Report 2)
─────────────────────────────────────────────────────────────────────
Provides two public functions:
  load_survey()       → pd.DataFrame  (40 rows, all questionnaire columns)
  build_headtrack()   → pd.DataFrame  (40 rows, wide: per-participant × per-video metrics)

The head-tracking CSVs are located either in flat or sub-folder layout:
  Flat:       <CSV_DIR>/data_video1_<ts>.csv
  Sub-folder: <CSV_DIR>/v1/data_video1_<ts>.csv
build_headtrack() tries sub-folder first, then flat fallback.
"""

import os
import pandas as pd
import numpy as np

from config import (
    DATA_PATH, CSV_DIR, CSV_AXES, CSV_TIME_COL,
    GROUP_ORDER, PHQ_GROUPS,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def assign_group(phq_score: float) -> str:
    """Map a PHQ-9 score to a depression-severity group label."""
    if phq_score <= 4:
        return "Minimal"
    if phq_score <= 9:
        return "Mild"
    return "Moderate-Severe"


def _parse_csv(path: str) -> pd.DataFrame | None:
    """
    Read one head-tracking CSV file.
    Drops any trailing summary row (e.g. 'Circular Averages,...').
    Returns a clean DataFrame or None if the file is too short / unreadable.
    """
    try:
        raw = pd.read_csv(path, on_bad_lines="skip")
        # Keep only rows where Time is numeric (drops the 'Circular Averages' footer)
        mask = pd.to_numeric(raw[CSV_TIME_COL], errors="coerce").notna()
        raw = raw[mask].copy()
        for col in raw.columns:
            raw[col] = pd.to_numeric(raw[col], errors="coerce")
        raw = raw.dropna(subset=["RotationSpeedY"])
        return raw if len(raw) >= 10 else None
    except Exception as exc:
        print(f"  [WARN] Could not parse {path}: {exc}")
        return None


def _compute_metrics(path: str) -> dict | None:
    """
    Compute per-participant × per-video summary metrics from one CSV.
    Returns a dict with keys:  mean_{axis}, std_{axis}  for each axis in
    CSV_AXES, plus 'duration_s' and 'n_frames'.
    """
    raw = _parse_csv(path)
    if raw is None:
        return None
    metrics = {}
    for key, col in CSV_AXES.items():
        if col in raw.columns:
            arr = raw[col].dropna().values
            metrics[f"mean_{key}"] = float(np.mean(arr))
            metrics[f"std_{key}"]  = float(np.std(arr))
        else:
            metrics[f"mean_{key}"] = np.nan
            metrics[f"std_{key}"]  = np.nan
    metrics["duration_s"] = float(raw[CSV_TIME_COL].max() - raw[CSV_TIME_COL].min())
    metrics["n_frames"]   = len(raw)
    return metrics


def _resolve_csv_path(video_num: int, csv_filename: str) -> str:
    """
    Return the filesystem path for a head-tracking CSV, trying sub-folder
    layout first then flat fallback.
    """
    sub  = os.path.join(CSV_DIR, f"v{video_num}", csv_filename)
    flat = os.path.join(CSV_DIR, csv_filename)
    if os.path.exists(sub):
        return sub
    if os.path.exists(flat):
        return flat
    return ""   # caller handles missing


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def load_survey() -> pd.DataFrame:
    """
    Load data.xlsx and attach a depression_group column.
    Returns a DataFrame with one row per participant (N = 40).
    """
    df = pd.read_excel(DATA_PATH)
    df["depression_group"] = df["score_phq"].apply(assign_group)
    df["depression_group"] = pd.Categorical(
        df["depression_group"], categories=GROUP_ORDER, ordered=True
    )
    return df


def build_headtrack(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Build a wide-format DataFrame (one row per participant) containing
    per-video head-tracking metrics (mean/SD for yaw, pitch, roll, total)
    alongside key questionnaire scores and subjective ratings.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Output of load_survey(). Loaded automatically if not provided.

    Returns
    -------
    pd.DataFrame
        40 rows × (4 axes × 2 stats × 5 videos + survey columns) columns.
        Column naming pattern: v{1-5}_mean_{axis}, v{1-5}_std_{axis}.
    """
    if df is None:
        df = load_survey()

    records = []
    for _, row in df.iterrows():
        rec: dict = {
            "participant":      row["participant"],
            "depression_group": row["depression_group"],
            "score_phq":        float(row["score_phq"]),
            "score_gad":        float(row["score_gad"]),
            "score_stai_t":     float(row["score_stai_t"]),
        }

        # Per-video subjective ratings from the survey spreadsheet
        for v in range(1, 6):
            rec[f"valence_v{v}"]   = float(row.get(f"valence_v{v}",   np.nan))
            rec[f"arousal_v{v}"]   = float(row.get(f"arousal_v{v}",   np.nan))
            rec[f"immersion_v{v}"] = float(row.get(f"immersion_v{v}", np.nan))

        # Per-video head-tracking metrics
        for v in range(1, 6):
            csv_name = str(row.get(f"v{v}", ""))
            path     = _resolve_csv_path(v, csv_name)
            m        = _compute_metrics(path) if path else None
            if m:
                for k, val in m.items():
                    rec[f"v{v}_{k}"] = float(val)
            else:
                # Fill with NaN so downstream code can use .dropna() cleanly
                for ax in CSV_AXES.keys():
                    rec[f"v{v}_mean_{ax}"] = np.nan
                    rec[f"v{v}_std_{ax}"]  = np.nan
                rec[f"v{v}_duration_s"] = np.nan
                rec[f"v{v}_n_frames"]   = np.nan

        records.append(rec)

    ht = pd.DataFrame(records)
    # Re-attach Categorical so downstream groupby preserves order
    ht["depression_group"] = pd.Categorical(
        ht["depression_group"], categories=GROUP_ORDER, ordered=True
    )
    return ht


def build_long(ht: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Convert the wide head-tracking table to long format (one row per
    participant × video), adding video-level subjective ratings.

    Useful for GLM / mixed-models that pool across all five videos.

    Parameters
    ----------
    ht : pd.DataFrame, optional
        Output of build_headtrack(). Built automatically if not provided.

    Returns
    -------
    pd.DataFrame
        200 rows (40 × 5) with columns:
        participant, depression_group, score_phq, score_gad, score_stai_t,
        video, yaw, pitch, roll, total, immersion, valence, arousal.
    """
    if ht is None:
        ht = build_headtrack()

    rows = []
    for _, row in ht.iterrows():
        for v in range(1, 6):
            yaw_val = row.get(f"v{v}_mean_yaw", np.nan)
            if pd.isna(yaw_val):
                continue
            rows.append({
                "participant":      row["participant"],
                "depression_group": row["depression_group"],
                "score_phq":        row["score_phq"],
                "score_gad":        row["score_gad"],
                "score_stai_t":     row["score_stai_t"],
                "video":            f"V{v}",
                "yaw":              float(yaw_val),
                "pitch":            float(row.get(f"v{v}_mean_pitch", np.nan)),
                "roll":             float(row.get(f"v{v}_mean_roll",  np.nan)),
                "total":            float(row.get(f"v{v}_mean_total", np.nan)),
                "immersion":        float(row.get(f"immersion_v{v}",  np.nan)),
                "valence":          float(row.get(f"valence_v{v}",    np.nan)),
                "arousal":          float(row.get(f"arousal_v{v}",    np.nan)),
            })

    long = pd.DataFrame(rows)
    long["depression_group"] = pd.Categorical(
        long["depression_group"], categories=GROUP_ORDER, ordered=True
    )
    long["video"] = pd.Categorical(
        long["video"], categories=[f"V{v}" for v in range(1, 6)]
    )
    return long
