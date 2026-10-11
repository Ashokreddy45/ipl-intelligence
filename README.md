# IPL Intelligence — Cricket Analytics Dashboard

An end-to-end cricket analytics project that transforms IPL ball-by-ball data into interactive insights on batting, bowling, player matchups, team strategy, and match outcomes.

Built with Python, Pandas, NumPy, Plotly, and Streamlit, the project combines a reproducible data-processing pipeline with an interactive dashboard and supporting analytical reports.

<!-- Replace the placeholder below after deployment -->
<!-- Live dashboard: https://YOUR-APP-NAME.streamlit.app -->

## Project Overview

IPL Intelligence is designed to explore performance beyond basic scorecards. It processes match-level and delivery-level data, derives analytical features, checks data quality, and presents findings through interactive visualizations.

**Project objectives**
- Explore player performance across IPL seasons.
- Compare batting and bowling contributions using contextual metrics.
- Examine batter-versus-bowler matchups.
- Investigate team performance, innings phases, and match outcomes.
- Provide a reproducible workflow from source data to dashboard.

## Dashboard Features

### Tournament Overview
- Season-level trends and tournament summaries.
- Match and scoring patterns.
- Interactive filters for exploring the dataset.

### Batting Intelligence
- Batting performance leaderboards and player profiles.
- Boundary contribution and scoring patterns.
- Consistency and comparative performance analysis.

### Bowling Intelligence
- Bowling performance comparisons.
- Wicket, economy, and related bowling metrics.
- Phase-based and dismissal-pattern analysis.

### Batter–Bowler Matchups
- Head-to-head batter and bowler analysis.
- Runs, dismissals, and matchup-level performance.
- Context for interpreting small samples and player comparisons.

### Teams and Innings Phases
- Team and season comparisons.
- Analysis by innings phase.
- Chasing, defending, and match-context exploration.

### Data Explorer
- Explore delivery-level records and match information.
- Inspect scoring, extras, and dismissal patterns.

> Metric definitions and filters matter. Comparisons can be affected by sample size, role, season, and match context; use minimum-ball or minimum-innings thresholds where available.

## Dataset and Data Quality

The project uses Cricsheet's New CSV archive, retained at `data/raw/ipl_csv2.zip`.

The current local data audit reports:
- **1,243 matches**
- **295,732 delivery records**
- **19 seasons**, from 2007/08 through 2026
- **739 unique batters**
- **578 unique bowlers**
- No missing match IDs, striker values, or bowler values in the audited delivery dataset
- No exact duplicate delivery rows in the audited dataset

These figures describe the current local dataset and should be rechecked when the source archive changes.

### Data source and attribution

Source: [Cricsheet downloads](https://cricsheet.org/downloads/).

The source archive contains `LICENSE.txt`, which identifies the ODC Attribution License (ODC-By). Review and follow the license's attribution requirements when redistributing the database or derived data. Retain the original archive and its license information.

This is an independent analytics project and is not affiliated with or endorsed by the IPL or Cricsheet.

### Important limitations

The source data does not provide shot labels such as pull, cut, or sweep; delivery line and length; or wagon-wheel coordinates. The project therefore does not claim to directly measure those attributes.

Historical data, player roles, sample sizes, team-name changes, and season boundaries can affect comparisons. Predictive or statistical outputs should be treated as exploratory analysis, not as guarantees or betting advice.

## Technology Stack

| Area | Tools |
|---|---|
| Language | Python |
| Data processing | Pandas, NumPy |
| Interactive dashboard | Streamlit |
| Visualizations | Plotly |
| Data source | Cricsheet CSV archive |
| Development | Jupyter notebooks, Git, GitHub |
| Hosting | Streamlit Community Cloud |

## Architecture

```text
Cricsheet CSV archive
        |
        v
src/build_dataset.py
        |
        v
Data loading, validation and feature engineering
        |
        +------> reports/data_audit.md
        |
        v
data/processed/
        |
        v
src/analytics.py
        |
        v
app.py — Streamlit dashboard
        |
        v
Interactive charts, comparisons and data explorer
```

The processed CSV files are generated locally from the source archive and are intentionally excluded from version control. On first startup, the application can rebuild missing processed data.

## Repository Structure

```text
ipl-intelligence/
├── app.py
├── requirements.txt
├── DATA_SOURCE.txt
├── data/
│   └── raw/
│       └── ipl_csv2.zip
├── notebooks/
│   ├── 01_data_quality_and_tournament_overview.ipynb
│   ├── 02_batting_performance_and_player_profiles.ipynb
│   ├── 03_bowling_matchups_and_dismissals.ipynb
│   ├── 04_team_strategy_venue_and_match_context.ipynb
│   └── README.md
├── reports/
│   ├── data_audit.md
│   ├── FEATURE_SCOPE.md
│   ├── advanced_*.csv
│   ├── batting_analysis/
│   └── bowling_analysis/
└── src/
    ├── analytics.py
    └── build_dataset.py
```

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Ashokreddy45/ipl-intelligence.git
cd ipl-intelligence
```

### 2. Create and activate a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Build the processed datasets

```bash
python src/build_dataset.py
```

This reads the source archive, processes match and delivery files, creates derived fields, and writes processed datasets and a data audit report.

### 5. Launch the dashboard

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal, usually `http://localhost:8501`.

## Deployment

The dashboard is designed for [Streamlit Community Cloud](https://share.streamlit.io/).

1. Push the repository to GitHub.
2. Sign in to Streamlit Community Cloud using GitHub.
3. Create an app using repository `Ashokreddy45/ipl-intelligence`.
4. Select branch `main` and entrypoint `app.py`.
5. Deploy and review the application logs if startup fails.

Dependencies are declared in the root `requirements.txt`. The app rebuilds the processed datasets when they are missing, using the committed source archive.

After deployment, add the public dashboard URL near the top of this README.

## Reproducibility and Quality Checks

Build the datasets and review `reports/data_audit.md` to inspect the current data-quality summary.

Check Python syntax with:

```bash
python -m py_compile app.py src/analytics.py src/build_dataset.py
```

For meaningful comparisons, inspect metric definitions, sample-size thresholds, and the effects of season or role before drawing conclusions.

## Future Improvements

- Add automated tests for key analytical metrics.
- Validate selected calculations against manually inspected matches.
- Improve notebook narratives with documented findings and reproducible charts.
- Add more robust temporal validation if predictive modelling is expanded.
- Continue refining data-quality checks and player/team name normalization.

## Author

**Ashok Reddy Damireddy**

Computer Science Engineering — Data Science

- GitHub: [@Ashokreddy45](https://github.com/Ashokreddy45)

---

*Built as a portfolio project to demonstrate data processing, exploratory analysis, metric design, visualization, and deployment.*
