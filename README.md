# IPL Intelligence — End-to-End Cricket Analytics

An interactive, reproducible IPL analytics project built from Cricsheet's newer CSV archive. It covers player performance, team and season trends, innings phases, batter–bowler matchups, match outcomes, exploratory statistical analysis, and an initial machine-learning baseline.

## Data source and attribution

Match and ball-by-ball data are sourced from [Cricsheet](https://cricsheet.org/downloads/), using its New CSV archive. The original archive is retained at `data/raw/ipl_csv2.zip`; its `LICENSE.txt` contains the applicable ODC Attribution License (ODC-By). Please consult and follow that license's attribution requirements when redistributing the source data or derived data. This project is an independent analytics project and is not affiliated with the IPL or Cricsheet.

## Important data boundary

The included `data/raw/ipl_csv2.zip` is the Cricsheet New CSV archive supplied for this project. Review `LICENSE.txt` inside the archive and preserve the required attribution when redistributing derived data or the project. The archive does **not** record shot names (pull, cut, sweep), delivery line/length, or wagon-wheel coordinates. Therefore the app does not claim to measure those directly. They require a separate annotated/tracking dataset.

## Quick start (Mac)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/build_dataset.py
streamlit run app.py
```

The first build extracts match files from the ZIP, validates the data, and creates local analytical CSVs under `data/processed/`. These generated files are intentionally excluded from version control.

## Project structure

- `data/raw/ipl_csv2.zip` — original source archive
- `src/build_dataset.py` — extraction, loading, quality checks, and feature engineering
- `src/analytics.py` — reusable metrics and matchup calculations
- `app.py` — interactive Streamlit dashboard
- `notebooks/` — notebook plan and starter notebook-generation instructions
- `reports/` — generated audit report after the build

## Analysis sections

1. Tournament overview and season trends
2. Batting leaderboard and player profile
3. Bowling leaderboard and player profile
4. Batter vs bowler matchup explorer
5. Team and innings-phase analysis
6. Match outcomes and toss patterns
7. Delivery, extras, dismissal, and scoring patterns
8. Exploratory win-probability model baseline

## Metric definitions and safeguards

- Legal balls exclude wides and no-balls; economy and overs use legal balls.
- Batter runs are `runs_off_bat`; innings/team runs include extras.
- A batter dismissal is not the same as any wicket: run-outs and other non-bowler dismissals are handled separately.
- Player comparisons must include minimum-ball / minimum-innings filters to avoid ranking tiny samples.
- The initial predictive model is a baseline, not a betting tool or a guarantee. Proper temporal validation and calibration are needed before stronger claims.
- Cricsheet CSVs contain no shot labels or ball-tracking coordinates. Do not infer a pull-shot success rate from generic runs/dismissals.

## Deployment

For Streamlit Community Cloud:
1. Push the project to GitHub.
2. In the app deployment settings, set the main file to `app.py`.
3. Ensure `requirements.txt` is in the repository root.
4. Keep generated `data/processed/` files out of Git. The app builds them on first run from the included archive. If you prefer not to commit source data, configure a private download workflow and follow the dataset licence.

## Next quality gates

- Run the pipeline and inspect `reports/data_audit.md`.
- Review team-name changes and season boundaries.
- Validate selected metrics manually against sample matches.
- Add tests and notebook narratives after the first audit.
