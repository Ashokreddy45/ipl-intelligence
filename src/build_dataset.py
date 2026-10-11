from pathlib import Path
import zipfile, csv, io, sys
import pandas as pd
from analytics import add_derived_columns

ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "data" / "raw" / "ipl_csv2.zip"
OUT = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

def parse_info_csv(text):
    rows = list(csv.reader(io.StringIO(text)))
    info = {}
    players = []
    teams = []
    for row in rows:
        if not row:
            continue
        if row[0] == "info" and len(row) >= 3:
            key = row[1]
            vals = row[2:]
            if key == "player":
                if len(vals) >= 2:
                    players.append({"team": vals[0], "player": vals[1]})
            elif key == "team":
                teams.extend(vals)
            else:
                value = vals[0] if len(vals) == 1 else "|".join(vals)
                info[key] = value
    info["teams"] = " | ".join(teams)
    info["players_listed"] = len(players)
    return info, players

def main():
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Expected source archive at {ZIP_PATH}")
    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as z:
        names = z.namelist()
        ball_names = [n for n in names if n.endswith(".csv") and n.rsplit("/",1)[-1][:-4].isdigit()]
        info_names = [n for n in names if n.endswith("_info.csv")]
        balls = []
        infos = []
        roster = []
        for n in ball_names:
            df = pd.read_csv(z.open(n))
            if not df.empty:
                balls.append(df)
        for n in info_names:
            info, players = parse_info_csv(z.read(n).decode("utf-8-sig", errors="replace"))
            infos.append(info)
            for p in players:
                p["match_id"] = info.get("match_id", n.split("/")[-1].replace("_info.csv",""))
                roster.append(p)
    if not balls:
        raise ValueError("No ball-by-ball CSV files found in archive.")
    deliveries = pd.concat(balls, ignore_index=True)
    matches = pd.DataFrame(infos)
    roster_df = pd.DataFrame(roster)
    deliveries = add_derived_columns(deliveries)
    deliveries["innings_key"] = deliveries["match_id"].astype(str) + "-" + deliveries["innings"].astype(str)
    deliveries["player_dismissed"] = deliveries["player_dismissed"].replace("", pd.NA)
    deliveries["wicket_type"] = deliveries["wicket_type"].fillna("")
    deliveries["start_date"] = pd.to_datetime(deliveries["start_date"], errors="coerce")
    deliveries.to_csv(OUT / "deliveries.csv", index=False)
    matches.to_csv(OUT / "matches.csv", index=False)
    roster_df.to_csv(OUT / "rosters.csv", index=False)
    audit = []
    audit.append("# Data audit\n")
    audit.append(f"- Ball-by-ball files loaded: **{len(balls):,}**")
    audit.append(f"- Match information files loaded: **{len(info_names):,}**")
    audit.append(f"- Delivery rows: **{len(deliveries):,}**")
    audit.append(f"- Unique match IDs in deliveries: **{deliveries['match_id'].nunique():,}**")
    audit.append(f"- Seasons: **{deliveries['season'].nunique()}** ({deliveries['season'].min()}–{deliveries['season'].max()})")
    audit.append(f"- Unique batters: **{deliveries['striker'].nunique():,}**")
    audit.append(f"- Unique bowlers: **{deliveries['bowler'].nunique():,}**")
    audit.append(f"- Missing match IDs: **{deliveries['match_id'].isna().sum():,}**")
    audit.append(f"- Duplicate delivery records (all columns): **{deliveries.duplicated().sum():,}**")
    audit.append(f"- Missing striker values: **{deliveries['striker'].isna().sum():,}**")
    audit.append(f"- Missing bowler values: **{deliveries['bowler'].isna().sum():,}**")
    audit.append("\n## Rows by season\n")
    audit.append(deliveries.groupby("season").size().to_frame("deliveries").to_markdown())
    (REPORTS / "data_audit.md").write_text("\n".join(audit), encoding="utf-8")
    print("\n".join(audit))
    print(f"\nProcessed data written to {OUT}")

if __name__ == "__main__":
    main()
