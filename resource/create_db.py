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
CREATE TABLE teams(
    team_name text PRIMARY KEY 
)
""")
for item in data["team"].unique().tolist():
    cur.execute("INSERT INTO teams VALUES (?)", (item,))
con.commit()
# endregion

# region create table players
cur.execute("""
CREATE TABLE players(
    player_name text PRIMARY KEY 
)
""")
for item in data["player"].unique().tolist():
    cur.execute("INSERT INTO players VALUES (?)", (item,))
con.commit()
# endregion

# region create table players_teams
cur.execute("""
CREATE TABLE players_teams(
    player_name TEXT,
    team_name TEXT,
    season INTEGER,
    FOREIGN KEY (player_name) REFERENCES players(player_name),
    FOREIGN KEY (team_name) REFERENCES team(team_name)
)
""")
for _, item in data[["player", "team", "stage"]].drop_duplicates().iterrows():
    cur.execute("INSERT INTO players_teams VALUES (?, ?, ?)", (item["player"], item["team"], int(item["stage"][:4])))
con.commit()
# endregion

# region create table matches
import time

cur.execute("""
CREATE TABLE matches(
    match_year INTEGER,
    match_month INTEGER,
    match_day INTEGER,
    match_no INTEGER,
    round INTEGER,
    PRIMARY KEY (match_year, match_month, match_day, match_no)
)
""")
for _, item in data[["date", "match_no", "round_no"]].drop_duplicates().iterrows():
    date_object = time.strptime(item["date"], "%Y/%m/%d")
    cur.execute("INSERT INTO matches VALUES (?, ?, ?, ?, ?)",
                (date_object.tm_year, date_object.tm_mon, date_object.tm_mday, item["match_no"], item["round_no"]))
con.commit()
# endregion

# region create table players_matches
cur.execute("""
CREATE TABLE players_matches(
    match_year INTEGER,
    match_month INTEGER,
    match_day INTEGER,
    match_no INTEGER,
    player_name TEXT,
    point FLOAT,
    rank INTEGER check ( rank BETWEEN 1 AND 4),
    pt FLOAT,
    FOREIGN KEY (match_year) REFERENCES matches(match_year),
    FOREIGN KEY (match_month) REFERENCES matches(match_month),
    FOREIGN KEY (match_day) REFERENCES matches(match_day),
    FOREIGN KEY (match_no) REFERENCES matches(match_no),
    FOREIGN KEY (player_name) REFERENCES players(player_name)
)
""")
cur.execute("""
    CREATE TRIGGER check_rank
    BEFORE INSERT ON players_matches
    FOR EACH ROW
    WHEN EXISTS(
        SELECT * 
        FROM players_matches
        WHERE match_year = NEW.match_year
            AND match_month = NEW.match_month
            AND match_day = NEW.match_day
            AND match_no = NEW.match_no
            AND((NEW.point < point AND NEW.rank < rank) OR(NEW.point > point AND NEW.rank > rank))
    ) 
        BEGIN
            SELECT RAISE(ABORT, 'Invalid rank. All players with higher points should have higher rank.');
        END;
""")

def calculate_pt(point, rank):
    pt = (point - 30000) / 1000
    bonus = {1: 50, 2: 10, 3: -10, 4: -30}
    try:
        pt += bonus[rank]
    except KeyError:
        raise KeyError("Invalid rank.")
    return pt

con.create_function("calculate_pt", 2, calculate_pt)
# cur.execute("""
#     CREATE TRIGGER check_pt
#     BEFORE INSERT ON players_matches
#     FOR EACH ROW
#     WHEN ABS(calculate_pt(NEW.point, NEW.rank) - NEW.pt) > 0.001
#         BEGIN
#             SELECT RAISE(ABORT, 'Inconsistent pt.');
#         END;
# """)
for _, item in data.iterrows():
    date_object = time.strptime(item["date"], "%Y/%m/%d")
    cur.execute("insert into players_matches values (?, ?, ?, ?, ?, ?, ?, ?)",
                (date_object.tm_year, date_object.tm_mon, date_object.tm_mday, item["match_no"],
                 item["player"], item["point"], item["rank"], item["pt"]))
con.commit()
# endregion



con.close()