# 🏏 IPL Intelligence — Cricket Data Analytics

An interactive cricket analytics platform for exploring Indian Premier League (IPL) history through data-driven insights into batting, bowling, team performance, player matchups, and tactical trends.

<p align="center">
  <a href="https://ipl-intelligence-nkqj6vtrqlbab2gvoygege.streamlit.app">
    <img src="https://img.shields.io/badge/Live%20Dashboard-Open%20App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Open Live Dashboard">
  </a>
  <a href="https://github.com/Ashokreddy45/ipl-intelligence">
    <img src="https://img.shields.io/badge/Source%20Code-GitHub-181717?style=for-the-badge&logo=github" alt="GitHub Repository">
  </a>
</p>

> **Explore the live application:**  
> https://ipl-intelligence-nkqj6vtrqlbab2gvoygege.streamlit.app

---

## Overview

IPL Intelligence transforms historical IPL ball-by-ball and match data into an interactive dashboard. It helps users investigate scoring patterns, compare player performance, explore team trends, and understand how performance changes across seasons and match situations.

The dashboard is designed to make cricket statistics easier to explore through interactive visualizations, filters, and player-level analysis.

## Key Features

- **Tournament Overview** — Explore match totals, runs, wickets, legal deliveries, and season-level scoring trends.
- **Batting Analytics** — Investigate run production, batting averages, strike rates, and player performance.
- **Bowling Analytics** — Examine bowling performance using delivery and wicket-related statistics.
- **Player Matchups** — Explore comparative performance and matchup patterns.
- **Teams & Match Phases** — Investigate team trends and performance across different phases of an innings.
- **Data Explorer** — Explore the underlying data through interactive tables and filters.
- **Interactive Filtering** — Narrow analyses by season and team.
- **Player Comparison** — Compare selected players using key batting statistics and season trends.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and application logic |
| Pandas | Data cleaning, transformation, and analysis |
| NumPy | Numerical operations |
| Plotly | Interactive charts and visualizations |
| Streamlit | Dashboard interface and deployment |

## Project Structure

```text
ipl_intelligence_project/
├── app.py
├── requirements.txt
├── src/
│   ├── analytics.py
│   └── build_dataset.py
├── data/
│   ├── raw/
│   └── processed/
└── README.md
```

*The exact repository contents may include additional files and folders.*

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Ashokreddy45/ipl-intelligence.git
cd ipl-intelligence
```

### 2. Create and activate a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Prepare the dataset, if required

If the processed datasets are not included in your local checkout, ensure the raw dataset is present under `data/raw/` and run:

```bash
python src/build_dataset.py
```

### 5. Launch the dashboard

```bash
streamlit run app.py
```

Streamlit will provide a local URL in the terminal, usually `http://localhost:8501`.

## Data & Methodology

The project uses historical IPL match and ball-by-ball records to derive match-level, season-level, team-level, and player-level insights.

Analyses depend on the fields available in the underlying dataset. Interpret player rankings with attention to sample size, season context, and the distinction between raw totals and rate-based statistics.

## Project Goals

- Demonstrate practical data analysis and transformation using Python.
- Build interactive visualizations for a real-world sports dataset.
- Explore statistical patterns in cricket performance.
- Present analytical findings in an accessible dashboard.

## Future Improvements

Potential extensions include advanced batter-versus-bowler analysis, phase-specific team strategy comparisons, predictive modeling, and additional validation of derived cricket metrics.

## Live Demo

**[Launch IPL Intelligence Dashboard](https://ipl-intelligence-nkqj6vtrqlbab2gvoygege.streamlit.app)**

## Author

**Ashok Reddy Damireddy**

- GitHub: [@Ashokreddy45](https://github.com/Ashokreddy45)

---

If you find this project useful, feel free to explore the source code and share feedback.
