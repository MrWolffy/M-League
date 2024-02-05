import os
import sqlite3
import pandas as pd

if "m-league.db" in os.listdir():
    os.remove("m-league.db")

con = sqlite3.connect("m-league.db")
cur = con.cursor()

data = pd.read_csv("m-league.csv")

# region create table teams
cur.execute("""
CREATE TABLE Team(
    team_name TEXT PRIMARY KEY 
)
""")
for item in data["team"].unique().tolist():
    cur.execute("INSERT INTO Team VALUES (?)", (item,))
con.commit()
# endregion

# region create table players
cur.execute("""
CREATE TABLE Player(
    player_name TEXT PRIMARY KEY 
)
""")
for item in data["player"].unique().tolist():
    cur.execute("INSERT INTO Player VALUES (?)", (item,))
con.commit()
# endregion

# region create table players_teams
cur.execute("""
CREATE TABLE Player_Team(
    player_name TEXT,
    team_name TEXT,
    season INTEGER,
    FOREIGN KEY (player_name) REFERENCES players(player_name),
    FOREIGN KEY (team_name) REFERENCES team(team_name)
)
""")
for _, item in data[["player", "team", "stage"]].drop_duplicates().iterrows():
    cur.execute("INSERT INTO Player_Team VALUES (?, ?, ?)", (item["player"], item["team"], int(item["stage"][:4])))
con.commit()
# endregion

# region create table matches
import time
import math
from collections import Counter

cur.execute("""
CREATE TABLE Match(
    match_year INTEGER,
    match_month INTEGER,
    match_day INTEGER,
    match_no INTEGER,
    round INTEGER
)
""")
for _, item in data[["date", "match_no", "round_no"]].drop_duplicates().iterrows():
    date_object = time.strptime(item["date"], "%Y/%m/%d")
    cur.execute("INSERT INTO Match VALUES (?, ?, ?, ?, ?)",
                (date_object.tm_year, date_object.tm_mon, date_object.tm_mday, item["match_no"], item["round_no"]))
con.commit()
# endregion

# region create table players_matches
cur.execute("""
CREATE TABLE Player_Match(
    match_id INTEGER,
    -- east player
    player_name_e TEXT,
    point_e INTEGER,
    rank_e INTEGER check (rank_e BETWEEN 1 AND 4),
    pt_e FLOAT,
    -- south player
    player_name_s TEXT,
    point_s INTEGER,
    rank_s INTEGER check (rank_s BETWEEN 1 AND 4),
    pt_s FLOAT,
    -- west player
    player_name_w TEXT,
    point_w INTEGER,
    rank_w INTEGER check (rank_w BETWEEN 1 AND 4),
    pt_w FLOAT,
    -- north player
    player_name_n TEXT,
    point_n INTEGER,
    rank_n INTEGER check (rank_n BETWEEN 1 AND 4),
    pt_n FLOAT,
    FOREIGN KEY (match_id) REFERENCES matches(rowid),
    FOREIGN KEY (player_name_e) REFERENCES players(player_name),
    FOREIGN KEY (player_name_s) REFERENCES players(player_name),
    FOREIGN KEY (player_name_w) REFERENCES players(player_name),
    FOREIGN KEY (player_name_n) REFERENCES players(player_name)
)
""")
# cur.execute("""
#     CREATE TRIGGER check_rank
#     BEFORE INSERT ON Player_Match
#     FOR EACH ROW
#     WHEN EXISTS(
#         SELECT *
#         FROM Player_Match
#         WHERE match_id = NEW.match_id
#             AND((NEW.point < point AND NEW.rank < rank) OR(NEW.point > point AND NEW.rank > rank))
#     )
#         BEGIN
#             SELECT RAISE(ABORT, 'Invalid rank. All players with higher points should have higher rank.');
#         END;
# """)

def validate_pt(point_e, point_s, point_w, point_n,
                rank_e, rank_s, rank_w, rank_n,
                pt_e, pt_s, pt_w, pt_n) -> bool:
    points = [point_e, point_s, point_w, point_n]
    ranks = [rank_e, rank_s, rank_w, rank_n]
    pts = [pt_e, pt_s, pt_w, pt_n]

    pts_calculated = [(point - 30000) / 1000 for point in points]
    bonus = {1: 50, 2: 10, 3: -10, 4: -30}
    rank_counter = Counter(ranks)

    if max(rank_counter.values()) == 1:
        for i in range(len(pts_calculated)):
            pts_calculated[i] += bonus[ranks[i]]
    elif max(rank_counter.values()) == 2:
        for i in range(len(pts_calculated)):
            if rank_counter[ranks[i]] == 2:
                pts_calculated[i] += (bonus[ranks[i]] + bonus[ranks[i]+1]) / 2
            else:
                pts_calculated[i] += bonus[ranks[i]]

    try:
        assert abs(pts[0] - pts_calculated[0]) < 0.001
        assert abs(pts[1] - pts_calculated[1]) < 0.001
        assert abs(pts[2] - pts_calculated[2]) < 0.001
        assert abs(pts[3] - pts_calculated[3]) < 0.001
    except AssertionError:
        return False
    return True

con.create_function("validate_pt", 12, validate_pt)
cur.execute("""
    CREATE TRIGGER check_pt
    BEFORE INSERT ON Player_Match
    FOR EACH ROW
    WHEN validate_pt(NEW.point_e, NEW.point_s, NEW.point_w, NEW.point_n, NEW.rank_e, NEW.rank_s, NEW.rank_w, NEW.rank_n, NEW.pt_e, NEW.pt_s, NEW.pt_w, NEW.pt_n) IS FALSE
        BEGIN
            SELECT RAISE(IGNORE);
        END;
""")
for identifier, item in data.groupby(["date", "match_no"]):
    date_object = time.strptime(identifier[0], "%Y/%m/%d")
    match_id = cur.execute("SELECT rowid FROM Match WHERE match_year = ? AND match_month = ? AND match_day = ? AND match_no = ?",
                           (date_object.tm_year, date_object.tm_mon, date_object.tm_mday, int(identifier[1]))).fetchone()[0]
    cur.execute("INSERT INTO Player_Match VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (match_id,
                 item.iloc[0]["player"], int(item.iloc[0]["point"]), int(item.iloc[0]["rank"]), item.iloc[0]["pt"],
                 item.iloc[1]["player"], int(item.iloc[1]["point"]), int(item.iloc[1]["rank"]), item.iloc[1]["pt"],
                 item.iloc[2]["player"], int(item.iloc[2]["point"]), int(item.iloc[2]["rank"]), item.iloc[2]["pt"],
                 item.iloc[3]["player"], int(item.iloc[3]["point"]), int(item.iloc[3]["rank"]), item.iloc[3]["pt"]))
    con.commit()
# endregion



con.close()