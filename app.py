from pathlib import Path
import sys, subprocess
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from analytics import add_derived_columns, batting_table, bowling_table, matchup_table

st.set_page_config(page_title="IPL Intelligence", page_icon="🏏", layout="wide")
st.title("🏏 IPL Intelligence")
st.caption("Historical IPL analytics • player performance • team trends • matchups • tactical patterns")

DATA = ROOT / "data" / "processed" / "deliveries.csv"
MATCHES = ROOT / "data" / "processed" / "matches.csv"

@st.cache_data(show_spinner="Building and validating the IPL dataset…")
def load_data():
    if not DATA.exists() or not MATCHES.exists():
        subprocess.run([sys.executable, str(ROOT/"src"/"build_dataset.py")], check=True, cwd=ROOT)
    d = pd.read_csv(DATA, low_memory=False)
    m = pd.read_csv(MATCHES, low_memory=False)
    d["start_date"] = pd.to_datetime(d["start_date"], errors="coerce")
    d["season"] = d["season"].astype(str)
    for c in ["runs_off_bat","extras","total_runs","legal_ball","is_wicket","is_boundary_four","is_boundary_six"]:
        if c in d: d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    return d, m

try:
    df, matches = load_data()
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

with st.sidebar:
    st.header("Filters")
    seasons = sorted(df["season"].dropna().astype(str).unique())
    selected_seasons = st.multiselect("Season", seasons, default=seasons)
    teams = sorted(set(df["batting_team"].dropna()) | set(df["bowling_team"].dropna()))
    selected_teams = st.multiselect("Teams", teams, default=teams)
    min_balls = st.slider("Minimum legal balls for player rankings", 0, 1000, 120, 30)
    st.caption("Rankings with small samples can be misleading. Adjust the minimum-ball threshold.")

f = df[df["season"].isin(selected_seasons) & df["batting_team"].isin(selected_teams)].copy()
if f.empty:
    st.warning("No deliveries match the selected filters.")
    st.stop()

total_runs = int(f["total_runs"].sum())
wickets = int(f["is_wicket"].sum())
matches_count = int(f["match_id"].nunique())
legal_balls = int(f["legal_ball"].sum())
c1,c2,c3,c4 = st.columns(4)
c1.metric("Matches", f"{matches_count:,}")
c2.metric("Runs", f"{total_runs:,}")
c3.metric("Wickets", f"{wickets:,}")
c4.metric("Legal balls", f"{legal_balls:,}")

tabs = st.tabs(["Overview", "Batting", "Bowling", "Matchups", "Teams & phases", "Data explorer"])
with tabs[0]:
    st.subheader("Tournament scoring trends")
    season_summary = f.groupby("season").agg(runs=("total_runs","sum"), wickets=("is_wicket","sum"), deliveries=("match_id","size"), matches=("match_id","nunique")).reset_index()
    a,b = st.columns(2)
    a.plotly_chart(px.line(season_summary, x="season", y="runs", markers=True, title="Total runs by season"), width="stretch")
    b.plotly_chart(px.line(season_summary, x="season", y="wickets", markers=True, title="Recorded wickets by season"), width="stretch")
    phase = f.groupby("phase").agg(runs=("total_runs","sum"), wickets=("is_wicket","sum"), legal_balls=("legal_ball","sum")).reset_index()
    phase["run_rate"] = np.where(phase.legal_balls>0, phase.runs*6/phase.legal_balls, np.nan)
    st.plotly_chart(px.bar(phase, x="phase", y="run_rate", title="Run rate by innings phase"), width="stretch")
    st.info("Season totals reflect the selected batting-team filters and the archive's available matches.")

    st.divider()
    st.subheader("Match & Innings Intelligence")

    innings_required = {"match_id", "innings", "over_number", "total_runs"}
    if innings_required.issubset(df.columns) and not df.empty:
        innings_source = df.copy()
        innings_source["total_runs"] = pd.to_numeric(
            innings_source["total_runs"], errors="coerce"
        ).fillna(0)
        innings_source["over_number"] = pd.to_numeric(
            innings_source["over_number"], errors="coerce"
        )

        match_ids = sorted(innings_source["match_id"].dropna().unique().tolist())
        chosen_match = st.selectbox(
            "Select a match ID",
            match_ids,
            key="overview_innings_match",
        )

        selected_match_data = innings_source[
            innings_source["match_id"] == chosen_match
        ].copy()

        innings_options = sorted(
            selected_match_data["innings"].dropna().unique().tolist()
        )
        if innings_options:
            chosen_innings = st.selectbox(
                "Select innings",
                innings_options,
                key="overview_innings_number",
            )
            innings_data = selected_match_data[
                selected_match_data["innings"] == chosen_innings
            ].copy()

            if not innings_data.empty:
                innings_data = innings_data.sort_values(
                    ["over_number"] +
                    (["actual_delivery"] if "actual_delivery" in innings_data.columns else [])
                )
                innings_data["Cumulative runs"] = innings_data["total_runs"].cumsum()

                c1, c2, c3 = st.columns(3)
                c1.metric("Innings runs", f"{innings_data['total_runs'].sum():,.0f}")
                c2.metric("Overs represented", str(innings_data["over_number"].nunique()))
                c3.metric(
                    "Wickets recorded",
                    str(
                        int(innings_data["is_wicket"].sum())
                        if "is_wicket" in innings_data.columns else 0
                    ),
                )

                progression = (
                    innings_data.groupby("over_number", dropna=True)
                    .agg(
                        Over_runs=("total_runs", "sum"),
                        Cumulative_runs=("total_runs", "sum"),
                    )
                    .reset_index()
                    .sort_values("over_number")
                )
                progression["Cumulative_runs"] = progression["Over_runs"].cumsum()

                fig_progression = px.line(
                    progression,
                    x="over_number",
                    y="Cumulative_runs",
                    markers=True,
                    title="Innings Scoring Progression",
                    labels={
                        "over_number": "Over number",
                        "Cumulative_runs": "Cumulative team runs",
                    },
                )
                st.plotly_chart(fig_progression, use_container_width=True)

                if "phase" in innings_data.columns:
                    phase_summary = (
                        innings_data.groupby("phase", dropna=False)
                        .agg(
                            Runs=("total_runs", "sum"),
                            Overs=("over_number", "nunique"),
                        )
                        .reset_index()
                    )
                    phase_summary["Runs per over"] = (
                        phase_summary["Runs"] / phase_summary["Overs"].replace(0, np.nan)
                    )
                    fig_phase = px.bar(
                        phase_summary,
                        x="phase",
                        y="Runs",
                        color="phase",
                        hover_data=["Overs", "Runs per over"],
                        title="Runs by Match Phase",
                    )
                    st.plotly_chart(fig_phase, use_container_width=True)

                if "is_wicket" in innings_data.columns:
                    wicket_data = innings_data.copy()
                    wicket_data["Wickets in delivery"] = pd.to_numeric(
                        wicket_data["is_wicket"], errors="coerce"
                    ).fillna(0)
                    wicket_data["Cumulative wickets"] = (
                        wicket_data["Wickets in delivery"].cumsum()
                    )
                    wicket_progression = (
                        wicket_data.groupby("over_number", dropna=True)
                        .agg(
                            Cumulative_wickets=("Cumulative wickets", "max"),
                        )
                        .reset_index()
                    )
                    fig_wickets = px.line(
                        wicket_progression,
                        x="over_number",
                        y="Cumulative_wickets",
                        markers=True,
                        title="Wicket Progression",
                        labels={
                            "over_number": "Over number",
                            "Cumulative_wickets": "Cumulative wickets",
                        },
                    )
                    st.plotly_chart(fig_wickets, use_container_width=True)
        else:
            st.info("No innings are available for this match.")
    else:
        st.info("Match progression requires match ID, innings, over number, and total runs.")
with tabs[1]:
    st.subheader("Batting performance")
    bt = batting_table(f)
    bt = bt[bt["balls_faced"] >= min_balls]
    st.plotly_chart(px.scatter(bt, x="strike_rate", y="average", size="runs", hover_name="player", title="Batting average vs strike rate (bubble size = runs)"), width="stretch")
    st.dataframe(bt.sort_values("runs", ascending=False), width="stretch", hide_index=True)
    players = sorted(f["striker"].dropna().unique())
    chosen = st.selectbox("Inspect batter", players, key="batter")
    pdta = f[f["striker"] == chosen]
    pc1,pc2,pc3 = st.columns(3)
    pc1.metric("Runs", f"{pdta.runs_off_bat.sum():,.0f}")
    pc2.metric("Legal balls", f"{pdta.legal_ball.sum():,.0f}")
    pc3.metric("Boundary fours / sixes", f"{(pdta.runs_off_bat==4).sum()} / {(pdta.runs_off_bat==6).sum()}")
    st.plotly_chart(px.bar(pdta.groupby("phase", as_index=False).agg(runs=("runs_off_bat","sum"), balls=("legal_ball","sum")), x="phase", y="runs", title=f"{chosen}: runs by phase"), width="stretch")

    st.divider()
    st.subheader("Player Comparison")
    st.caption("Compare batting output using the currently selected seasons and teams.")

    comparison_players = sorted(f["striker"].dropna().unique())

    if len(comparison_players) >= 2:
        col_a, col_b = st.columns(2)
        default_a = comparison_players[0]
        default_b = comparison_players[1]

        player_a = col_a.selectbox(
            "First batter",
            comparison_players,
            index=comparison_players.index(default_a),
            key="compare_batter_a"
        )
        player_b = col_b.selectbox(
            "Second batter",
            comparison_players,
            index=comparison_players.index(default_b),
            key="compare_batter_b"
        )

        comparison_rows = []
        for player in [player_a, player_b]:
            player_df = f[f["striker"] == player]
            runs = player_df["runs_off_bat"].sum()
            balls = player_df["is_legal_ball"].sum()
            dismissals = player_df["player_dismissed"].notna().sum()
            fours = player_df["is_boundary_four"].sum()
            sixes = player_df["is_boundary_six"].sum()

            comparison_rows.append({
                "Player": player,
                "Runs": int(runs),
                "Legal balls": int(balls),
                "Dismissals recorded": int(dismissals),
                "Strike rate": 100 * runs / balls if balls else np.nan,
                "Average": runs / dismissals if dismissals else np.nan,
                "Fours": int(fours),
                "Sixes": int(sixes),
                "Boundary runs %": (
                    100 * (4 * fours + 6 * sixes) / runs if runs else np.nan
                ),
                "Matches": player_df["match_id"].nunique()
            })

        comparison = pd.DataFrame(comparison_rows)
        st.dataframe(
            comparison.round(2),
            width="stretch",
            hide_index=True
        )

        metric_options = {
            "Runs": "runs_off_bat",
            "Balls faced": "is_legal_ball",
            "Fours": "is_boundary_four",
            "Sixes": "is_boundary_six"
        }
        selected_metric = st.selectbox(
            "Season trend metric",
            list(metric_options.keys()),
            key="comparison_trend_metric"
        )

        season_comparison = (
            f[f["striker"].isin([player_a, player_b])]
            .groupby(["season", "striker"], as_index=False)
            .agg(
                value=(metric_options[selected_metric], "sum")
            )
        )

        st.plotly_chart(
            px.line(
                season_comparison,
                x="season",
                y="value",
                color="striker",
                markers=True,
                title=f"{selected_metric} by season"
            ),
            width="stretch"
        )

        if player_a == player_b:
            st.info("Choose two different batters for a meaningful comparison.")
    else:
        st.info("At least two batters are needed for comparison.")


    st.divider()
    st.subheader("Player Performance Intelligence")

    required = {"striker", "match_id", "innings_key", "runs_off_bat"}
    if not required.issubset(f.columns):
        st.warning("Required batting columns are unavailable for this analysis.")
    elif f.empty:
        st.info("No batting deliveries match the current filters.")
    else:
        balls_col = "is_legal_ball" if "is_legal_ball" in f.columns else None
        runs_col = "runs_off_bat"

        innings_data = (
            f.groupby(["striker", "match_id", "innings_key"], dropna=False)
            .agg(
                Innings_runs=(runs_col, "sum"),
                Balls_faced=(balls_col, "sum") if balls_col else (runs_col, "size"),
            )
            .reset_index()
        )

        player_stats = (
            innings_data.groupby("striker")
            .agg(
                Innings=("Innings_runs", "count"),
                Total_runs=("Innings_runs", "sum"),
                Average_innings_runs=("Innings_runs", "mean"),
                Run_variation=("Innings_runs", "std"),
                Best_innings=("Innings_runs", "max"),
                Balls_faced=("Balls_faced", "sum"),
            )
            .reset_index()
        )

        player_stats["Run_variation"] = player_stats["Run_variation"].fillna(0)
        player_stats["Strike_rate"] = (
            100 * player_stats["Total_runs"]
            / player_stats["Balls_faced"].replace(0, np.nan)
        )
        player_stats["Consistency_score"] = (
            100 / (1 + player_stats["Run_variation"])
        )

        if {"is_boundary_four", "is_boundary_six"}.issubset(f.columns):
            boundaries = (
                f.groupby("striker")
                .agg(
                    Fours=("is_boundary_four", "sum"),
                    Sixes=("is_boundary_six", "sum"),
                    Batter_runs=("runs_off_bat", "sum"),
                )
                .reset_index()
            )
            boundaries["Boundary_runs"] = (
                boundaries["Fours"] * 4 + boundaries["Sixes"] * 6
            )
            boundaries["Boundary_dependency_pct"] = (
                100 * boundaries["Boundary_runs"]
                / boundaries["Batter_runs"].replace(0, np.nan)
            ).fillna(0)

            player_stats = player_stats.merge(
                boundaries[["striker", "Fours", "Sixes", "Boundary_dependency_pct"]],
                on="striker",
                how="left",
            )

        min_innings = st.slider(
            "Minimum innings played",
            min_value=1,
            max_value=20,
            value=5,
            key="player_intelligence_min_innings",
        )
        qualified = player_stats[player_stats["Innings"] >= min_innings].copy()

        if qualified.empty:
            st.info("No players meet this innings threshold. Try a lower value.")
        else:
            best_runs = qualified.loc[qualified["Total_runs"].idxmax()]
            best_sr = qualified.loc[qualified["Strike_rate"].idxmax()]
            most_consistent = qualified.loc[qualified["Consistency_score"].idxmax()]

            c1, c2, c3 = st.columns(3)
            c1.metric("Most runs", str(best_runs["striker"]),
                      f"{int(best_runs['Total_runs']):,} runs")
            c2.metric("Highest strike rate", str(best_sr["striker"]),
                      f"{best_sr['Strike_rate']:.1f}")
            c3.metric("Lowest run variation", str(most_consistent["striker"]),
                      f"Score {most_consistent['Consistency_score']:.1f}")

            all_batters = sorted(qualified["striker"].dropna().unique().tolist())
            selected_batters = st.multiselect(
                "Select 2 or more batters",
                options=all_batters,
                default=[],
                max_selections=10,
                key="player_intelligence_batter_selector",
                help="Choose two players for a direct comparison, or choose more to compare the top three.",
            )

            if len(selected_batters) < 2:
                st.info("Select at least two batters to compare.")
            else:
                selected_data = qualified[
                    qualified["striker"].isin(selected_batters)
                ].copy()

                if len(selected_batters) == 2:
                    comparison_data = selected_data
                    st.caption("Head-to-head comparison: both selected batters.")
                else:
                    comparison_data = selected_data.nlargest(3, "Total_runs")
                    st.caption("Showing the top 3 selected batters by total runs.")

                fig = px.scatter(
                    comparison_data,
                    x="Strike_rate",
                    y="Total_runs",
                    size="Innings",
                    color="striker",
                    hover_name="striker",
                    hover_data=["Average_innings_runs", "Run_variation"],
                    title="Selected Batters: Runs vs Strike Rate",
                    labels={
                        "Strike_rate": "Strike rate",
                        "Total_runs": "Total runs",
                        "striker": "Batter",
                    },
                )
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("#### Selected Batter Comparison")
                display_columns = [
                    col for col in [
                        "striker", "Innings", "Total_runs", "Balls_faced",
                        "Strike_rate", "Average_innings_runs", "Best_innings",
                        "Consistency_score", "Fours", "Sixes",
                        "Boundary_dependency_pct",
                    ]
                    if col in comparison_data.columns
                ]
                st.dataframe(
                    comparison_data[display_columns]
                    .sort_values("Total_runs", ascending=False)
                    .round(2),
                    use_container_width=True,
                    hide_index=True,
                )

                if "Boundary_dependency_pct" in comparison_data.columns:
                    boundary_chart = px.bar(
                        comparison_data.sort_values("Boundary_dependency_pct"),
                        x="Boundary_dependency_pct",
                        y="striker",
                        orientation="h",
                        title="Boundary Run Dependency of Selected Batters",
                        labels={
                            "Boundary_dependency_pct": "Boundary runs (%)",
                            "striker": "Batter",
                        },
                    )
                    st.plotly_chart(boundary_chart, use_container_width=True)

with tabs[2]:
    st.subheader("Bowling performance")
    bw = bowling_table(f)
    bw = bw[bw["legal_balls"] >= min_balls]
    st.plotly_chart(px.scatter(bw, x="economy", y="wickets", size="legal_balls", hover_name="player", title="Bowling economy vs wickets (bubble size = legal balls)"), width="stretch")
    st.dataframe(bw.sort_values("wickets", ascending=False), width="stretch", hide_index=True)

    st.divider()
    st.subheader("Advanced Bowling Intelligence")

    if not bw.empty:
        metric_cols = st.columns(3)
        best_economy = bw.dropna(subset=["economy"])
        best_average = bw.dropna(subset=["bowling_average"])
        best_strike = bw.dropna(subset=["strike_rate"])

        if not best_economy.empty:
            best = best_economy.loc[best_economy["economy"].idxmin()]
            metric_cols[0].metric(
                "Best economy",
                f"{best['player']} · {best['economy']:.2f}"
            )

        if not best_average.empty:
            best = best_average.loc[best_average["bowling_average"].idxmin()]
            metric_cols[1].metric(
                "Best bowling average",
                f"{best['player']} · {best['bowling_average']:.2f}"
            )

        if not best_strike.empty:
            best = best_strike.loc[best_strike["strike_rate"].idxmin()]
            metric_cols[2].metric(
                "Best bowling strike rate",
                f"{best['player']} · {best['strike_rate']:.2f}"
            )

        display_cols = [
            "player", "matches", "legal_balls", "wickets",
            "runs_conceded", "economy", "bowling_average",
            "strike_rate", "dot_ball_pct"
        ]
        display_cols = [c for c in display_cols if c in bw.columns]

        st.plotly_chart(
            px.scatter(
                bw,
                x="dot_ball_pct",
                y="economy",
                size="wickets",
                hover_name="player",
                hover_data=["matches", "legal_balls", "wickets"],
                title="Dot-ball percentage vs economy"
            ),
            width="stretch"
        )

        st.caption(
            "The best-player cards use the current filters and minimum-ball threshold. "
            "Interpret rankings alongside wickets and sample size."
        )

        st.dataframe(
            bw[display_cols].sort_values("dot_ball_pct", ascending=False),
            width="stretch",
            hide_index=True
        )

        st.markdown("#### Compare two bowlers")

        bowler_names = sorted(f["bowler"].dropna().unique())

        if len(bowler_names) >= 2:
            col_a, col_b = st.columns(2)
            bowler_a = col_a.selectbox(
                "First bowler", bowler_names, key="compare_bowler_a"
            )
            bowler_b = col_b.selectbox(
                "Second bowler", bowler_names, index=1, key="compare_bowler_b"
            )

            compare_rows = []
            for name in [bowler_a, bowler_b]:
                row = bw[bw["player"] == name]
                if row.empty:
                    row = bowling_table(f[f["bowler"] == name])
                if not row.empty:
                    r = row.iloc[0]
                    compare_rows.append({
                        "Bowler": name,
                        "Wickets": r["wickets"],
                        "Economy": r["economy"],
                        "Bowling average": r["bowling_average"],
                        "Strike rate": r["strike_rate"],
                        "Dot-ball %": r["dot_ball_pct"],
                        "Legal balls": r["legal_balls"]
                    })

            if compare_rows:
                st.dataframe(
                    pd.DataFrame(compare_rows).round(2),
                    width="stretch",
                    hide_index=True
                )

        st.markdown("#### Economy by innings phase")

        phase_bowling = f.copy()
        phase_bowling["bowler_runs_conceded"] = (
            phase_bowling["total_runs"]
            - phase_bowling["byes"]
            - phase_bowling["legbyes"]
            - phase_bowling["penalty"]
        )

        phase_summary = (
            phase_bowling.groupby(["bowler", "phase"], as_index=False)
            .agg(
                runs_conceded=("bowler_runs_conceded", "sum"),
                legal_balls=("legal_ball", "sum"),
                wickets=("is_bowler_credited_wicket", "sum")
            )
        )

        phase_summary = phase_summary[phase_summary["legal_balls"] > 0]
        phase_summary["economy"] = (
            6 * phase_summary["runs_conceded"] / phase_summary["legal_balls"]
        )

        selected_bowlers = st.multiselect(
            "Select bowlers for phase comparison",
            sorted(phase_summary["bowler"].dropna().unique()),
            default=sorted(phase_summary["bowler"].dropna().unique())[:5],
            key="phase_bowlers"
        )

        phase_view = phase_summary[
            phase_summary["bowler"].isin(selected_bowlers)
        ]

        if not phase_view.empty:
            st.plotly_chart(
                px.bar(
                    phase_view,
                    x="phase",
                    y="economy",
                    color="bowler",
                    barmode="group",
                    title="Bowling economy by phase"
                ),
                width="stretch"
            )
        else:
            st.info("Select at least one bowler to view phase comparisons.")
    else:
        st.info("No bowlers meet the current minimum-ball threshold.")

with tabs[3]:
    st.subheader("Batter vs bowler")
    batter_options = sorted(f["striker"].dropna().unique())
    bowler_options = sorted(f["bowler"].dropna().unique())
    x,y = st.columns(2)
    batter = x.selectbox("Batter", batter_options, index=batter_options.index("RG Sharma") if "RG Sharma" in batter_options else 0)
    bowler = y.selectbox("Bowler", bowler_options)
    md = f[(f.striker==batter)&(f.bowler==bowler)]
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Runs off bat", int(md.runs_off_bat.sum()))
    m2.metric("Legal balls", int(md.legal_ball.sum()))
    m3.metric("Dismissals recorded", int(md.player_dismissed.notna().sum()))
    m4.metric("Matches", int(md.match_id.nunique()))
    if len(md):
        st.dataframe(md[["season","start_date","innings","ball","runs_off_bat","extras","wicket_type","player_dismissed"]], width="stretch", hide_index=True)
    else:
        st.info("No deliveries found for this batter–bowler pair under the current filters.")
    st.caption("Use sample size and context when interpreting head-to-head results.")

    st.divider()
    st.subheader("Advanced Batter vs Bowler Intelligence")
    st.caption(
        "Explore head-to-head results from the delivery data currently loaded. "
        "Use the ball count to judge how much evidence supports each matchup."
    )

    required = {
        "striker", "bowler", "runs_off_bat", "match_id",
        "is_legal_ball", "player_dismissed", "wicket_type",
    }

    if not required.issubset(f.columns):
        st.warning("Some required batter-bowler columns are unavailable.")
    elif f.empty:
        st.info("No delivery data is available under the current filters.")
    else:
        matchup_data = f.copy()
        matchup_data["runs_off_bat"] = pd.to_numeric(
            matchup_data["runs_off_bat"], errors="coerce"
        ).fillna(0)
        matchup_data["is_legal_ball"] = pd.to_numeric(
            matchup_data["is_legal_ball"], errors="coerce"
        ).fillna(0)

        batters = sorted(matchup_data["striker"].dropna().unique().tolist())
        bowlers = sorted(matchup_data["bowler"].dropna().unique().tolist())

        left, right = st.columns(2)
        with left:
            chosen_batter = st.selectbox(
                "Choose batter",
                batters,
                key="matchup_intel_batter",
            )
        with right:
            chosen_bowler = st.selectbox(
                "Choose bowler",
                bowlers,
                key="matchup_intel_bowler",
            )

        pair = matchup_data[
            (matchup_data["striker"] == chosen_batter)
            & (matchup_data["bowler"] == chosen_bowler)
        ].copy()

        legal_balls = int(pair["is_legal_ball"].sum())
        batter_runs = int(pair["runs_off_bat"].sum())
        dismissal_rows = pair[
            pair["player_dismissed"].fillna("").astype(str).str.strip().ne("")
        ]
        batter_dismissals = int(
            (dismissal_rows["player_dismissed"] == chosen_batter).sum()
        )
        fours = int(pair["is_boundary_four"].sum()) if "is_boundary_four" in pair.columns else 0
        sixes = int(pair["is_boundary_six"].sum()) if "is_boundary_six" in pair.columns else 0
        strike_rate = batter_runs / legal_balls * 100 if legal_balls else 0
        average = batter_runs / batter_dismissals if batter_dismissals else None

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Balls", f"{legal_balls:,}")
        c2.metric("Batter runs", f"{batter_runs:,}")
        c3.metric("Strike rate", f"{strike_rate:.1f}")
        c4.metric("Dismissals", f"{batter_dismissals}")
        c5.metric("Average", f"{average:.1f}" if average is not None else "N/A")

        st.caption(
            f"Head-to-head: {chosen_batter} vs {chosen_bowler} · "
            f"{fours} fours · {sixes} sixes"
        )

        if legal_balls < 12:
            st.warning(
                "Small sample: fewer than 12 legal balls. Treat this matchup "
                "as descriptive, not conclusive."
            )
        elif legal_balls < 30:
            st.info("Moderate sample. Interpret the matchup with caution.")

        st.markdown("#### Dismissal Breakdown")
        if not dismissal_rows.empty:
            dismissal_summary = (
                dismissal_rows["wicket_type"]
                .fillna("Unspecified")
                .replace("", "Unspecified")
                .value_counts()
                .rename_axis("Dismissal type")
                .reset_index(name="Dismissals")
            )
            fig_dismissals = px.bar(
                dismissal_summary,
                x="Dismissal type",
                y="Dismissals",
                title=f"Dismissals of {chosen_batter} against {chosen_bowler}",
                text="Dismissals",
            )
            st.plotly_chart(fig_dismissals, use_container_width=True)
        else:
            st.info("No recorded dismissals for this batter-bowler pairing.")

        st.markdown("#### Matchup Leaderboard")
        minimum_balls = st.slider(
            "Minimum legal balls per matchup",
            min_value=6,
            max_value=60,
            value=12,
            step=6,
            key="matchup_minimum_balls",
        )

        leaderboard = (
            matchup_data.groupby(["striker", "bowler"], dropna=True)
            .agg(
                Legal_balls=("is_legal_ball", "sum"),
                Batter_runs=("runs_off_bat", "sum"),
                Matches=("match_id", "nunique"),
            )
            .reset_index()
        )

        dismissed_pairs = dismissal_rows if False else matchup_data[
            matchup_data["player_dismissed"].fillna("").astype(str).str.strip().ne("")
        ]
        dismissed_pairs = dismissed_pairs[
            dismissed_pairs["player_dismissed"] == dismissed_pairs["striker"]
        ].groupby(["striker", "bowler"]).size().rename("Dismissals").reset_index()

        leaderboard = leaderboard.merge(
            dismissed_pairs, on=["striker", "bowler"], how="left"
        )
        leaderboard["Dismissals"] = leaderboard["Dismissals"].fillna(0)
        leaderboard = leaderboard[leaderboard["Legal_balls"] >= minimum_balls].copy()
        leaderboard["Strike_rate"] = (
            100 * leaderboard["Batter_runs"]
            / leaderboard["Legal_balls"].replace(0, np.nan)
        )
        leaderboard["Runs_per_legal_ball"] = (
            leaderboard["Batter_runs"]
            / leaderboard["Legal_balls"].replace(0, np.nan)
        )

        if leaderboard.empty:
            st.info("No batter-bowler pairings meet the minimum-ball threshold.")
        else:
            st.markdown("**Lowest scoring rate — batter versus bowler**")
            st.dataframe(
                leaderboard.sort_values(
                    ["Runs_per_legal_ball", "Dismissals"],
                    ascending=[True, False],
                ).head(15).round(2),
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("**Most dismissals — batter versus bowler**")
            st.dataframe(
                leaderboard.sort_values(
                    ["Dismissals", "Legal_balls"],
                    ascending=[False, False],
                ).head(15).round(2),
                use_container_width=True,
                hide_index=True,
            )

            fig_matchups = px.scatter(
                leaderboard,
                x="Legal_balls",
                y="Strike_rate",
                size="Dismissals",
                color="Runs_per_legal_ball",
                hover_name="striker",
                hover_data=["bowler", "Batter_runs", "Matches", "Dismissals"],
                title="Batter-Bowler Matchup Map",
                labels={
                    "Legal_balls": "Legal balls",
                    "Strike_rate": "Batter strike rate",
                    "Runs_per_legal_ball": "Runs per legal ball",
                    "Dismissals": "Dismissals",
                },
            )
            st.plotly_chart(fig_matchups, use_container_width=True)

with tabs[4]:
    st.subheader("Team and Tactical Phase Analysis")

    phase = (
        f.groupby(["batting_team", "phase"])
        .agg(
            runs=("total_runs", "sum"),
            legal_balls=("legal_ball", "sum"),
            wickets=("is_wicket", "sum"),
            matches=("match_id", "nunique")
        )
        .reset_index()
    )
    phase["run_rate"] = np.where(
        phase["legal_balls"] > 0,
        6 * phase["runs"] / phase["legal_balls"],
        np.nan
    )

    st.plotly_chart(
        px.bar(
            phase, x="batting_team", y="run_rate",
            color="phase", barmode="group",
            title="Team Run Rate by Innings Phase"
        ),
        width="stretch"
    )
    st.dataframe(
        phase.sort_values(["batting_team", "phase"]),
        width="stretch", hide_index=True
    )

    wicket_types = (
        f[f["wicket_type"].fillna("").astype(str).ne("")]
        .groupby("wicket_type")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    st.plotly_chart(
        px.bar(wicket_types, x="wicket_type", y="count",
               title="Dismissal Types"),
        width="stretch"
    )

    st.divider()
    st.subheader("Team Results Intelligence")

    required = {"match_id", "teams", "winner"}
    if required.issubset(matches.columns):
        results = matches.copy()
        results["season"] = results["season"].astype(str)

        if "super_over" in results.columns:
            results = results[
                ~results["super_over"].astype(str).str.lower()
                .isin(["true", "1", "yes"])
            ]

        if "method" in results.columns:
            results = results[results["method"].isna()]

        results = results.dropna(subset=["winner", "teams"]).copy()
        results["teams"] = results["teams"].astype(str)
        results = results[
            results["teams"].apply(
                lambda value: len(value.split("|")) == 2
            )
        ]

        team_rows = []
        for _, match in results.iterrows():
            participants = [
                team.strip() for team in match["teams"].split("|")
            ]
            winner = str(match["winner"]).strip()

            if winner not in participants:
                continue

            for team in participants:
                if team not in selected_teams:
                    continue

                team_rows.append({
                    "match_id": match["match_id"],
                    "season": str(match["season"]),
                    "team": team,
                    "won": int(team == winner),
                    "toss_won": (
                        str(match.get("toss_winner", "")).strip() == team
                    ),
                    "toss_decision": match.get("toss_decision")
                })

        team_results = pd.DataFrame(team_rows)

        if not team_results.empty:
            team_summary = (
                team_results.groupby("team")
                .agg(
                    matches=("match_id", "nunique"),
                    wins=("won", "sum")
                )
                .reset_index()
            )
            team_summary["losses"] = (
                team_summary["matches"] - team_summary["wins"]
            )
            team_summary["win_pct"] = (
                100 * team_summary["wins"] / team_summary["matches"]
            )

            st.markdown("#### Team win percentage")
            sorted_teams = team_summary.sort_values(
                "win_pct", ascending=False
            )
            st.plotly_chart(
                px.bar(
                    sorted_teams, x="team", y="win_pct",
                    hover_data=["matches", "wins", "losses"],
                    title="Win Percentage by Team",
                    labels={"team": "Team", "win_pct": "Win percentage (%)"}
                ),
                width="stretch"
            )
            st.dataframe(
                sorted_teams.round(2), width="stretch", hide_index=True
            )

            st.markdown("#### Season-by-season team performance")
            season_summary = (
                team_results.groupby(["season", "team"])
                .agg(
                    matches=("match_id", "nunique"),
                    wins=("won", "sum")
                )
                .reset_index()
            )
            season_summary["win_pct"] = (
                100 * season_summary["wins"] / season_summary["matches"]
            )
            st.plotly_chart(
                px.line(
                    season_summary, x="season", y="win_pct",
                    color="team", markers=True,
                    title="Team Win Percentage Across Seasons",
                    labels={"season": "Season",
                            "win_pct": "Win percentage (%)"}
                ),
                width="stretch"
            )

            st.markdown("#### Toss winner match outcomes")
            toss_results = team_results[team_results["toss_won"]].copy()

            if not toss_results.empty:
                toss_summary = (
                    toss_results.groupby("toss_decision")
                    .agg(
                        toss_wins=("match_id", "nunique"),
                        match_wins=("won", "sum")
                    )
                    .reset_index()
                )
                toss_summary["match_win_pct"] = (
                    100 * toss_summary["match_wins"]
                    / toss_summary["toss_wins"]
                )
                st.plotly_chart(
                    px.bar(
                        toss_summary, x="toss_decision",
                        y="match_win_pct", text="match_win_pct",
                        title="Match Win Percentage After Winning Toss",
                        labels={"toss_decision": "Toss decision",
                                "match_win_pct": "Match win percentage (%)"}
                    ),
                    width="stretch"
                )
                st.dataframe(
                    toss_summary.round(2),
                    width="stretch", hide_index=True
                )
        else:
            st.info("No completed match results found for selected teams.")
    else:
        st.info("Required match-result columns are missing.")


    st.subheader("Chasing vs Defending Intelligence")

    # Use match results and delivery data to identify each innings' batting team.
    # IPL matches can have incomplete or unusual results, so only count matches
    # with a known winner and identifiable batting-first team.
    if {"match_id", "innings", "batting_team"}.issubset(df.columns):
        first_innings = (
            df[df["innings"] == 1]
            .sort_values(["match_id"])
            .groupby("match_id", as_index=False)
            .first()[["match_id", "batting_team"]]
            .rename(columns={"batting_team": "batting_first"})
        )

        match_results = matches.copy()
        match_results["winner"] = match_results["winner"].astype("string").str.strip()
        match_results["toss_winner"] = match_results["toss_winner"].astype("string").str.strip()

        strategy = match_results.merge(first_innings, on="match_id", how="inner")
        strategy = strategy[
            strategy["winner"].notna()
            & strategy["winner"].ne("")
            & strategy["batting_first"].notna()
        ].copy()

        strategy = strategy[
            ~strategy["winner"].str.lower().isin(["nan", "no result", "tie"])
        ]

        strategy["batting_second"] = strategy.apply(
            lambda row: next(
                (
                    team.strip()
                    for team in str(row.get("teams", "")).split("|")
                    if team.strip() and team.strip() != row["batting_first"]
                ),
                None,
            ),
            axis=1,
        )

        strategy = strategy[strategy["batting_second"].notna()].copy()
        strategy["first_innings_win"] = strategy["winner"] == strategy["batting_first"]
        strategy["chasing_win"] = strategy["winner"] == strategy["batting_second"]

        if not strategy.empty:
            first_wins = int(strategy["first_innings_win"].sum())
            chase_wins = int(strategy["chasing_win"].sum())
            total_decided = len(strategy)

            c1, c2, c3 = st.columns(3)
            c1.metric("Matches analysed", f"{total_decided:,}")
            c2.metric(
                "Batting-first wins",
                f"{first_wins:,}",
                f"{first_wins / total_decided:.1%} of analysed matches",
            )
            c3.metric(
                "Chasing wins",
                f"{chase_wins:,}",
                f"{chase_wins / total_decided:.1%} of analysed matches",
            )

            overall = pd.DataFrame({
                "Strategy": ["Batting first", "Chasing"],
                "Wins": [first_wins, chase_wins],
                "Win rate (%)": [
                    first_wins / total_decided * 100,
                    chase_wins / total_decided * 100,
                ],
            })

            fig_strategy = px.bar(
                overall,
                x="Strategy",
                y="Win rate (%)",
                text="Win rate (%)",
                color="Strategy",
                title="Overall Win Rate: Batting First vs Chasing",
            )
            fig_strategy.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_strategy.update_layout(yaxis_range=[0, 100], showlegend=False)
            st.plotly_chart(fig_strategy, use_container_width=True)

            season_strategy = (
                strategy.groupby("season", dropna=True)
                .agg(
                    Matches=("match_id", "nunique"),
                    Batting_first_wins=("first_innings_win", "sum"),
                    Chasing_wins=("chasing_win", "sum"),
                )
                .reset_index()
            )
            season_strategy["Batting first win rate (%)"] = (
                season_strategy["Batting_first_wins"] / season_strategy["Matches"] * 100
            )
            season_strategy["Chasing win rate (%)"] = (
                season_strategy["Chasing_wins"] / season_strategy["Matches"] * 100
            )

            season_long = season_strategy.melt(
                id_vars=["season", "Matches"],
                value_vars=[
                    "Batting first win rate (%)",
                    "Chasing win rate (%)",
                ],
                var_name="Strategy",
                value_name="Win rate (%)",
            )
            fig_season_strategy = px.line(
                season_long,
                x="season",
                y="Win rate (%)",
                color="Strategy",
                markers=True,
                hover_data=["Matches"],
                title="Batting First vs Chasing Win Rate by Season",
            )
            fig_season_strategy.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig_season_strategy, use_container_width=True)

            team_strategy = (
                strategy.melt(
                    id_vars=["match_id", "season"],
                    value_vars=["batting_first", "batting_second"],
                    var_name="innings_role",
                    value_name="team",
                )
                .assign(
                    won=lambda x: (
                        (x["innings_role"] == "batting_first")
                        & x["match_id"].isin(
                            strategy.loc[strategy["first_innings_win"], "match_id"]
                        )
                    )
                    | (
                        (x["innings_role"] == "batting_second")
                        & x["match_id"].isin(
                            strategy.loc[strategy["chasing_win"], "match_id"]
                        )
                    )
                )
            )

            team_strategy_summary = (
                team_strategy.groupby(["team", "innings_role"])
                .agg(Matches=("match_id", "nunique"), Wins=("won", "sum"))
                .reset_index()
            )
            team_strategy_summary["Win rate (%)"] = (
                team_strategy_summary["Wins"] / team_strategy_summary["Matches"] * 100
            )

            team_strategy_pivot = team_strategy_summary.pivot(
                index="team", columns="innings_role", values="Win rate (%)"
            ).rename(columns={
                "batting_first": "Batting first win rate (%)",
                "batting_second": "Chasing win rate (%)",
            }).reset_index()

            if "Batting first win rate (%)" in team_strategy_pivot.columns:
                team_strategy_pivot = team_strategy_pivot.sort_values(
                    "Chasing win rate (%)", ascending=False
                )

            st.markdown("#### Team-wise Strategy Performance")
            st.caption(
                "Win rates use matches with a recorded winner and an identifiable "
                "first-innings batting team. Abandoned/no-result matches are excluded."
            )
            st.dataframe(
                team_strategy_pivot.round(1),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No completed matches with identifiable innings and winner data were found.")
    else:
        st.warning("Required match or innings columns are missing from the loaded data.")

with tabs[5]:
    st.subheader("Filtered delivery explorer")
    cols = [c for c in ["season","start_date","match_id","innings","ball","batting_team","bowling_team","striker","non_striker","bowler","runs_off_bat","extras","total_runs","wicket_type","player_dismissed","phase"] if c in f.columns]
    search = st.text_input("Search player, team, or bowler")
    view = f[cols].copy()
    if search:
        mask = view.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        view = view[mask]
    st.dataframe(view, width="stretch", hide_index=True)
    st.download_button("Download filtered deliveries CSV", view.to_csv(index=False).encode("utf-8"), "ipl_filtered_deliveries.csv", "text/csv")

with st.expander("Advanced Match & Venue Intelligence", expanded=False):
    st.subheader("Venue scoring intelligence")

    if "venue" in matches.columns:
        venue_options = sorted(matches["venue"].dropna().astype(str).unique())
        selected_venues = st.multiselect(
            "Select venues",
            venue_options,
            default=venue_options[:min(10, len(venue_options))],
            key="advanced_venues"
        )

        venue_data = matches[
            matches["venue"].astype(str).isin(selected_venues)
        ].copy()

        if not venue_data.empty:
            st.dataframe(
                venue_data.groupby("venue").agg(
                    matches=("match_id", "nunique")
                ).reset_index().sort_values("matches", ascending=False),
                width="stretch",
                hide_index=True
            )
        else:
            st.info("Select at least one venue.")
    else:
        st.info("The matches dataset has no venue column.")

    st.divider()
    st.subheader("Toss and match outcomes")

    required = {"toss_winner", "toss_decision", "winner"}
    if required.issubset(matches.columns):
        toss_data = matches.dropna(
            subset=["toss_winner", "toss_decision", "winner"]
        ).copy()

        toss_data["toss_winner_won"] = (
            toss_data["toss_winner"] == toss_data["winner"]
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Matches with recorded toss/outcome", len(toss_data))
        c2.metric(
            "Toss winners who also won",
            f"{toss_data['toss_winner_won'].mean() * 100:.1f}%"
            if len(toss_data) else "N/A"
        )
        c3.metric(
            "Matches won by toss losers",
            int((~toss_data["toss_winner_won"]).sum())
        )

        if not toss_data.empty:
            toss_summary = (
                toss_data.groupby("toss_decision")
                .agg(
                    matches=("match_id", "nunique"),
                    toss_winner_wins=("toss_winner_won", "sum")
                )
                .reset_index()
            )
            toss_summary["toss_winner_win_pct"] = (
                100 * toss_summary["toss_winner_wins"]
                / toss_summary["matches"]
            )

            st.plotly_chart(
                px.bar(
                    toss_summary,
                    x="toss_decision",
                    y="toss_winner_win_pct",
                    text="toss_winner_win_pct",
                    title="Toss Winner's Match-Win Percentage by Decision"
                ),
                width="stretch"
            )
            st.dataframe(toss_summary, width="stretch", hide_index=True)
    else:
        st.info("Toss or winner columns are missing from the match dataset.")

st.markdown("---")
st.caption("Data source: Cricsheet IPL New CSV archive. Shot type, line/length, and wagon-wheel location are not present in this source.")
