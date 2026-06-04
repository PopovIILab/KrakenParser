#!/usr/bin/env python3
"""Normalization module for calculating relative abundances of microbial taxa.

This module reshapes wide count matrices into tidy long-format tables, converts
raw read counts into percentage distributions per sample, filters out zero-abundance
observations, and optionally aggregates rare background taxa under a unified
customizable threshold to prevent downstream overplotting.
"""

import logging
import sys
import warnings
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
import typer

from krakenparser.utils import ensure_output_dir

# Initialize module-level isolated logger
_log: logging.Logger = logging.getLogger(__name__)

# Dedicated Typer routing application instantiation
app: typer.Typer = typer.Typer(
    name="relabund",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def calculate_rel_abund(
    input_file: Path, output_file: Path, other_threshold: Optional[float] = None
) -> None:
    """Transform absolute taxonomic counts to relative percentage profiles.

    Reshapes data into long format, detects and warns about zero-abundance samples,
    normalizes counts to a 100% scale, and applies an efficient vector-based
    threshold filter to bundle low-abundance variants into an 'Other' abstraction.

    Args:
        input_file: Path to the incoming wide matrix CSV (index or Sample_id required).
        output_file: Target path where the final long-format normalized CSV is saved.
        other_threshold: Optional percentage bound (e.g., 3.5). Taxa falling below
            this value within a sample are aggregated into a generic composite pool.

    Raises:
        FileNotFoundError: Triggered if the specified input count resource is missing.
    """
    if not input_file.is_file():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    out_path: Path = ensure_output_dir(output_file, is_file=True)

    # Load counts table matrix (Wide format: rows=samples, cols=taxa)
    df: pd.DataFrame = pd.read_csv(input_file)

    # Reshape to long format: Sample_id, taxon, abundance (Tidy data specification)
    long_df: pd.DataFrame = df.melt(
        id_vars=["Sample_id"], var_name="taxon", value_name="abundance"
    )

    # Vectorized total abundance extraction per mapping target profile
    total_abundance: pd.Series = long_df.groupby("Sample_id")["abundance"].transform(
        "sum"
    )

    # Isolate and audit unsequenced or empty background sample profiles
    sample_sums: pd.Series = long_df.groupby("Sample_id")["abundance"].sum()
    zero_samples: list[Any] = sample_sums[sample_sums == 0].index.tolist()
    if zero_samples:
        warnings.warn(
            f"Samples with zero total abundance were excluded from output: {zero_samples}",
            UserWarning,
            stacklevel=2,
        )

    # Compute relative composition metric percentage arrays
    long_df["rel_abund_perc"] = (long_df["abundance"] / total_abundance) * 100

    # Clean runtime noise by purging absolute zero occurrences
    long_df = long_df[long_df["rel_abund_perc"] > 0.0]

    # Conditionally execute low-abundance grouping utilizing high-performance numpy mapping
    if other_threshold is not None:
        threshold: float = float(other_threshold)
        label: str = f"Other (<{threshold}%)"

        # High-performance Vectorized assignment replacing legacy row-wise df.apply loop
        threshold_mask: pd.Series = long_df["rel_abund_perc"] < threshold
        long_df["taxon"] = np.where(threshold_mask, label, long_df["taxon"])

    # Aggregate final percentage statistics collapsed under composite groups if applied
    result: pd.DataFrame = (
        long_df.groupby(["Sample_id", "taxon"], as_index=False)["rel_abund_perc"]
        .sum()
        .sort_values(["Sample_id", "rel_abund_perc"], ascending=[True, False])
    )

    # Flush metrics out to structured storage layout
    result.to_csv(out_path, index=False)
    _log.info("Relative abundance saved as '%s'.", output_file)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    input_file: Optional[Path] = typer.Option(
        None,
        "-i",
        "--input",
        help="Input CSV file with counts.",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output CSV file path.",
    ),
    other: Optional[float] = typer.Option(
        None,
        "-O",
        "--other",
        help="Threshold for grouping taxa into 'Other (<X%)'. Example: -O 3.5",
    ),
) -> None:
    """Calculates taxa relative abundance and saves it to a CSV file."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if input_file is None and output_file is None:
        print(ctx.get_help())
        raise typer.Exit()

    if not input_file or not output_file:
        print(
            "Error: Missing required options '-i / --input' and '-o / --output'.",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)

    try:
        calculate_rel_abund(input_file, output_file, other)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
