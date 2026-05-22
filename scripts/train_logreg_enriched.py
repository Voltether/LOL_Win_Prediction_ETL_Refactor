from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.models.logreg_enriched import (
    FEATURES,
    LogRegArtifacts,
    evaluate_model,
    load_training_data,
    save_artifacts,
    split_and_scale,
    train_logreg,
)
from src.visualization.ml_plots import (
    plot_confusion_matrix,
    plot_logistic_curve_vs_gold_diff,
    plot_logreg_coefficients,
    plot_roc_auc,
)

from src.config import load_config

config = load_config()

features = config["model"]["features"]
target = config["model"]["target_column"]
test_size = config["model"]["test_size"]
random_state = config["model"]["random_state"]
threshold = config["model"]["threshold"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train enriched logistic regression model for Modular 3."
    )
    parser.add_argument(
        "--input-csv",
        default="data/processed/dfinfo_apex_enriched.csv",
        help="Path to enriched ML training CSV.",
    )
    parser.add_argument(
        "--model-dir",
        default="models",
        help="Directory where model artifacts will be saved.",
    )
    parser.add_argument(
        "--plots-dir",
        default="reports/figures",
        help="Directory where plots will be saved.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Decision threshold for binary prediction.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    df = load_training_data(args.input_csv)

    # Keep an unscaled split for the logistic-curve plot.
    X = df[FEATURES]
    y = df["my_team_win"]

    X_train_scaled, X_test_scaled, y_train, y_test, scaler = split_and_scale(df)
    X_train = X.loc[X_train_scaled.index]
    X_test = X.loc[X_test_scaled.index]

    model = train_logreg(X_train_scaled, y_train)
    artifacts = LogRegArtifacts(model=model, scaler=scaler, features=FEATURES)

    metrics = evaluate_model(model, X_test_scaled, y_test, threshold=args.threshold)

    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"ROC AUC: {metrics['roc_auc']:.4f}")
    print("\nConfusion matrix:")
    print(metrics["confusion_matrix"])
    print("\nClassification report:")
    print(metrics["classification_report"])

    save_artifacts(artifacts, args.model_dir)

    plots_dir = Path(args.plots_dir)
    plot_confusion_matrix(
        model,
        X_test_scaled,
        y_test,
        threshold=args.threshold,
        output_path=plots_dir / "confusion_matrix.png",
    )
    plot_logistic_curve_vs_gold_diff(
        model,
        scaler,
        X_test,
        FEATURES,
        output_path=plots_dir / "logistic_curve_vs_gold_diff.png",
    )
    plot_roc_auc(
        model,
        X_train_scaled,
        y_train,
        X_test_scaled,
        y_test,
        output_path=plots_dir / "roc_auc.png",
    )
    plot_logreg_coefficients(
        model,
        FEATURES,
        output_path=plots_dir / "logreg_coefficients.png",
    )

    print(f"\nSaved model artifacts to: {Path(args.model_dir).resolve()}")
    print(f"Saved plots to: {plots_dir.resolve()}")


if __name__ == "__main__":
    main()
