import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Optional, Tuple, Union, List
from pathlib import Path
import shutil
from .base import KpPlotBase


class KpStreamgraph(KpPlotBase):
    pass


def streamgraph(
    df,
    metadata: Optional[pd.DataFrame] = None,
    metadata_group: Optional[str] = None,
    sample_order: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (14, 7),
    cmap: Optional[Union[str, List[str]]] = "tab20",
    fill_alpha: float = 1.0,
    edgecolor: Optional[str] = None,
    edge_linewidth: float = 0.3,
    title: Optional[str] = None,
    title_fontsize: float = 16.0,
    title_color: str = "black",
    title_weight: str = "normal",
    title_style: str = "normal",
    xlabel: str = "Samples",
    xlabel_fontsize: float = 12.0,
    xlabel_color: str = "black",
    xlabel_weight: str = "normal",
    xlabel_style: str = "normal",
    ylabel: str = "Relative Abundance (%)",
    ylabel_fontsize: float = 12.0,
    ylabel_color: str = "black",
    ylabel_weight: str = "normal",
    ylabel_style: str = "normal",
    xticks_rotation: float = 0.0,
    xticks_ha: str = "center",
    xticks_fontsize: float = 12.0,
    xticks_color: str = "black",
    xticks_weight: str = "normal",
    xticks_style: str = "normal",
    background_color="white",
    grid: bool = True,
    grid_linestyle: str = "--",
    grid_alpha: float = 0.7,
    legend_title: str = "Taxon",
    legend_fontsize: float = 9.0,
    legend_fontstyle: str = "italic",
    legend_loc: str = "upper left",
    legend_bbox: Tuple[float, float] = (1.05, 1),
    show_legend: bool = True,
):
    """
    Generates a customizable streamgraph plot showing relative abundance values across samples.

    Parameters:
    - df: Pandas DataFrame containing the dataset.
    - metadata: Optional DataFrame with sample metadata (must include 'Sample_id').
    - metadata_group: Column in `metadata` to group samples by for aggregation.
    - sample_order: Optional list to specify the order of columns (samples) in the heatmap.
    - figsize: Tuple (width, height) of the figure.
    - cmap: Colormap name (str) or list of colors.
    - fill_alpha: Transparency of the filled areas.
    - edgecolor: Color of the edges (borders) drawn around each stacked area in the streamgraph.
    - edge_linewidth: Width of the edge lines around each stacked area.
    - title: Title of the plot.
    - title_fontsize, title_color, title_weight, title_style: Title styling.
    - xlabel, ylabel: Axis labels.
    - xlabel_fontsize, xlabel_color, xlabel_weight, xlabel_style: X-axis label styling.
    - ylabel_fontsize, ylabel_color, ylabel_weight, ylabel_style: Y-axis label styling.
    - xticks_rotation, xticks_ha: Rotation angle and alignment of x-axis tick labels.
    - xticks_fontsize, xticks_color, xticks_weight, xticks_style: X-axis tick label styling.
    - background_color: Background color of the figure.
    - grid: Whether to display a grid.
    - grid_color, grid_linestyle, grid_linewidth: Grid styling.
    - legend_fontsize: Font size for legend labels.
    - legend_loc: Position of the legend.
    - legend_bbox: Position of the legend box.
    - show_legend: Whether to display the legend.

    Returns:
    - KpStreamgraph: An object containing the streamgraph figure and axis for customization or saving.
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

    if sample_order is not None:
        df = df[df["Sample_id"].isin(sample_order)]
        df["Sample_id"] = pd.Categorical(
            df["Sample_id"], categories=sample_order, ordered=True
        )
    df["taxon"] = pd.Categorical(
        df["taxon"],
        categories=sorted(
            df["taxon"].unique(), key=lambda x: (x.startswith("Other"), x)
        ),
        ordered=True,
    )
    df_plot = df.pivot(
        index="Sample_id", columns="taxon", values="rel_abund_perc"
    ).fillna(0)

    if isinstance(cmap, str):
        color_dict = dict(
            zip(df_plot.columns, sns.color_palette(cmap, n_colors=len(df_plot.columns)))
        )
    elif isinstance(cmap, list):
        color_dict = dict(zip(df_plot.columns, cmap))
    else:
        raise ValueError("cmap must be a str or a list of colors")

    for col in color_dict:
        if col.lower().startswith("other"):
            color_dict[col] = "#837b8d"

    colors = [color_dict[col] for col in df_plot.columns]

    fig, ax = plt.subplots(figsize=figsize, facecolor=background_color)

    layers = ax.stackplot(
        df_plot.index,
        df_plot.values.T,
        labels=df_plot.columns,
        colors=colors,
        alpha=fill_alpha,
        zorder=3,
    )

    for poly in layers:
        poly.set_edgecolor(edgecolor)
        poly.set_linewidth(edge_linewidth)

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

    if show_legend:
        legend = ax.legend(
            title=legend_title,
            bbox_to_anchor=legend_bbox,
            loc=legend_loc,
            fontsize=legend_fontsize,
        )
        for text in legend.get_texts():
            text.set_fontstyle(legend_fontstyle)

    if grid:
        ax.grid(axis="x", linestyle=grid_linestyle, alpha=grid_alpha, zorder=0)

    positions = np.arange(len(df_plot.index))
    labels = df_plot.index.tolist()
    plt.xticks(
        positions,
        labels,
        rotation=xticks_rotation,
        ha=xticks_ha,
        fontsize=xticks_fontsize,
        color=xticks_color,
        weight=xticks_weight,
        style=xticks_style,
    )

    ax.set_xlim(-0.5, len(df_plot.index) - 0.5)

    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"

    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    plt.close(fig)

    return KpStreamgraph(fig, ax)
