import sqlite3
import pandas as pd


def save_dfinfo_to_sqlite(
    dfinfo: pd.DataFrame,
    conn: sqlite3.Connection,
    table_name: str = "dfinfo",
) -> None:
    dfinfo.to_sql(
        name=table_name,
        con=conn,
        if_exists="replace",
        index=False,
    )


def load_dfinfo_from_sqlite(
    conn: sqlite3.Connection,
    table_name: str = "dfinfo",
) -> pd.DataFrame:
    return pd.read_sql(
        f"SELECT * FROM {table_name}",
        conn,
    )