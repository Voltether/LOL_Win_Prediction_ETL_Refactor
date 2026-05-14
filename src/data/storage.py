def load_existing_data(csv_path):
    """
    Carga datos existentes desde CSV si existe.
    Devuelve:
    - data: lista de registros
    - existing_match_ids: set de match_ids ya procesados
    """
    if not os.path.exists(csv_path):
        return [], set()

    df_old = pd.read_csv(csv_path)
    data = df_old.to_dict(orient="records")
    existing_match_ids = set(df_old["match_id"].astype(str))

    return data, existing_match_ids