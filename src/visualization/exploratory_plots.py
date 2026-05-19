import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


DEFAULT_COLUMNS = [
    "gold_diff",
    "kill_diff",
    "my_team_tower_fb",
    "my_team_drake_fb",
    "my_team_herald_fb",
    "my_team_win",
]


def plot_correlation_heatmap(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    figsize: tuple[int, int] = (10, 8),
) -> None:
    """
    Genera heatmap de correlación.
    """
    if columns is None:
        columns = DEFAULT_COLUMNS

    corr = df[columns].corr()

    plt.figure(figsize=figsize)

    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
    )

    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.show()


def plot_pairplot(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    hue: str = "my_team_win",
) -> None:
    """
    Genera pairplot para análisis exploratorio.
    """
    if columns is None:
        columns = DEFAULT_COLUMNS

    sns.pairplot(
        df[columns],
        hue=hue,
    )

    plt.show()


def plot_boxplots(
    df: pd.DataFrame,
    target_column: str = "my_team_win",
) -> None:
    """
    Genera boxplots para comparar variables contra el target.
    """
    feature_columns = [
        col
        for col in df.columns
        if col != target_column
    ]

    for column in feature_columns:

        plt.figure(figsize=(8, 5))

        sns.boxplot(
            data=df,
            x=target_column,
            y=column,
        )

        plt.title(f"{column} vs {target_column}")

        plt.tight_layout()
        plt.show()