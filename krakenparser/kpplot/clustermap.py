import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple, Union, List
from pathlib import Path
import shutil
from .base import KpPlotBase


class KpClustermap(KpPlotBase):
    pass


def clustermap(
    df: pd.DataFrame,
    metadata: Optional[pd.DataFrame] = None,
    metadata_group: Optional[str] = None,
    sample_order: Optional[List[str]] = None,
    clust_linewidths: float = 0.5,
    clust_linecolor: str = "grey",
    x_axis: str = "Sample_id",
    y_axis: str = "taxon",
    figsize: Optional[Tuple[int, int]] = None,
    cmap: str = "Greens",
    title: Optional[str] = None,
    title_fontsize: float = 16.0,
    title_color: str = "black",
    title_weight: str = "normal",
    title_style: str = "normal",
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    xlabel_fontsize: float = 12.0,
    ylabel_fontsize: float = 12.0,
    xlabel_color: str = "black",
    ylabel_color: str = "black",
    xlabel_weight: str = "normal",
    ylabel_weight: str = "normal",
    xlabel_style: str = "normal",
    ylabel_style: str = "normal",
    xticks_rotation: float = 0.0,
    xticks_ha: str = "center",
    xticks_fontsize: float = 12.0,
    xticks_color: str = "black",
    xticks_weight: str = "normal",
    xticks_style: str = "normal",
    yticks_rotation: float = 0.0,
    yticks_ha: str = "left",
    yticks_fontsize: float = 12.0,
    yticks_color: str = "black",
    yticks_weight: str = "normal",
    yticks_style: str = "normal",
    standard_scale: Optional[int] = None,
    z_score: Optional[int] = None,
    legend_title: str = "Relative abundance (%)",
    cbar_pos: Tuple[float, float, float, float] = (1.02, 0.3, 0.03, 0.4),
    background_color: str = "white",
):
    """
    Generates a customizable clustermap to visualize the relative abundance across samples.

    Parameters:
    - df: Pandas DataFrame containing the dataset.
    - metadata: Optional DataFrame with sample metadata (must include 'Sample_id').
    - metadata_group: Column in `metadata` to group samples by for aggregation.
    - sample_order: Optional list to specify the order of columns (samples) in the heatmap.
    - clust_linewidths: Width of the lines that divide cells in the clustermap heatmap.
    - clust_linecolor: Color of the grid lines separating the heatmap cells.
    - x_axis, y_axis: Column name in `df` to be used for the X- or Y-axis.
    - figsize: Tuple (width, height) of the figure.
    - cmap: Colormap name (str) or list of colors.
    - title: Main title of the plot.
    - title_fontsize, title_color, title_weight, title_style: Title text styling.
    - xlabel, ylabel: Axis labels.
    - xlabel_fontsize, xlabel_color, xlabel_weight, xlabel_style: X-axis label styling.
    - ylabel_fontsize, ylabel_color, ylabel_weight, ylabel_style: Y-axis label styling.
    - xticks_rotation, xticks_ha: Rotation angle and alignment of X-axis tick labels.
    - xticks_fontsize, xticks_color, xticks_weight, xticks_style: X-axis tick label styling.
    - yticks_fontsize, yticks_color, yticks_weight, yticks_style: Y-axis tick label styling.
    - legend_title: Title for the colorbar legend indicating what the values represent.
    - cbar_pos: Tuple (X, Y, width, height) of the colorbar.
    - background_color: Background color of the figure.

    Returns:
    - KpStackedBarplot: An object containing the clustermap figure and axis for customization or saving.
    """

    df = df.copy()

    if metadata is not None and metadata_group is not None:
        if "Sample_id" not in metadata.columns:
            raise ValueError("metadata must contain 'Sample_id' column")
        if metadata_group not in metadata.columns:
            raise ValueError(f"'{metadata_group}' column not found in metadata")

        df = df.merge(
            metadata[["Sample_id", metadata_group]], on="Sample_id", how="left"
        )
        df = (
            df.groupby([metadata_group, "taxon"], as_index=False)["rel_abund_perc"]
            .mean()
            .rename(columns={metadata_group: "Sample_id"})
        )
        df["rel_abund_perc"] = df.groupby("Sample_id")["rel_abund_perc"].transform(
            lambda x: (x / x.sum()) * 100
        )

    if df[y_axis].dtype == object:
        other_mask = df[y_axis].str.startswith("Other")
        taxon_order = list(df[other_mask][y_axis].unique()) + sorted(
            df[~other_mask][y_axis].unique()
        )
        df[y_axis] = pd.Categorical(df[y_axis], categories=taxon_order, ordered=True)

    pivot = df.pivot(index=y_axis, columns=x_axis, values="rel_abund_perc").fillna(0)

    if sample_order is not None:
        missing = set(sample_order) - set(pivot.columns)
        if missing:
            raise ValueError(f"Samples missing from data: {missing}")
        pivot = pivot[sample_order]

        col_cluster = False
    else:
        col_cluster = True

    g = sns.clustermap(
        pivot,
        cmap=cmap,
        figsize=figsize,
        annot=True,
        fmt=".1f",
        linewidths=clust_linewidths,
        linecolor=clust_linecolor,
        cbar_kws={"label": legend_title, "shrink": 0.7, "pad": 0.02},
        cbar_pos=cbar_pos,
        standard_scale=standard_scale,
        z_score=z_score,
        col_cluster=col_cluster,
    )

    g.fig.patch.set_facecolor(background_color)

    ax = g.ax_heatmap
    fig = g.fig

    ax.set_title(
        title,
        fontsize=title_fontsize,
        color=title_color,
        weight=title_weight,
        style=title_style,
    )

    ax.set_xlabel(
        xlabel,
        fontsize=xlabel_fontsize,
        color=xlabel_color,
        weight=xlabel_weight,
        style=xlabel_style,
    )

    ax.set_ylabel(
        ylabel,
        fontsize=ylabel_fontsize,
        color=ylabel_color,
        weight=ylabel_weight,
        style=ylabel_style,
    )

    plt.setp(
        ax.get_xticklabels(),
        rotation=xticks_rotation,
        ha=xticks_ha,
        fontsize=xticks_fontsize,
        color=xticks_color,
        weight=xticks_weight,
        style=xticks_style,
    )

    plt.setp(
        ax.get_yticklabels(),
        rotation=yticks_rotation,
        ha=yticks_ha,
        fontsize=yticks_fontsize,
        color=yticks_color,
        weight=yticks_weight,
        style=yticks_style,
    )

    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    plt.close(fig)
    return KpClustermap(fig, ax)
