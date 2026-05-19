import sqlite3
from pathlib import Path


def get_sqlite_connection(db_path: str | Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(db_path)