from src.data.storage import load_existing_data
from src.data.riot_api import fetch_match_and_timeline
from src.features.match_features import build_match_row

def get_df_data(history, puuid, api_key, csv_path, sleep_seconds=1):
    """
    Procesa una lista de match_ids, obtiene métricas al minuto 10
    y devuelve un DataFrame actualizado.
    """

    data, existing_match_ids = load_existing_data(csv_path)

    for match_id in history:
        match_id = str(match_id)

        if match_id in existing_match_ids:
            print(f"[{match_id}] Ya estaba registrado, se omite.")
            continue

        try:
            match_data, timeline_data = fetch_match_and_timeline(
                match_id=match_id,
                api_key=api_key
            )

            row = build_match_row(
                match_id=match_id,
                match_data=match_data,
                timeline_data=timeline_data,
                puuid=puuid
            )

            data.append(row)
            existing_match_ids.add(match_id)

            print(f"[{match_id}] Procesado correctamente.")

            time.sleep(sleep_seconds)

        except Exception as e:
            print(f"[{match_id}] Error: {e}")

    df = pd.DataFrame(data)

    return df