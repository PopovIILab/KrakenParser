#!/usr/bin/env python3
"""Streamgraph visualization module for continuous-like metagenomic cohort profiles.

This module renders smooth, contiguous stacked area charts representing
the progression and shifts of relative taxonomic abundances across samples
or grouped metadata categories.
"""

from typing import Any, Literal, Optional, Sequence, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .base import KpPlotBase, aggregate_by_metadata


class KpStreamgraph(KpPlotBase):
    """Orchestration context wrapper encapsulating Matplotlib streamgraph layouts."""

    def __init__(self, fig: plt.Figure, ax: plt.Axes) -> None:
        """Initialize the streamgraph canvas with layout metrics.

        Args:
            fig: The Matplotlib Figure container hosting the drawing canvas.
            ax: The core underlying Axes coordinate grid mapper.
        """
        super().__init__(fig, ax)


def streamgraph(
    df: pd.DataFrame,
    metadata: Optional[pd.DataFrame] = None,
    metadata_group: Optional[str] = None,
    sample_order: Optional[Sequence[str]] = None,
    figsize: Tuple[float, float] = (14.0, 7.0),
    cmap: Union[str, Sequence[str]] = "tab20",
    bar_width: float = 0.6,
    fill_alpha: float = 1.0,
    edgecolor: Optional[str] = None,
    edge_linewidth: float = 0.3,
    title: Optional[str] = None,
    title_fontsize: float = 16.0,
    title_color: str = "black",
    title_weight: Literal["normal", "bold", "heavy", "light"] = "normal",
    title_style: Literal["normal", "italic", "oblique"] = "normal",
    xlabel: str = "Samples",
    xlabel_fontsize: float = 12.0,
    xlabel_color: str = "black",
    xlabel_weight: Literal["normal", "bold", "heavy", "light"] = "normal",
    xlabel_style: Literal["normal", "italic", "oblique"] = "normal",
    ylabel: str = "Relative Abundance (%)",
    ylabel_fontsize: float = 12.0,
    ylabel_color: str = "black",
    ylabel_weight: Literal["normal", "bold", "heavy", "light"] = "normal",
    ylabel_style: Literal["normal", "italic", "oblique"] = "normal",
    xticks_rotation: float = 0.0,
    xticks_ha: Literal["left", "right", "center"] = "center",
    xticks_fontsize: float = 12.0,
    xticks_color: str = "black",
    xticks_weight: Literal["normal", "bold", "heavy", "light"] = "normal",
    xticks_style: Literal["normal", "italic", "oblique"] = "normal",
    background_color: Optional[str] = "white",
    grid: bool = True,
    grid_linestyle: str = "--",
    grid_alpha: float = 0.7,
    legend_title: str = "Taxon",
    legend_fontsize: float = 9.0,
    legend_fontstyle: Literal["normal", "italic", "oblique"] = "italic",
    legend_loc: str = "upper left",
    legend_bbox: Tuple[float, float] = (1.05, 1.0),
    show_legend: bool = True,
) -> KpStreamgraph:
    """Generate a highly customizable streamgraph/stacked-area plot for relative abundances.

    Transforms microbial datasets into aligned matrices, formats taxonomic categories
    ensuring 'Other' components sink to the baseline, flattens continuous area coordinates,
    and handles custom color palettes without static analysis overloads.

    Args:
        df: Input DataFrame containing tracking metrics ('Sample_id', 'taxon', 'rel_abund_perc').
        metadata: Optional worksheet schema mapping samples to experimental variables.
        metadata_group: Column header within metadata used for cross-sample aggregation.
        sample_order: Explicit layout sequence locking the display order on the X-axis.
        figsize: Geometric allocation limits (width, height) defining canvas borders.
        cmap: Target string name lookup or a sequential list of direct hexadecimal colors.
        bar_width: Horizontal span coefficient used to step and duplicate area limits.
        fill_alpha: Opacity index managing transparency limits of the filled polygons.
        edgecolor: Border styling color outline separating adjacent stacked streams.
        edge_linewidth: Thickness parameter of border outlines enclosing stream paths.
        title: Global text message identifier rendering above the drawing matrix.
        title_fontsize, title_color, title_weight, title_style: Font properties for title.
        xlabel, ylabel: Text content values mapping coordinates descriptors.
        xlabel_fontsize, ylabel_fontsize: Typography scale indices.
        xlabel_color, ylabel_color: Text color variables mapping target labels.
        xlabel_weight, ylabel_weight: Structural typographic density metrics.
        xlabel_style, ylabel_style: Geometric font slope configurations.
        xticks_rotation, xticks_ha: Position variables mapping target X tick attributes.
        xticks_fontsize, xticks_color, xticks_weight, xticks_style: X-tick typography rules.
        background_color: Primary layout canvas backdrop color mapping.
        grid: Toggles background coordinate reference line structures.
        grid_linestyle: Grid line texture rendering parameter.
        grid_alpha: Opacity index managing visibility bounds of grid elements.
        legend_title: Display title contextual wrapper tracking color keys.
        legend_fontsize, legend_fontstyle: Typography rules mapping legends.
        legend_loc: Positional anchoring code identifier tracking layout widgets.
        legend_bbox: Coordinate anchor box offsets defining bounding regions for legends.
        show_legend: If False, completely suppresses widget layer execution.

    Returns:
        KpStreamgraph: Container instance holding references to optimized figures.

    Raises:
        ValueError: Triggered if sample targets or color map arrays violate alignment steps.
    """
    working_df: pd.DataFrame = df.copy()

    # Step 1: Conditionally execute group aggregation operations
    if metadata is not None and metadata_group is not None:
        working_df = aggregate_by_metadata(working_df, metadata, metadata_group)

    # Step 2: Validate sample elements and apply strict ordered categorical indices
    if sample_order is not None:
        missing_samples: set[str] = set(sample_order) - set(
            working_df["Sample_id"].unique()
        )
        if missing_samples:
            raise ValueError(
                f"Samples missing from the data matrix sequence alignment: missing {missing_samples}"
            )
        working_df = working_df[working_df["Sample_id"].isin(sample_order)].copy()
        working_df["Sample_id"] = pd.Categorical(
            working_df["Sample_id"], categories=list(sample_order), ordered=True
        )

    # Step 3: Extract and structure taxonomic sort categories ensuring 'Other' falls last
    unique_taxa: Sequence[str] = working_df["taxon"].unique()
    other_taxa: list[str] = sorted(
        [t for t in unique_taxa if str(t).startswith("Other")]
    )
    regular_taxa: list[str] = sorted(
        [t for t in unique_taxa if not str(t).startswith("Other")]
    )
    taxon_categories: list[str] = regular_taxa + other_taxa

    working_df["taxon"] = pd.Categorical(
        working_df["taxon"], categories=taxon_categories, ordered=True
    )

    # Step 4: Reshape layout spreadsheet structure via pivot operations
    df_plot: pd.DataFrame = working_df.pivot(
        index="Sample_id", columns="taxon", values="rel_abund_perc"
    ).fillna(0.0)

    # Step 5: Establish palette map dictionaries compliant with static analysis
    if isinstance(cmap, str):
        palette_colors = sns.color_palette(cmap, n_colors=len(df_plot.columns))
        color_dict: dict[str, Any] = {
            str(col): color for col, color in zip(df_plot.columns, palette_colors)
        }
    elif isinstance(cmap, (list, tuple, np.ndarray, pd.Series)) or hasattr(
        cmap, "__iter__"
    ):
        if len(cmap) < len(df_plot.columns):
            raise ValueError(
                f"Color allocation array size mismatch: custom cmap palette has {len(cmap)} blocks "
                f"but target dataset maps {len(df_plot.columns)} taxonomic items."
            )
        color_dict = {str(col): color for col, color in zip(df_plot.columns, cmap)}
    else:
        raise ValueError(
            "Parameter 'cmap' violates validation constraints: must map to str or sequence."
        )

    # Apply specialized bioinformatic neutral-grey mapping overrides targeting unresolved fragments
    for col in color_dict:
        if str(col).lower().startswith("other"):
            color_dict[col] = "#837b8d"

    colors_list: list[Any] = [color_dict[col] for col in df_plot.columns]

    # Step 6: Flat coordinates preparation for stream area alignment
    centers = np.arange(len(df_plot.index))
    xs = np.column_stack(
        (centers - bar_width / 2.0, centers + bar_width / 2.0)
    ).flatten()

    # Step 7: Initialize structural container canvas layers
    fig, ax = plt.subplots(figsize=figsize, facecolor=background_color)

    ys = np.repeat(df_plot.values.T, 2, axis=1)
    layers = ax.stackplot(
        xs,
        ys,
        labels=df_plot.columns,
        colors=colors_list,
        alpha=fill_alpha,
        zorder=3,
    )

    resolved_edgecolor: str = edgecolor if edgecolor is not None else "none"

    # Atomic configurations updates on polygon streams objects
    for poly in layers:
        poly.set_edgecolor(resolved_edgecolor)
        poly.set_linewidth(edge_linewidth)

    # Step 8: Apply customized typography parameters to coordinate boundaries
    if title:
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

    # Step 9: Build legend overlays if requested by execution flags
    if show_legend:
        legend = ax.legend(
            title=legend_title,
            bbox_to_anchor=legend_bbox,
            loc=legend_loc,
            fontsize=legend_fontsize,
        )
        if legend:
            for text_node in legend.get_texts():
                text_node.set_fontstyle(legend_fontstyle)

    if grid:
        ax.grid(axis="y", linestyle=grid_linestyle, alpha=grid_alpha, zorder=0)

    # Step 10: Configure ticks geometric parameters and close active canvas streams
    labels_list = df_plot.index.tolist()
    plt.xticks(
        centers,
        labels_list,
        rotation=xticks_rotation,
        ha=xticks_ha,
        fontsize=xticks_fontsize,
        color=xticks_color,
        weight=xticks_weight,
        style=xticks_style,
    )

    ax.set_xlim(-0.5, len(df_plot.index) - 0.5)

    plt.close(fig)
    return KpStreamgraph(fig, ax)
