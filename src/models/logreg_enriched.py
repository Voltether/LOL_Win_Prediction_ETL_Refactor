from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


@dataclass
class LogRegArtifacts:
    model: LogisticRegression
    scaler: StandardScaler
    features: list[str]


def load_training_data(
    csv_path: str | Path,
    features: list[str],
    target: str,
) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    required = features + [target]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns in training CSV: {missing}")

    return df[required].copy()


def split_and_scale(
    df: pd.DataFrame,
    features: list[str],
    target: str,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, StandardScaler]:
    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    scaler = StandardScaler()

    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=features,
        index=X_train.index,
    )

    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=features,
        index=X_test.index,
    )

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


def train_logreg(
    X_train_scaled: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = 42,
) -> LogisticRegression:
    """Return core classification metrics."""
    model = LogisticRegression(
        l1_ratio=1,
        C=0.1,
        solver="saga",
        random_state=random_state,
        max_iter=10000,
        fit_intercept=True,
    )

    model.fit(X_train_scaled, y_train)
    return model


def evaluate_model(
    model: LogisticRegression,
    X_test_scaled: pd.DataFrame,
    y_test: pd.Series,
    threshold: float = 0.5,
) -> dict:
    """Return core classification metrics."""
    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=[0, 1]),
        "classification_report": classification_report(y_test, y_pred, digits=3),
    }


def build_match_features(
    df: pd.DataFrame,
    features: list[str],
) -> pd.DataFrame:
    df = df.copy()

    objective_cols = {
        "tower_fb": "my_team_tower_fb",
        "drake_fb": "my_team_drake_fb",
        "herald_fb": "my_team_herald_fb",
    }

    if "my_team" not in df.columns:
        raise ValueError("Missing column my_team to build first-objective features.")

    for raw_col, feature_col in objective_cols.items():
        if raw_col not in df.columns:
            raise ValueError(f"Missing column {raw_col} to build {feature_col}.")

        df[feature_col] = (df[raw_col] == df["my_team"]).astype(int)

    missing = [col for col in features if col not in df.columns]

    if missing:
        raise ValueError(f"Missing model features: {missing}")

    return df[features].copy()


def predict_matches(
    df_matches: pd.DataFrame,
    artifacts: LogRegArtifacts,
    match_id_col: str = "match_id",
) -> pd.DataFrame:
    X_pred = build_match_features(
        df_matches,
        artifacts.features,
    )

    X_pred_scaled = pd.DataFrame(
        artifacts.scaler.transform(X_pred),
        columns=artifacts.features,
        index=X_pred.index,
    )

    probs = artifacts.model.predict_proba(X_pred_scaled)[:, 1]

    result = pd.DataFrame({"prob_victoria": probs})

    if match_id_col in df_matches.columns:
        result.insert(0, match_id_col, df_matches[match_id_col].values)

    return result.sort_values("prob_victoria", ascending=False)


def save_artifacts(artifacts: LogRegArtifacts, output_dir: str | Path) -> None:
    """Save model, scaler and feature list."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(artifacts.model, output_dir / "logreg_enriched_model.joblib")
    joblib.dump(artifacts.scaler, output_dir / "logreg_enriched_scaler.joblib")
    joblib.dump(artifacts.features, output_dir / "logreg_enriched_features.joblib")


def load_artifacts(model_dir: str | Path) -> LogRegArtifacts:
    """Load model, scaler and feature list."""
    model_dir = Path(model_dir)

    return LogRegArtifacts(
        model=joblib.load(model_dir / "logreg_enriched_model.joblib"),
        scaler=joblib.load(model_dir / "logreg_enriched_scaler.joblib"),
        features=joblib.load(model_dir / "logreg_enriched_features.joblib"),
    )