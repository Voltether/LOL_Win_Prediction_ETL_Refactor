import requests

def get_chall_ladder(api_key):
    """
    Devuelve una lista con los PUUIDs de Challenger (LAN, ranked solo 5x5).
    """
    link = f"https://la1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}"
    response = requests.get(link)
    leaguev4 = response.json()

    CHladder = list(set([summ['puuid'] for summ in leaguev4['entries']]))

    return CHladder


def get_gm_ladder(api_key):
    """
    Devuelve una lista con los PUUIDs de la mitad superior (~250) de GM (LAN, ranked solo 5x5).
    """
    link = f"https://la1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}"
    response = requests.get(link)
    leaguev4 = response.json()

    top_half = leaguev4["entries"][:250]

    GMladder = [summ['puuid'] for summ in top_half]

    return GMladder


def get_matchids (puuid=None, queueid=None, matchtype=None, start=None, count=None, api_key=None):
    """
    Obtiene el historial de partidas del jugador
    """

    link = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={queueid}&type={matchtype}&start={start}&count={count}&api_key={api_key}'

    response = requests.get(link)

    return response.json()

def get_participant_info(match_data, puuid, mode):
    """
    Regresa el participantid del jugador asociado al PUUID en cada partida y el teamid asociado al juagor, es decir,
    regresa el numero de jugador y en qué equipo estaba. Versión ampliada de get_participant_id
    """
    for i, participant_puuid in enumerate(match_data["metadata"]["participants"]):
        if participant_puuid == puuid:
            participant_id = i + 1
            team_id = match_data["info"]["participants"][i]["teamId"]  # 100 o 200
            
            if mode == "both":
                return str(participant_id), team_id
            elif mode == "team":
                return team_id
            elif mode == "participant":
                return str(participant_id)

    return None


def get_team_gold_difference(timeline_data, my_team):
    """
    Calcula el oro al minuto 10 de ambos equipos, su diferencia y el equipo líder.
    100 para azul y 200 para rojo.
    """
    frames = timeline_data["info"]["frames"]
    if len(frames) <= 10:
        return None

    frame_10 = frames[10]["participantFrames"]

    team1_gold = sum([frame_10[str(pid)]["totalGold"] for pid in range(1, 6)])
    team2_gold = sum([frame_10[str(pid)]["totalGold"] for pid in range(6, 11)])

    if my_team == 100:
        difference = team1_gold - team2_gold
    
    else:
        difference = team2_gold - team1_gold
        
    if team1_gold > team2_gold:
        leading_team_id = 100
        leading_team_name = "Azul (100)"
    elif team2_gold > team1_gold:
        leading_team_id = 200
        leading_team_name = "Rojo (200)"
    else:  # empate
        leading_team_id = 0
        leading_team_name = "Empate"

    return {
        "team1_gold": team1_gold,
        "team2_gold": team2_gold,
        "difference": difference,
        "leading_team": leading_team_name,
        "leading_team_id": leading_team_id
    }


def get_team_kills_at_10(timeline_data, my_team):
    """
    Calcula las kills globales del equipo 100 y 200 al minuto 10
    """
    frames = timeline_data["info"]["frames"]
    if len(frames) <= 10:
        return None
    
    team1_kills = 0
    team2_kills = 0

    for frame in frames[:11]:
        for event in frame.get("events", []):
            if event["type"] == "CHAMPION_KILL":
                killer_id = event.get("killerId", 0)
                if killer_id == 0:
                    continue  # torre, súbdito
                team = 100 if killer_id <= 5 else 200
                if team == 100:
                    team1_kills += 1
                else:
                    team2_kills += 1
    
    if my_team == 100:
        kill_difference = team1_kills - team2_kills

    else:
        kill_difference = team2_kills - team1_kills

    if team1_kills > team2_kills:
        kill_leading_team_id = int(100)
    elif team2_kills > team1_kills:
        kill_leading_team_id = int(200)
    else:
        kill_leading_team_id = 0

    return {
        "team1_kills": team1_kills,
        "team2_kills": team2_kills,
        "kill_diff": kill_difference,
        "kill_leading_team": kill_leading_team_id
    }


def get_winner(match_data):
    for team in match_data['info']['teams']:
        if team['win']:
            return team['teamId']
        

def fetch_match_and_timeline(match_id, api_key):
    """
    Descarga match_data y timeline_data desde Riot API.
    """
    base_url = "https://americas.api.riotgames.com/lol/match/v5/matches"

    match_url = f"{base_url}/{match_id}?api_key={api_key}"
    timeline_url = f"{base_url}/{match_id}/timeline?api_key={api_key}"

    match_response = requests.get(match_url)
    timeline_response = requests.get(timeline_url)

    match_response.raise_for_status()
    timeline_response.raise_for_status()

    return match_response.json(), timeline_response.json()
        

def get_df_data(history, puuid, api_key, csv_path):
    """
    Procesa una lista de match_ids (history), obtiene las métricas al min 10
    y devuelve un DataFrame. También actualiza/crea un CSV evitando duplicados.
    """

    if os.path.exists(csv_path):
        df_old = pd.read_csv(csv_path)
        data = df_old.to_dict(orient="records")
        existing_match_ids = {row["match_id"] for row in data}
    else:
        data = []
        existing_match_ids = set()

    for match_id in history:
        if match_id in existing_match_ids:
            print(f"[{match_id}] Ya estaba registrado, se omite.")
            continue

        try:
            # URLs
            match_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
            timeline_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline?api_key={api_key}"

            # Requests
            match_data = requests.get(match_url).json()
            timeline_data = requests.get(timeline_url).json()

            # Info del jugador
            participant_id, team_id = get_participant_info(match_data, puuid, mode = 'both')
            if not participant_id:
                print(f"[{match_id}] PUUID no encontrado.")
                continue

            my_team = get_participant_info(match_data, puuid, mode = 'team')

            # Determinar victoria
            player_info = next((p for p in match_data["info"]["participants"] if p["puuid"] == puuid), None)
            if not player_info:
                print(f"[{match_id}] No se encontró info del jugador.")
                continue
            my_team_win = player_info["win"]

            # Oro por equipo
            gold_info = get_team_gold_difference(timeline_data, my_team)
            if not gold_info:
                print(f"[{match_id}] Error al obtener oro de equipos.")
                continue

            # Kills por equipo
            kill_info = get_team_kills_at_10(timeline_data, my_team)
            if not kill_info:
                print(f"[{match_id}] Error al obtener kills")
                continue

            # Mi equipo
            my_team_label = 100 if team_id == 100 else 200
            my_team_was_ahead_kills = (team_id == 100 and kill_info['kill_diff'] > 0) or \
                                      (team_id == 200 and kill_info['kill_diff'] < 0)
            my_team_was_ahead_gold = (team_id == 100 and gold_info["leading_team"] == 1) or \
                                     (team_id == 200 and gold_info["leading_team"] == 2)

            # Ganador
            winner = get_winner(match_data)

            # Agregar info
            data.append({
                "match_id": match_id,
                "my_team": my_team_label,
                "team1_gold": gold_info["team1_gold"],
                "team2_gold": gold_info["team2_gold"],
                "gold_diff": gold_info["difference"],
                "gold_leading_team": gold_info["leading_team_id"],
                "my_team_ahead_gold": my_team_was_ahead_gold,
                "team1_kills": kill_info['team1_kills'],
                "team2_kills": kill_info['team2_kills'],
                "kill_diff": kill_info['kill_diff'],
                "kill_leading_team": kill_info['kill_leading_team'],
                "my_team_ahead_kills": my_team_was_ahead_kills,
                "my_team_win": my_team_win,
                "winner": winner
            })

            time.sleep(1)  

        except Exception as e:
            print(f"[{match_id}] Error: {e}")

    return data


def get_tower_fb(timeline_data):
    """
    Devuelve el teamId (100 o 200) que tiró la primera torre.
    Retorna None si no encuentra evento.
    """
    try:
        for frame in timeline_data["info"]["frames"]:
            for event in frame["events"]:
                if event["type"] == "BUILDING_KILL" and event["buildingType"] == "TOWER_BUILDING":
                    return event.get("teamId")  # 100 o 200
    except Exception as e:
        print(f"Error en get_tower_fb: {e}")
    return None


def get_drake_fb(timeline_data):
    """
    Devuelve el teamId (100 o 200) que mató el primer dragón.
    Retorna None si no encuentra evento.
    """
    try:
        for frame in timeline_data["info"]["frames"]:
            for event in frame["events"]:
                if event["type"] == "ELITE_MONSTER_KILL" and event.get("monsterType") == "DRAGON":
                    return event.get("killerTeamId")  # 100 o 200
    except Exception as e:
        print(f"Error en get_drake_fb: {e}")
    return None


def get_herald_fb(timeline_data):
    """
    Devuelve el teamId (100 o 200) que mató el primer heraldo.
    Retorna None si no encuentra evento.
    """
    try:
        for frame in timeline_data["info"]["frames"]:
            for event in frame["events"]:
                if event["type"] == "ELITE_MONSTER_KILL" and event.get("monsterType") == "RIFTHERALD":
                    return event.get("killerTeamId")  # 100 o 200
    except Exception as e:
        print(f"Error en get_herald_fb: {e}")
    return None


def enrich_with_objectives(df, api_key):
    """
    Enriquecer un DataFrame con primeras torres, dragones y heraldos.
    Agrega 3 columnas: tower_fb, drake_fb, herald_fb
    """
    objectives_data = []

    for match_id in df["match_id"]:
        try:
            # Obtener timeline
            timeline_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline?api_key={api_key}"
            timeline_data = requests.get(timeline_url).json()

            tower_fb = get_tower_fb(timeline_data)
            drake_fb = get_drake_fb(timeline_data)
            herald_fb = get_herald_fb(timeline_data)

            objectives_data.append({
                "match_id": match_id,
                "tower_fb": tower_fb,
                "drake_fb": drake_fb,
                "herald_fb": herald_fb
            })

            time.sleep(1.2)  # evitar rate limit

        except Exception as e:
            print(f"[{match_id}] Error en enrich_with_objectives: {e}")
            objectives_data.append({
                "match_id": match_id,
                "tower_fb": None,
                "drake_fb": None,
                "herald_fb": None
            })

    # Convertir en DataFrame
    df_obj = pd.DataFrame(objectives_data)

    # Merge con el original
    df_merged = df.merge(df_obj, on="match_id", how="left")

    # Reordenar columnas: insertar después de 'my_team_ahead_kills' y antes de 'my_team_win'
    cols = list(df_merged.columns)
    insert_at = cols.index("my_team_win")  # antes de my_team_win
    new_cols_order = (
        cols[:insert_at] +
        ["tower_fb", "drake_fb", "herald_fb"] +
        cols[insert_at:]
    )

    df_final = df_merged[new_cols_order]

    return df_final

