from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import load_config, get_paths
from src.models.logreg_enriched import load_artifacts, predict_matches


def main() -> None:
    config = load_config()
    paths = get_paths(config)

    input_csv = paths["sample_enriched"]
    model_dir = Path(config["artifacts"]["model_dir"])
    output_path = Path(config["paths"]["predictions_csv"])

    output_path.parent.mkdir(parents=True, exist_ok=True)

    df_matches = pd.read_csv(input_csv)

    artifacts = load_artifacts(model_dir)

    predictions = predict_matches(
        df_matches=df_matches,
        artifacts=artifacts,
        match_id_col="match_id",
    )

    predictions.to_csv(output_path, index=False)

    print("Predicciones generadas correctamente")
    print(f"Input: {input_csv}")
    print(f"Output: {output_path}")
    print(f"Filas predichas: {len(predictions)}")


if __name__ == "__main__":
    main()