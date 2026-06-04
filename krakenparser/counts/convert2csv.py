#!/usr/bin/env python3
"""Matrix manipulation utility for restructuring metagenomic abundance tables.

This module converts tab-delimited abundance tables (traditionally structured
with features/taxa as rows and samples as columns) into standardized,
transposed CSV sheets conforming to the tidy data format (samples as rows).
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import typer

from krakenparser.utils import ensure_output_dir

# Initialize module-level isolated logger
_log: logging.Logger = logging.getLogger(__name__)

# Dedicated Typer routing application instantiation
app: typer.Typer = typer.Typer(
    name="csv",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def convert_to_csv(input_file: Path, output_file: Path) -> None:
    """Transpose a tab-separated matrix and export it as a sample-centric CSV.

    Reads a matrix where columns represent samples and rows represent taxa,
    performs an algebraic transposition operation (.T), and locks the new row
    index under the canonical 'Sample_id' header label.

    Args:
        input_file: Path to the validated incoming tab-separated matrix file.
        output_file: Target path where the restructured CSV matrix will be dumped.

    Raises:
        FileNotFoundError: Triggered if the specified input text resource is missing.
    """
    if not input_file.is_file():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    out_path: Path = ensure_output_dir(output_file, is_file=True)

    # Load high-dimensional matrix (Rows: Taxa, Columns: Samples)
    data: pd.DataFrame = pd.read_csv(input_file, sep="\t", index_col=0)

    # Execute matrix transposition to shift samples to rows (Tidy Data layout)
    data.T.to_csv(out_path, index_label="Sample_id")

    _log.info("Data successfully transposed and saved to '%s'.", output_file)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    input_file: Optional[Path] = typer.Option(
        None,
        "-i",
        "--input",
        help="Path to the input tab-delimited TXT file (samples in columns, taxa in rows).",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Path to the output transposed CSV file.",
    ),
) -> None:
    """Reads a TXT file, reorganizes the data, and converts it into a CSV file."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if input_file is None and output_file is None:
        print(ctx.get_help())
        raise typer.Exit()

    if not input_file or not output_file:
        print("Error: Missing required options '-i / --input' and '-o / --output'.")
        raise typer.Exit(code=1)

    try:
        convert_to_csv(input_file, output_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
