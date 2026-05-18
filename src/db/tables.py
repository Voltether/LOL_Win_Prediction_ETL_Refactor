def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches_dataset (
            match_id TEXT PRIMARY KEY,
            my_team INTEGER,

            team1_gold INTEGER,
            team2_gold INTEGER,
            gold_diff INTEGER,
            gold_leading_team INTEGER,
            my_team_ahead_gold BOOLEAN,

            team1_kills INTEGER,
            team2_kills INTEGER,
            kill_diff INTEGER,
            kill_leading_team INTEGER,
            my_team_ahead_kills BOOLEAN,

            tower_fb INTEGER,
            drake_fb INTEGER,
            herald_fb INTEGER,

            my_team_win BOOLEAN,
            winner INTEGER
        )
    """)

    conn.commit()