from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, roc_auc_score, roc_curve


def _save_or_show(output_path: str | Path | None) -> None:
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.tight_layout()
        plt.show()


def plot_confusion_matrix(
    model,
    X_test_scaled: pd.DataFrame,
    y_test: pd.Series,
    threshold: float = 0.5,
    output_path: str | Path | None = None,
) -> None:
    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    disp = ConfusionMatrixDisplay(cm, display_labels=["Derrota", "Victoria"])
    disp.plot(values_format="d")
    plt.title(f"Matriz de confusión (threshold={threshold:.2f})")
    _save_or_show(output_path)


def plot_logistic_curve_vs_gold_diff(
    model,
    scaler,
    X_test: pd.DataFrame,
    features: list[str],
    output_path: str | Path | None = None,
) -> None:
    feature_x = "gold_diff"

    ref_base = X_test[features].median().to_frame().T
    qmin, qmax = X_test[feature_x].quantile([0.005, 0.995])
    grid = np.linspace(qmin, qmax, 300)

    scenarios = [
        ("Neutral", {}),
        (
            "Unfavorable (low kills, no FBs)",
            {
                "kill_diff": X_test["kill_diff"].quantile(0.25),
                "my_team_tower_fb": 0,
                "my_team_drake_fb": 0,
                "my_team_herald_fb": 0,
            },
        ),
        (
            "Favorable (high kills, with FBs)",
            {
                "kill_diff": X_test["kill_diff"].quantile(0.75),
                "my_team_tower_fb": 1,
                "my_team_drake_fb": 1,
                "my_team_herald_fb": 1,
            },
        ),
    ]

    def predict_curve_for_scenario(overrides: dict) -> tuple[np.ndarray, float | None]:
        ref = ref_base.copy()

        for key, value in overrides.items():
            if key in ref.columns:
                ref.loc[:, key] = value

        grid_df = pd.concat([ref] * len(grid), ignore_index=True)
        grid_df[feature_x] = grid

        grid_scaled = scaler.transform(grid_df[features])
        p = model.predict_proba(grid_scaled)[:, 1]

        w = model.coef_[0]
        b = model.intercept_[0]
        mu = scaler.mean_
        sigma = scaler.scale_
        idx = features.index(feature_x)

        z_ref = (ref.iloc[0].values - mu) / sigma
        k = np.dot(w, z_ref) - w[idx] * z_ref[idx]

        threshold_x = None
        if not np.isclose(w[idx], 0.0):
            threshold_x = mu[idx] - sigma[idx] * (k + b) / w[idx]

        return p, threshold_x

    fig, axes = plt.subplots(1, len(scenarios), figsize=(16, 5), sharey=True)

    for ax, (name, overrides) in zip(axes, scenarios):
        p, threshold_x = predict_curve_for_scenario(overrides)

        ax.plot(grid, p, label="Victory Pred.", lw=2)
        ax.fill_between(grid, 0, 0.5, alpha=0.08, label="Loss Pred.")
        ax.fill_between(grid, 0.5, 1, alpha=0.08, label="Win Pred.")
        ax.axhline(0.5, ls="--", lw=1, label="0.5 Threshold")

        if threshold_x is not None and grid.min() <= threshold_x <= grid.max():
            ax.axvline(threshold_x, ls="--", lw=1)
            ax.text(
                threshold_x,
                0.52,
                f"{threshold_x:.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        ax.set_title(name, fontsize=11)
        ax.set_xlabel("gold_diff")
        ax.grid(alpha=0.25)

    axes[0].set_ylabel("Victory Probability")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles[:4],
        labels[:4],
        loc="lower center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.5, -0.02),
    )

    fig.suptitle("Logistic Curve vs gold_diff", fontsize=13, y=1.03)
    _save_or_show(output_path)


def plot_roc_auc(
    model,
    X_train_scaled: pd.DataFrame,
    y_train: pd.Series,
    X_test_scaled: pd.DataFrame,
    y_test: pd.Series,
    output_path: str | Path | None = None,
) -> tuple[float, float]:
    y_proba_train = model.predict_proba(X_train_scaled)[:, 1]
    y_proba_test = model.predict_proba(X_test_scaled)[:, 1]

    fpr_train, tpr_train, _ = roc_curve(y_train, y_proba_train)
    fpr_test, tpr_test, _ = roc_curve(y_test, y_proba_test)

    auc_train = roc_auc_score(y_train, y_proba_train)
    auc_test = roc_auc_score(y_test, y_proba_test)

    plt.figure(figsize=(6, 5))
    plt.plot(fpr_train, tpr_train, label=f"Train AUC = {auc_train:.3f}")
    plt.plot(fpr_test, tpr_test, label=f"Test AUC = {auc_test:.3f}")
    plt.plot([0, 1], [0, 1], "--", linewidth=1)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve (Logistic Regression)")
    plt.legend()

    _save_or_show(output_path)
    return auc_train, auc_test


def plot_logreg_coefficients(
    model,
    feature_names: list[str],
    output_path: str | Path | None = None,
) -> pd.Series:
    coef = pd.Series(model.coef_[0], index=feature_names).sort_values()

    plt.figure(figsize=(8, 6))
    coef.plot(kind="barh")
    plt.axvline(0, linewidth=0.8)
    plt.title("Coeficientes normalizados de la regresión logística")
    plt.xlabel("Peso (impacto en la predicción)")
    plt.ylabel("Features")

    _save_or_show(output_path)
    return coef
