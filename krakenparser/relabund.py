#!/usr/bin/env python

import shutil
from pathlib import Path
import argparse
import pandas as pd


def calculate_rel_abund(input_file, output_file, other_threshold=None):
    # Load counts table
    df = pd.read_csv(input_file)

    # Reshape to long format: Sample_id, taxon, abundance
    long_df = df.melt(id_vars=["Sample_id"], var_name="taxon", value_name="abundance")

    # Summarize total abundance per sample (used for percentage calculation)
    total_abundance = long_df.groupby("Sample_id")["abundance"].transform("sum")

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
    result.to_csv(output_file, index=False)
    print(
        f"Relative abundance has been successfully calculated and saved as '{output_file}'."
    )

    # Remove __pycache__
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"
    if pycache_dir.exists():
        shutil.rmtree(pycache_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculates taxa relative abundance and saves it to a CSV file."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Input CSV file with counts."
    )
    parser.add_argument("-o", "--output", required=True, help="Output CSV file path.")
    parser.add_argument(
        "-O",
        "--other",
        type=float,
        default=None,
        help="Threshold for grouping taxa into 'Other (<X%%)'. Example: -O 3.5",
    )

    args = parser.parse_args()
    calculate_rel_abund(args.input, args.output, args.other)
