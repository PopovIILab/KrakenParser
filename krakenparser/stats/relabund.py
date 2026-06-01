#!/usr/bin/env python

import logging
import sys
import warnings
from pathlib import Path
from typing import Optional

import pandas as pd
import typer

from krakenparser.utils import ensure_output_dir

_log = logging.getLogger(__name__)

app = typer.Typer(
    name="relabund",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def calculate_rel_abund(
    input_file: Path, output_file: Path, other_threshold: Optional[float] = None
) -> None:
    in_path = Path(input_file)
    if not in_path.is_file():
        raise FileNotFoundError(f"Input file not found: {in_path}")
    out_path = ensure_output_dir(str(output_file), is_file=True)

    # Load counts table
    df = pd.read_csv(in_path)

    # Reshape to long format: Sample_id, taxon, abundance
    long_df = df.melt(id_vars=["Sample_id"], var_name="taxon", value_name="abundance")

    # Summarize total abundance per sample (used for percentage calculation)
    total_abundance = long_df.groupby("Sample_id")["abundance"].transform("sum")

    zero_samples = long_df.groupby("Sample_id")["abundance"].sum()
    zero_samples = zero_samples[zero_samples == 0].index.tolist()
    if zero_samples:
        warnings.warn(
            f"Samples with zero total abundance were excluded from output: {zero_samples}",
            UserWarning,
            stacklevel=2,
        )

    # Calculate relative abundance (%)
    long_df["rel_abund_perc"] = (long_df["abundance"] / total_abundance) * 100

    # Drop 0.0 rows
    long_df = long_df[long_df["rel_abund_perc"] > 0.0]

    # Apply "Other" grouping if threshold is specified
    if other_threshold is not None:
        threshold = float(other_threshold)
        label = f"Other (<{threshold}%)"
        long_df["taxon"] = long_df.apply(
            lambda row: label if row["rel_abund_perc"] < threshold else row["taxon"],
            axis=1,
        )

    # Summarize final percentages
    result = (
        long_df.groupby(["Sample_id", "taxon"], as_index=False)["rel_abund_perc"]
        .sum()
        .sort_values(["Sample_id", "rel_abund_perc"], ascending=[True, False])
    )

    # Save to CSV
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
