import requests
import pandas as pd
import os
from dotenv import load_dotenv
import time
from pathlib import Path


from src.data.riot_api import get_gm_ladder, get_chall_ladder
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

no_apex_ranks = ('IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND')
apex_ranks = ('MASTER', 'GRAND_MASTER', 'CHALLENGER')

gm_ladder = get_gm_ladder(api_key=api_key)
ch_ladder = get_chall_ladder(api_key=api_key)

apex_ladder = ch_ladder + gm_ladder

df_ladder = pd.DataFrame(data=apex_ladder, columns=["puuid_apex"])
df_ladder.to_csv(paths["ladder_population"], index=False)
