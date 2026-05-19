import pandas as pd


INFO_COLUMNS = [
    "gold_diff",
    "kill_diff",
    "my_team_tower_fb",
    "my_team_drake_fb",
    "my_team_herald_fb",
    "my_team_win",
]


def build_dfinfo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye el dataframe dfinfo usado para análisis exploratorio.

    Agrega flags binarios para saber si el equipo del jugador obtuvo
    first tower, first drake y first herald.
    """
    df = df.copy()

    required_columns = [
        "gold_diff",
        "kill_diff",
        "tower_fb",
        "drake_fb",
        "herald_fb",
        "my_team",
        "my_team_win",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Faltan columnas requeridas: {missing_columns}")

    df["my_team_tower_fb"] = (df["tower_fb"] == df["my_team"]).astype(int)
    df["my_team_drake_fb"] = (df["drake_fb"] == df["my_team"]).astype(int)
    df["my_team_herald_fb"] = (df["herald_fb"] == df["my_team"]).astype(int)

    return df[INFO_COLUMNS].copy()


def build_dfinfo_from_csv(input_path: str, output_path: str | None = None) -> pd.DataFrame:
    """
    Lee un CSV, construye dfinfo y opcionalmente lo guarda.
    """
    df = pd.read_csv(input_path)
    dfinfo = build_dfinfo(df)

    if output_path is not None:
        dfinfo.to_csv(output_path, index=False)

    return dfinfo