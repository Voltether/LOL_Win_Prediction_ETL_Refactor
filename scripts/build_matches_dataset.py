import pandas as pd
import time
from src.db.database import get_connection
from src.db.tables import create_tables
from src.db.save import save_matches_dataset

from src.data.riot_api import get_df_data, get_matchids
from src.config import load_config, load_api_key, get_paths

config = load_config()
api_key = load_api_key()
paths = get_paths(config)

riot_config = config["riot"]
match_config = config["matches"]

queueid = match_config["queueid"]
matchtype = match_config["matchtype"]
start = match_config["start"]
count = match_config["count"]
sleep_seconds = match_config["sleep_seconds"]


df_ladder = pd.read_csv(paths["ladder_population"])

ladder_list = list(df_ladder["puuid_apex"])

all_dfs = []
seen_matches = set()

# matchid de cada jugador en ladder_list
for summ in ladder_list:
    matches = list(set(get_matchids(
        puuid=summ,
        queueid=queueid,
        matchtype=matchtype,
        start=start,
        count=count,
        api_key=api_key
    )))
    
    new_matches = [m for m in matches if m not in seen_matches]

    if not new_matches:
        continue

    # csv temporal
    df_sample_player = get_df_data(
        history=new_matches,
        puuid=summ,
        api_key=api_key,
        csv_path=paths["temp_matches"],
        sleep_seconds=sleep_seconds
)

    all_dfs.append(df_sample_player)
    seen_matches.update(new_matches)
    
    time.sleep(1.5)

if not all_dfs:
    raise ValueError(
        "No se generaron datos. Revisa ladder_list, get_matchids o filtros de matches."
    )

df_dataset = pd.concat(all_dfs, ignore_index=True)
df_dataset.drop_duplicates(subset=["match_id"], inplace=True)

df_dataset.to_csv(paths["sample_enriched"], index=False)

conn = get_connection(paths["database"])
create_tables(conn)
save_matches_dataset(df_dataset, conn)
conn.close()

print("Dataset enriquecido generado correctamente.")
print(df_dataset.shape)
