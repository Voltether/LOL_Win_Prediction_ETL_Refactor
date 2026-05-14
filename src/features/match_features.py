from src.data.riot_api import get_participant_info, get_team_gold_difference, get_team_kills_at_10, get_winner

def build_match_row(match_id, match_data, timeline_data, puuid):
    """
    Construye una fila de métricas para un match específico.
    """

    participant_id, team_id = get_participant_info(
        match_data,
        puuid,
        mode="both"
    )

    if not participant_id:
        raise ValueError("PUUID no encontrado en la partida.")

    player_info = next(
        (p for p in match_data["info"]["participants"] if p["puuid"] == puuid),
        None
    )

    if not player_info:
        raise ValueError("No se encontró información del jugador.")

    my_team_win = player_info["win"]

    gold_info = get_team_gold_difference(timeline_data, team_id)
    if not gold_info:
        raise ValueError("No se pudo obtener información de oro.")

    kill_info = get_team_kills_at_10(timeline_data, team_id)
    if not kill_info:
        raise ValueError("No se pudo obtener información de kills.")

    my_team_ahead_kills = (
        (team_id == 100 and kill_info["kill_diff"] > 0) or
        (team_id == 200 and kill_info["kill_diff"] < 0)
    )

    my_team_ahead_gold = (
        (team_id == 100 and gold_info["leading_team"] == 1) or
        (team_id == 200 and gold_info["leading_team"] == 2)
    )

    winner = get_winner(match_data)

    return {
        "match_id": match_id,
        "my_team": team_id,

        "team1_gold": gold_info["team1_gold"],
        "team2_gold": gold_info["team2_gold"],
        "gold_diff": gold_info["difference"],
        "gold_leading_team": gold_info["leading_team_id"],
        "my_team_ahead_gold": my_team_ahead_gold,

        "team1_kills": kill_info["team1_kills"],
        "team2_kills": kill_info["team2_kills"],
        "kill_diff": kill_info["kill_diff"],
        "kill_leading_team": kill_info["kill_leading_team"],
        "my_team_ahead_kills": my_team_ahead_kills,

        "my_team_win": my_team_win,
        "winner": winner
    }

