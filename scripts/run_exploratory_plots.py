from src.visualization.exploratory_plots import (
    plot_boxplots,
    plot_correlation_heatmap,
    plot_pairplot,
)

from src.features.build_dfinfo import build_dfinfo_from_csv


dfinfo = build_dfinfo_from_csv(
    input_path="data/processed/sample_apex_enriched.csv"
)

plot_correlation_heatmap(dfinfo)

plot_pairplot(dfinfo)

plot_boxplots(dfinfo)