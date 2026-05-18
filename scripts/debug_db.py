# %%
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.config import load_config, get_paths
import sqlite3
import pandas as pd

config = load_config(PROJECT_ROOT / "config.yaml")
paths = get_paths(config)

conn = sqlite3.connect(paths["database"])

df = pd.read_sql("""
    SELECT *
    FROM matches_dataset
    LIMIT 5
""", conn)

print(df)

count = pd.read_sql("""
    SELECT COUNT(*) AS total
    FROM matches_dataset
""", conn)

print(count)

conn.close()
# %%
