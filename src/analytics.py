import pandas as pd
import numpy as np

DISMISSALS = {
    "bowled", "caught", "caught and bowled", "lbw", "stumped",
    "hit wicket", "hit the ball twice", "handled the ball", "obstructing the field"
}

def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    for c in ["runs_off_bat", "extras", "wides", "noballs", "byes", "legbyes", "penalty"]:
        if c not in d:
            d[c] = 0
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    d["total_runs"] = d["runs_off_bat"] + d["extras"]
    d["is_legal_ball"] = (d["wides"] == 0) & (d["noballs"] == 0)
    d["legal_ball"] = d["is_legal_ball"].astype(int)
    d["is_boundary_four"] = (d["runs_off_bat"] == 4)
    d["is_boundary_six"] = (d["runs_off_bat"] == 6)
    d["is_dot_ball_batter"] = (d["runs_off_bat"] == 0)
    d["is_wicket"] = d["wicket_type"].fillna("").astype(str).str.strip().ne("")
    d["is_bowler_credited_wicket"] = d["wicket_type"].fillna("").str.lower().isin(DISMISSALS)
    d["over_number"] = pd.to_numeric(d["ball"].astype(str).str.split(".").str[0], errors="coerce").fillna(0).astype(int) + 1
    d["phase"] = np.select(
        [d["over_number"] <= 6, d["over_number"] <= 15],
        ["Powerplay (1–6)", "Middle (7–15)"],
        default="Death (16+)"
    )
    d["season"] = d["season"].astype(str)
    return d

def batting_table(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("striker", dropna=False).agg(
        runs=("runs_off_bat", "sum"),
        balls_faced=("is_legal_ball", "sum"),
        fours=("is_boundary_four", "sum"),
        sixes=("is_boundary_six", "sum"),
        dot_deliveries=("is_dot_ball_batter", "sum"),
        dismissals=("player_dismissed", lambda x: x.notna().sum()),
        innings=("innings_key", "nunique"),
        matches=("match_id", "nunique")
    ).reset_index().rename(columns={"striker": "player"})
    g["strike_rate"] = np.where(g.balls_faced > 0, 100 * g.runs / g.balls_faced, np.nan)
    g["average"] = np.where(g.dismissals > 0, g.runs / g.dismissals, np.nan)
    g["boundary_runs_pct"] = np.where(g.runs > 0, 100 * (4*g.fours + 6*g.sixes) / g.runs, np.nan)
    g["dot_ball_pct"] = np.where(g.balls_faced > 0, 100 * g.dot_deliveries / g.balls_faced, np.nan)
    return g.sort_values("runs", ascending=False)

def bowling_table(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["bowler_runs_conceded"] = d["total_runs"] - d["byes"] - d["legbyes"] - d["penalty"]
    g = d.groupby("bowler", dropna=False).agg(
        runs_conceded=("bowler_runs_conceded", "sum"),
        legal_balls=("legal_ball", "sum"),
        wickets=("is_bowler_credited_wicket", "sum"),
        matches=("match_id", "nunique"),
        dot_balls=("total_runs", lambda x: (x == 0).sum()),
        fours_conceded=("runs_off_bat", lambda x: (x == 4).sum()),
        sixes_conceded=("runs_off_bat", lambda x: (x == 6).sum())
    ).reset_index().rename(columns={"bowler": "player"})
    g["overs"] = g["legal_balls"] / 6
    g["economy"] = np.where(g.legal_balls > 0, g.runs_conceded * 6 / g.legal_balls, np.nan)
    g["bowling_average"] = np.where(g.wickets > 0, g.runs_conceded / g.wickets, np.nan)
    g["strike_rate"] = np.where(g.wickets > 0, g.legal_balls / g.wickets, np.nan)
    g["dot_ball_pct"] = np.where(g.legal_balls > 0, 100*g.dot_balls/g.legal_balls, np.nan)
    return g.sort_values("wickets", ascending=False)

def matchup_table(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["bowler_runs_conceded"] = d["total_runs"] - d["byes"] - d["legbyes"] - d["penalty"]
    g = d.groupby(["striker", "bowler"], dropna=False).agg(
        runs=("runs_off_bat", "sum"),
        balls=("is_legal_ball", "sum"),
        total_deliveries=("match_id", "size"),
        wickets=("player_dismissed", lambda x: x.notna().sum()),
        matches=("match_id", "nunique"),
        bowler_conceded=("bowler_runs_conceded", "sum")
    ).reset_index()
    g["strike_rate"] = np.where(g.balls > 0, 100*g.runs/g.balls, np.nan)
    return g.sort_values(["matches", "balls"], ascending=False)

def season_team_table(df: pd.DataFrame) -> pd.DataFrame:
    # Match-level results are sourced from the info CSVs, not inferred from deliveries.
    return df.groupby(["season", "batting_team"]).agg(
        runs=("total_runs", "sum"),
        batter_runs=("runs_off_bat", "sum"),
        deliveries=("match_id", "size"),
        wickets=("is_wicket", "sum"),
        matches=("match_id", "nunique")
    ).reset_index()
