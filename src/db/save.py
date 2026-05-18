def save_matches_dataset(df, conn):
    df = df.drop_duplicates(subset=["match_id"])

    rows = df.to_dict(orient="records")
    cursor = conn.cursor()

    for row in rows:
        cursor.execute("""
            INSERT OR IGNORE INTO matches_dataset (
                match_id,
                my_team,

                team1_gold,
                team2_gold,
                gold_diff,
                gold_leading_team,
                my_team_ahead_gold,

                team1_kills,
                team2_kills,
                kill_diff,
                kill_leading_team,
                my_team_ahead_kills,

                tower_fb,
                drake_fb,
                herald_fb,

                my_team_win,
                winner
            )
            VALUES (
                :match_id,
                :my_team,

                :team1_gold,
                :team2_gold,
                :gold_diff,
                :gold_leading_team,
                :my_team_ahead_gold,

                :team1_kills,
                :team2_kills,
                :kill_diff,
                :kill_leading_team,
                :my_team_ahead_kills,

                :tower_fb,
                :drake_fb,
                :herald_fb,

                :my_team_win,
                :winner
            )
        """, row)

    conn.commit()