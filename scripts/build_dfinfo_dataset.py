from src.config import load_config, get_paths
from src.features.build_dfinfo import build_dfinfo_from_csv
from src.db.sqlite_connection import get_sqlite_connection
from src.db.dfinfo_repository import save_dfinfo_to_sqlite


def main() -> None:
    config = load_config()
    paths = get_paths(config)

    dfinfo = build_dfinfo_from_csv(
        input_path=paths["sample_enriched"],
        output_path=paths["dfinfo_csv"],
    )

    conn = get_sqlite_connection(paths["predictor_db"])

    try:
        save_dfinfo_to_sqlite(
            dfinfo=dfinfo,
            conn=conn,
            table_name="dfinfo_apex_enriched",
        )
    finally:
        conn.close()

    print("dfinfo generado correctamente")
    print(f"CSV guardado en: {paths['dfinfo_csv']}")
    print(f"SQLite guardado en: {paths['predictor_db']}")


if __name__ == "__main__":
    main()