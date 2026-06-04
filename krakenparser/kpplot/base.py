#!/usr/bin/env python3
"""Base classes and data aggregation utilities for metagenomic visualization.

This module provides structural baselines for managing Matplotlib canvas states
and executing dataframe transformations, such as merging abundance matrices
with cohort metadata schemas and performing group-level re-normalization.
"""

from pathlib import Path
from typing import Optional, Union

import matplotlib.pyplot as plt
import pandas as pd


class KpPlotBase:
    """Base orchestration class managing Matplotlib figure and axis contexts."""

    def __init__(self, fig: plt.Figure, ax: plt.Axes) -> None:
        """Initialize the plot base wrapper with canvas references.

        Args:
            fig: The Matplotlib Figure instance acting as the global canvas.
            ax: The Matplotlib Axes instance mapping sub-plot coordinate space.
        """
        self.fig: plt.Figure = fig
        self.ax: plt.Axes = ax

    def plotfig(self) -> plt.Figure:
        """Render the underlying canvas interactively.

        Returns:
            plt.Figure: The updated Matplotlib Figure object.
        """
        plt.show()
        return self.fig

    def savefig(
        self,
        path: Union[Path, str],
        dpi: int = 300,
        transparent: bool = False,
        bbox_inches: Optional[str] = "tight",
    ) -> None:
        """Commit the current canvas state atomically to a physical image file.

        Args:
            path: Target location or string path where the layout image is exported.
            dpi: Dots per inch managing resolution limits. Defaults to 300.
            transparent: Toggles transparency anchors for background regions.
            bbox_inches: Boundary box padding constraints. Defaults to "tight".
        """
        target_path: Path = Path(path)
        self.fig.savefig(
            target_path,
            dpi=dpi,
            transparent=transparent,
            bbox_inches=bbox_inches,
        )


def aggregate_by_metadata(
    df: pd.DataFrame,
    metadata: pd.DataFrame,
    metadata_group: str,
) -> pd.DataFrame:
    """Consolidate abundance samples by cohorts and re-normalize relative profiles.

    Maps discrete sample rows to experimental variables, calculates group-specific
    abundance means per taxon, and scales profiles to ensure the sum equals 100%.

    Args:
        df: Input DataFrame containing 'Sample_id', 'taxon', and 'rel_abund_perc'.
        metadata: Metadata worksheet mapping 'Sample_id' to cohort traits.
        metadata_group: Specific targeted feature column label inside metadata.

    Returns:
        pd.DataFrame: A transposed tidy dataframe ready for cohort-wide plotting.

    Raises:
        ValueError: Triggered if 'Sample_id' or 'metadata_group' columns are missing.
    """
    if "Sample_id" not in metadata.columns:
        raise ValueError(
            "Metadata schema violates structural constraints: missing 'Sample_id'."
        )
    if metadata_group not in metadata.columns:
        raise ValueError(
            f"Target cohort variable column absent from metadata: '{metadata_group}'."
        )

    # Step 1: Execute left-join operation to append experimental cohort tags
    merged_df: pd.DataFrame = df.merge(
        metadata[["Sample_id", metadata_group]], on="Sample_id", how="left"
    )

    # Step 2: Compute arithmetic means for distinct taxonomic categories within groups
    grouped_df: pd.DataFrame = (
        merged_df.groupby([metadata_group, "taxon"], as_index=False)["rel_abund_perc"]
        .mean()
        .rename(columns={metadata_group: "Sample_id"})
    )

    # Step 3: High-performance vectorized transformation to re-normalize profiles to 100%
    # Replaces slow lambda functions with native Series grouping division
    group_sums = grouped_df.groupby("Sample_id")["rel_abund_perc"].transform("sum")
    grouped_df["rel_abund_perc"] = (grouped_df["rel_abund_perc"] / group_sums) * 100

    return grouped_df
