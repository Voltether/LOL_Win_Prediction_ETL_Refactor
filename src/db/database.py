from pathlib import Path
import sqlite3


def get_connection(db_path):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(db_path)