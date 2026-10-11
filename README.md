<div align="center">

# IPL INTELLIGENCE

### Cricket Analytics & Performance Insights Platform

**Turning IPL ball-by-ball data into interactive, data-driven cricket insights.**

<br>

[![Live Dashboard](https://img.shields.io/badge/EXPLORE-LIVE%20DASHBOARD-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://ipl-intelligence-nkqj6vtrqlbab2gvoygege.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)

<br>

[Live Application](https://ipl-intelligence-nkqj6vtrqlbab2gvoygege.streamlit.app) ·
[Source Code](https://github.com/Ashokreddy45/ipl-intelligence)

</div>

---

## 01 — Project Overview

**IPL Intelligence** is an interactive cricket analytics platform built to explore historical Indian Premier League data through statistical analysis and visual storytelling.

The platform transforms match-level and ball-by-ball records into accessible visual insights, enabling users to investigate scoring patterns, evaluate player performance, compare teams, and explore how outcomes vary across seasons and innings phases.

Rather than presenting cricket statistics as static tables, IPL Intelligence brings them together in a unified analytical dashboard designed for exploration, comparison, and discovery.

<div align="center">

### Explore the live dashboard

[**Launch IPL Intelligence →**](https://ipl-intelligence-nkqj6vtrqlbab2gvoygege.streamlit.app)

</div>

## 02 — Analytical Capabilities

| Module | What it explores |
|---|---|
| **Tournament Overview** | Match statistics, aggregate scoring, wickets, legal deliveries, and season-level trends |
| **Batting Analytics** | Run production, batting averages, strike rates, boundaries, and player comparisons |
| **Bowling Analytics** | Bowling workloads, wicket-related metrics, and performance comparisons |
| **Player Matchups** | Comparative player performance and matchup-oriented analysis |
| **Teams & Match Phases** | Team trends and performance across different stages of an innings |
| **Data Explorer** | Interactive exploration of the underlying analytical data |

### Designed for interactive analysis

- **Contextual filtering** — Explore selected seasons and teams.
- **Comparative analysis** — Evaluate players and performance metrics side by side.
- **Interactive visualizations** — Investigate trends through charts and data tables.
- **Sample-aware rankings** — Apply minimum-ball thresholds to batting and bowling rankings.
- **Season-level exploration** — Examine how scoring and performance change over time.

## 03 — Technology Stack

| Technology | Role in the project |
|---|---|
| **Python** | Application logic and analytical workflows |
| **Pandas** | Data preparation, aggregation, and transformation |
| **NumPy** | Numerical computation |
| **Plotly** | Interactive data visualization |
| **Streamlit** | Dashboard interface and application delivery |

## 04 — System Architecture

The application follows a straightforward analytical workflow, separating dataset preparation, reusable analytics, and dashboard presentation.

```text
Historical IPL Dataset
         │
         ▼
Dataset Preparation
   src/build_dataset.py
         │
         ▼
Processed Match & Delivery Data
         │
         ▼
Analytical Functions
     src/analytics.py
         │
         ▼
Interactive Dashboard
         app.py
         │
         ▼
Charts · Filters · Comparisons · Insights
```

## 05 — Repository Structure

```text
ipl-intelligence/
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

The structure above highlights the primary application files. Additional project assets and configuration files may also be present.

## 06 — Getting Started

Follow these steps to run the application locally.

### Prerequisites

- Python 3.x
- Git
- The IPL dataset required by the data preparation pipeline

### Step 1 — Clone the repository

```bash
git clone https://github.com/Ashokreddy45/ipl-intelligence.git
cd ipl-intelligence
```

### Step 2 — Create a virtual environment

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

### Step 3 — Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4 — Prepare the data

If the processed datasets are not available locally, place the required source dataset in the expected `data/raw/` location and run:

```bash
python src/build_dataset.py
```

Ensure the source archive and its format match what the dataset preparation script expects.

### Step 5 — Start the application

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, usually:

`http://localhost:8501`

## 07 — Data & Analytical Approach

The platform works with historical IPL match and delivery records to support analysis at several levels:

- **Match level:** match counts and aggregate match statistics.
- **Season level:** scoring patterns and historical trends.
- **Player level:** batting and bowling performance metrics.
- **Team level:** team-based comparisons and innings-phase analysis.
- **Delivery level:** granular observations used to derive aggregated statistics.

Analytical results depend on the available dataset fields and the definitions implemented in the project. Player comparisons should be interpreted in context, particularly when sample sizes differ.

## 08 — Engineering & Learning Outcomes

This project brings together practical data analytics and application development:

- Data preparation and transformation with Python.
- Grouped statistical analysis using Pandas and NumPy.
- Interactive chart development with Plotly.
- Multi-section dashboard design with Streamlit.
- Reusable analytical logic separated from the presentation layer.
- Deployment of an interactive data application.

## 09 — Roadmap

Potential future extensions include:

- Advanced batter-versus-bowler matchup analysis.
- More detailed innings-phase and team-strategy comparisons.
- Additional validation of derived cricket metrics.
- Expanded statistical analysis and carefully evaluated predictive models.
- Further performance optimization for interactive dashboard workloads.

These are potential enhancements, not claims about existing functionality.

## 10 — Live Application

The dashboard is deployed on Streamlit Community Cloud.

<div align="center">

[![Open IPL Intelligence](https://img.shields.io/badge/OPEN%20IPL%20INTELLIGENCE-Launch%20Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://ipl-intelligence-nkqj6vtrqlbab2gvoygege.streamlit.app)

**[ipl-intelligence-nkqj6vtrqlbab2gvoygege.streamlit.app](https://ipl-intelligence-nkqj6vtrqlbab2gvoygege.streamlit.app)**

</div>

## Author

**Ashok Reddy Damireddy**

GitHub: [@Ashokreddy45](https://github.com/Ashokreddy45)

---

<div align="center">

*IPL Intelligence — Explore the game through data.*

</div>
