import requests
import pandas as pd
import os
from dotenv import load_dotenv
import time
from pathlib import Path


from src.data.riot_api import get_gm_ladder, get_chall_ladder, get_df_data, get_matchids, enrich_with_objectives
from src.config import load_config, load_api_key, get_paths

config = load_config()
api_key = load_api_key()
paths = get_paths(config)

riot_config = config["riot"]

queueid = riot_config["queueid"]
matchtype = riot_config["matchtype"]
start = riot_config["start"]
count = riot_config["count"]
sleep_seconds = riot_config["sleep_seconds"]

no_apex_ranks = ('IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND')
apex_ranks = ('MASTER', 'GRAND_MASTER', 'CHALLENGER')

gm_ladder = get_gm_ladder(api_key=api_key)
ch_ladder = get_chall_ladder(api_key=api_key)

apex_ladder = ch_ladder + gm_ladder

df_ladder = pd.DataFrame(data = apex_ladder, columns=['puuid_apex'])
df_ladder = pd.read_csv(paths["ladder_population"]) #De momento usamos csv, se planea migrar a una DB
df_ladder.to_csv(['ladder_population'], index=False)


df_ladder = pd.read_csv(paths['ladder_population'])  
ladder_list = list(df_ladder['puuid_apex'])

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
    
    time.sleep(1.7)

df_sample = pd.concat(all_dfs, ignore_index=True)
df_sample.drop_duplicates(subset=["match_id"], inplace=True)

df_sample.to_csv(paths["sample_matches"], index=False)
df = pd.read_csv(paths["sample_matches"])

df_enriched = enrich_with_objectives(df = df, api_key=api_key)
df_enriched.to_csv(paths['sample_enriched'], index = False)