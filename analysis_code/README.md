# VR Depression Study — Analysis Code (Report 1)
### Behavioral Research & Statistical Methods | IIIT Hyderabad
### Team: Rachakonda Hrithik Sagar | Aryan Jain | Vidhi Rathore

---

## Folder Layout Expected

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
    ├── 01_data_exploration.py  ...
    └── outputs/            ← auto-created
```

config.py points to ../data/data.xlsx and ../data/headtracking-data by default.

---

## Setup

```bash
pip install -r requirements.txt
```

## How to Run

```bash
cd analysis_code
python run_all.py
```

---

## Script Summary

| Script | What it does | Key output |
|--------|-------------|------------|
| `01` | Data overview, demographics | Console |
| `02` | Shapiro-Wilk normality + outlier detection (IQR & z-score) | Console |
| `03` | PHQ-9 group assignment + full descriptive stats | `descriptive_stats.csv`, `group_stats.csv` |
| `04` | Pearson r, Spearman rho, Kruskal-Wallis H (anxiety by group) | `correlation_matrix.csv` |
| `05` | Per-video ratings, Kruskal-Wallis (group x video), PANAS paired t-test | `video_stats.csv` |
| `06` | Head-tracking yaw speed, Kruskal-Wallis, Spearman | `headtrack_summary.csv`, `fig5.png` |
| `07` | Generates all 4 Report 1 figures (fig1-fig4) | `fig1-fig4.png` |
| `08` | Additional head-tracking visualisations | `fig5-fig7.png` |

---

## Head-Tracking CSV Format

Each CSV (one per participant x video) has 11 columns:

| Column | Description | Used? |
|--------|-------------|-------|
| Time | Seconds since session start | YES - duration |
| PositionChangeX/Y/Z | Head position change (metres) | NO - negligible in seated task |
| RotationChangeX/Y/Z | Raw rotation angle change (degrees) | NO - speed columns preferred |
| RotationSpeedX | Pitch speed up/down (deg/s) | NO |
| RotationSpeedY | Yaw angular speed (deg/s) PRIMARY METRIC | YES |
| RotationSpeedZ | Roll speed tilt (deg/s) | NO |
| RotationSpeedTotal | Total 3-D rotation speed (deg/s) | Computed |


Why yaw only? 360 video exploration is predominantly horizontal scanning.
Matches primary metric of Srivastava & Lahane (2025).

---

## Statistical Methods (Report 1)

| Method | Script | Why used |
|--------|--------|----------|
| Shapiro-Wilk | 02 | Normality test before choosing parametric vs non-parametric |
| IQR + z-score | 02 | Dual outlier detection |
| Pearson r | 04 | Correlations among clinical scales |
| Kruskal-Wallis H | 04, 05, 06 | Non-parametric group comparison — normality violated; matches Srivastava & Lahane (2025) |
| Spearman rho | 04, 06 | Non-parametric correlation for head-tracking vs PHQ-9 |
| Paired t-test | 05 | PANAS difference scores were normally distributed (SW p > .10) |



