#!/usr/bin/env python

import argparse
import logging
from pathlib import Path
import pandas as pd

_log = logging.getLogger(__name__)


def convert_to_csv(input_file, output_file):
    in_path = Path(input_file)
    if not in_path.is_file():
        raise FileNotFoundError(f"Input file not found: {in_path}")
    out_path = Path(output_file)
    if not out_path.parent.exists():
        raise FileNotFoundError(f"Output directory does not exist: {out_path.parent}")

    data = pd.read_csv(in_path, sep="\t", index_col=0)
    data.T.to_csv(out_path, index_label="Sample_id")
    _log.info("Data converted and saved as '%s'.", output_file)


if __name__ == "__main__":
    # Use argparse to handle command-line arguments
    parser = argparse.ArgumentParser(
        description="Reads a TXT file, reorganizes the data, and converts it into a CSV file."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to the input TXT file. This file should contain sample names in columns and microbial taxa in rows.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to the output CSV file. The script will restructure the data and save it here.",
    )

    args = parser.parse_args()

    # Call function with parsed arguments
    convert_to_csv(args.input, args.output)
