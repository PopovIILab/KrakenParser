#!/usr/bin/env python3
"""Hierarchical clustering and heatmap visualization module for metagenomic profiles.

This module leverages Seaborn's ClusterGrid matrix engine to compute and render
dendrogram-driven abundance clusterings, enabling rapid detection of co-occurrence
taxonomic patterns and sample cohort similarities.
"""

from typing import Literal, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from seaborn.matrix import ClusterGrid

from .base import KpPlotBase, aggregate_by_metadata


class KpClustermap(KpPlotBase):
    """Orchestration context wrapper encapsulating Seaborn ClusterGrid matrix states."""

    def __init__(self, fig: plt.Figure, ax: plt.Axes, grid: ClusterGrid) -> None:
        """Initialize the clustermap canvas with extended layout grid context.

        Args:
            fig: The Matplotlib Figure container hosting the ClusterGrid layout.
            ax: The core underlying Axes mapping the central abundance heatmap.
            grid: The raw Seaborn ClusterGrid object for deep layout mutations.
        """
        super().__init__(fig, ax)
        self.grid: ClusterGrid = grid


def clustermap(
    df: pd.DataFrame,
    metadata: Optional[pd.DataFrame] = None,
    metadata_group: Optional[str] = None,
    sample_order: Optional[Sequence[str]] = None,
    clust_linewidths: float = 0.5,
    clust_linecolor: str = "grey",
    x_axis: str = "Sample_id",
    y_axis: str = "taxon",
    figsize: Optional[Tuple[float, float]] = None,
    cmap: str = "Greens",
    title: Optional[str] = None,
    title_fontsize: float = 16.0,
    title_color: str = "black",
    title_weight: Literal["normal", "bold", "heavy", "light"] = "normal",
    title_style: Literal["normal", "italic", "oblique"] = "normal",
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    xlabel_fontsize: float = 12.0,
    ylabel_fontsize: float = 12.0,
    xlabel_color: str = "black",
    ylabel_color: str = "black",
    xlabel_weight: Literal["normal", "bold", "heavy", "light"] = "normal",
    ylabel_weight: Literal["normal", "bold", "heavy", "light"] = "normal",
    xlabel_style: Literal["normal", "italic", "oblique"] = "normal",
    ylabel_style: Literal["normal", "italic", "oblique"] = "normal",
    xticks_rotation: float = 0.0,
    xticks_ha: Literal["left", "right", "center"] = "center",
    xticks_fontsize: float = 12.0,
    xticks_color: str = "black",
    xticks_weight: Literal["normal", "bold", "heavy", "light"] = "normal",
    xticks_style: Literal["normal", "italic", "oblique"] = "normal",
    yticks_rotation: float = 0.0,
    yticks_ha: Literal["left", "right", "center"] = "left",
    yticks_fontsize: float = 12.0,
    yticks_color: str = "black",
    yticks_weight: Literal["normal", "bold", "heavy", "light"] = "normal",
    yticks_style: Literal["normal", "italic", "oblique"] = "normal",
    standard_scale: Optional[int] = None,
    z_score: Optional[int] = None,
    legend_title: str = "Relative abundance (%)",
    cbar_pos: Tuple[float, float, float, float] = (1.02, 0.3, 0.03, 0.4),
    background_color: Optional[str] = "white",
) -> KpClustermap:
    """Generate a highly customizable, publication-grade hierarchical clustermap.

    Transforms microbial abundance worksheets into cross-pivoted correlation matrices,
    groups related feature layers using standard Euclidean/Ward metrics, and builds
    composite figures containing core heatmaps linked to sample and taxon dendrograms.

    Args:
        df: Input DataFrame containing categorical axes and continuous metrics.
        metadata: Optional metadata sheet used for categorical sample mapping.
        metadata_group: Column header inside metadata used to pool and average targets.
        sample_order: Explicit structural layout sequence restricting column rendering.
        clust_linewidths: Grid borderline widths dividing independent matrix cells.
        clust_linecolor: Palette color map utilized to draw border partitions.
        x_axis: Column key mapping individual sample profiles. Defaults to 'Sample_id'.
        y_axis: Column key mapping individual microbial features. Defaults to 'taxon'.
        figsize: Dimensional width and height tuple managing canvas allocations.
        cmap: Color lookup palette or standard Matplotlib string color map identifier.
        title: Global chart layout label string text.
        title_fontsize, title_color, title_weight, title_style: Title style metrics.
        xlabel, ylabel: Text descriptors mapping horizontal and vertical axes.
        xlabel_fontsize, ylabel_fontsize: Axis layout font dimensions.
        xlabel_color, ylabel_color: Text color variables mapping labels.
        xlabel_weight, ylabel_weight: Structural typographic density metrics.
        xlabel_style, ylabel_style: Geometric font slope configurations.
        xticks_rotation, xticks_ha: Geometric transformation variables mapping x-ticks.
        xticks_fontsize, xticks_color, xticks_weight, xticks_style: X-tick text parameters.
        yticks_rotation, yticks_ha: Geometric transformation variables mapping y-ticks.
        yticks_fontsize, yticks_color, yticks_weight, yticks_style: Y-tick text parameters.
        standard_scale: Integer axis reference (0 or 1) applied to normalize matrices.
        z_score: Integer axis reference (0 or 1) calculating standard Z score shifts.
        legend_title: Context label string rendering adjacent to colorbars.
        cbar_pos: Coordinates tracking anchor bounding limits for the legend block.
        background_color: Primary layout canvas backdrop color mapping.

    Returns:
        KpClustermap: Context tracking wrapper ready for saving operations.

    Raises:
        ValueError: Triggered if specified sample elements fail data alignment steps.
    """
    working_df: pd.DataFrame = df.copy()

    # Step 1: Conditionally execute metadata-driven group pooling operations
    if metadata is not None and metadata_group is not None:
        working_df = aggregate_by_metadata(working_df, metadata, metadata_group)

    # Step 2: Enforce structural categorization rules to isolate 'Other' catch-all components
    if working_df[y_axis].dtype == object or isinstance(
        working_df[y_axis].dtype, pd.CategoricalDtype
    ):
        unique_taxa: Sequence[str] = working_df[y_axis].unique()
        other_mask: Sequence[bool] = [str(t).startswith("Other") for t in unique_taxa]

        taxon_order: list[str] = [
            t for t, m in zip(unique_taxa, other_mask) if m
        ] + sorted([t for t, m in zip(unique_taxa, other_mask) if not m])
        working_df[y_axis] = pd.Categorical(
            working_df[y_axis], categories=taxon_order, ordered=True
        )

    # Step 3: Reshape tabular datasets into algebraic continuous pivot frames
    pivot: pd.DataFrame = working_df.pivot(
        index=y_axis, columns=x_axis, values="rel_abund_perc"
    ).fillna(0.0)

    # Step 4: Validate and lock custom user column sequences if provided
    col_cluster: bool = True
    if sample_order is not None:
        missing_samples: set[str] = set(sample_order) - set(pivot.columns)
        if missing_samples:
            raise ValueError(
                f"Samples missing from the clustermap matrix sequence alignment: {missing_samples}"
            )
        pivot = pivot[list(sample_order)]
        col_cluster = False

    # Step 5: Initialize and compute Seaborn clustering grid structures (with original defaults)
    g: ClusterGrid = sns.clustermap(
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

    if background_color is not None:
        g.fig.patch.set_facecolor(background_color)

    ax: plt.Axes = g.ax_heatmap
    fig: plt.Figure = g.fig

    # Step 6: Apply publication-grade typography modifications to layout canvas
    if title:
        ax.set_title(
            title,
            fontsize=title_fontsize,
            color=title_color,
            weight=title_weight,
            style=title_style,
        )

    if xlabel:
        ax.set_xlabel(
            xlabel,
            fontsize=xlabel_fontsize,
            color=xlabel_color,
            weight=xlabel_weight,
            style=xlabel_style,
        )
    else:
        ax.set_xlabel("")

    if ylabel:
        ax.set_ylabel(
            ylabel,
            fontsize=ylabel_fontsize,
            color=ylabel_color,
            weight=ylabel_weight,
            style=ylabel_style,
        )
    else:
        ax.set_ylabel("")

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

    # Intercept immediate rendering frames to keep memory blocks sterile
    plt.close(fig)
    return KpClustermap(fig, ax, g)
