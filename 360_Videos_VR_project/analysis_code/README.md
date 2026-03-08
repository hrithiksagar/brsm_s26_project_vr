# VR Depression Study — Analysis Code
### Behavioral Research & Statistical Methods | IIIT Hyderabad

---

## Folder Layout Expected

Place your files so the folder tree looks like this:

```
360_Videos_VR_project/
├── data/
│   ├── data.xlsx
│   └── headtracking-data/
│       ├── v1/   data_video1_*.csv   (one per participant)
│       ├── v2/   data_video2_*.csv
│       ├── v3/   data_video3_*.csv
│       ├── v4/   data_video4_*.csv
│       └── v5/   data_video5_*.csv
└── analysis_code/          ← run scripts from HERE
    ├── config.py
    ├── run_all.py
    ├── 01_data_exploration.py
    ├── ...
    └── outputs/            ← auto-created, all results saved here
```

config.py already points to `../data/data.xlsx` and
`../data/headtracking-data` by default. Edit if your layout differs.

---

## Setup

```bash
pip install -r requirements.txt
```

---

## How to Run

```bash
cd analysis_code

# Report 1 only (no head-tracking needed):
python run_all.py

# Full analysis including head-tracking (Report 2):
python run_all.py --report2
```

Or run any single script:
```bash
python 03_grouping_and_descriptives.py
python 06_head_tracking_analysis.py
```

---

## Script Summary

| Script | What it does | Key output |
|--------|-------------|------------|
| `01` | Data overview, demographics | Console |
| `02` | Shapiro-Wilk normality + outlier detection (IQR & z-score) | Console |
| `03` | PHQ-9 group assignment + full descriptive stats | `descriptive_stats.csv`, `group_stats.csv` |
| `04` | Pearson r, Spearman ρ, Kruskal-Wallis H | `correlation_matrix.csv` |
| `05` | Video valence/arousal, Friedman, Wilcoxon, PANAS t-test | `video_stats.csv` |
| `06` | **[Report 2]** Head-tracking → scanning speed → ANCOVA | `headtrack_summary.csv`, `fig5`, `fig6` |
| `07` | Regenerates all 4 Report 1 figures | `fig1–fig4.png` |

---

## Head-Tracking CSV Format

Each CSV (one per participant × video) has these columns:

| Column | Description |
|--------|-------------|
| `Time` | Seconds since session start |
| `RotationSpeedY` | **Yaw angular speed (deg/s) — PRIMARY METRIC** |
| `RotationSpeedTotal` | Total 3-D rotation speed magnitude (deg/s) |
| `RotationSpeedX` | Pitch speed — up/down (deg/s) |
| `RotationSpeedZ` | Roll speed — tilt (deg/s) |
| `RotationChangeY` | Cumulative yaw rotation (degrees) |

The last row of each CSV is a summary row ("Circular Averages,...") and is
automatically skipped by the parser.

**Primary metric used**: mean `RotationSpeedY` per participant per video,
matching the "head scanning speed" metric of Srivastava & Lahane (2025).

---

## Key Preliminary Results (from actual data)

### Head Scanning Speed by Video
| Video | Mean (deg/s) | SD |
|-------|-------------|-----|
| V1: Abandoned Buildings | 31.19 | 8.77 |
| V2: Evening at Beach    | 28.14 | 7.73 |
| V3: Campus              | 29.73 | 9.39 |
| V4: The Nun (Horror)    | 17.92 | 8.28 |
| V5: Tahiti Surf         | 25.95 | 9.64 |

**V4 (Horror) has substantially lower scanning speed** despite the highest
arousal ratings — likely due to the threatening content freezing head movement.

### Depression Group Trends
- V1, V3, V5: Moderate-Severe group shows numerically lower yaw speed
  than Minimal (direction consistent with paper's hypothesis)
- None of the videos show a statistically significant Kruskal-Wallis result
  (all p > 0.30) — partial failure to replicate. See Report 2 for ANCOVA
  results controlling for anxiety.

---

## Statistical Methods Justification

| Method | Where | Why |
|--------|-------|-----|
| Shapiro-Wilk | Script 02 | Test normality in small sample (N=40) |
| IQR + z-score | Script 02 | Dual outlier detection for triangulation |
| Kruskal-Wallis H | Scripts 04, 05, 06 | PHQ/GAD/STAI violate normality |
| Spearman ρ | Scripts 04, 06 | Non-parametric correlation (non-normal data) |
| Friedman test | Script 05 | Non-parametric repeated-measures across videos |
| Wilcoxon signed-rank | Script 05 | Paired video comparisons |
| Paired t-test | Script 05 | PANAS difference scores were normally distributed |
| ANCOVA | Script 06 | Controls for GAD-7/STAI-T covariance with depression |
