from pathlib import Path
import yaml
from dotenv import load_dotenv
import os


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_api_key() -> str:
    load_dotenv()
    api_key = os.getenv("RIOT_API_KEY")

    if not api_key:
        raise ValueError("RIOT_API_KEY no está definida en el archivo .env")

    return api_key


def get_paths(config: dict) -> dict:
    interim_dir = Path(config["paths"]["interim_dir"])
    processed_dir = Path(config["paths"]["processed_dir"])

    interim_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    return {
        "interim_dir": interim_dir,
        "processed_dir": processed_dir,
        "ladder_population": interim_dir / config["files"]["ladder_population"],
        "sample_matches": interim_dir / config["files"]["sample_matches"],
        "sample_enriched": processed_dir / config["files"]["sample_enriched"],
    }