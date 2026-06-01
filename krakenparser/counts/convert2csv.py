#!/usr/bin/env python
import logging
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import typer

from krakenparser.utils import ensure_output_dir

_log = logging.getLogger(__name__)

app = typer.Typer(
    name="csv",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def convert_to_csv(input_file: str, output_file: str) -> None:
    in_path = Path(input_file)
    if not in_path.is_file():
        raise FileNotFoundError(f"Input file not found: {in_path}")
    out_path = ensure_output_dir(output_file, is_file=True)

    data = pd.read_csv(in_path, sep="\t", index_col=0)
    data.T.to_csv(out_path, index_label="Sample_id")
    _log.info("Data converted and saved as '%s'.", output_file)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,  # Контекст для нативного хелпа
    input_file: Optional[str] = typer.Option(
        None,
        "-i",
        "--input",
        help="Path to the input TXT file. This file should contain sample names in columns and microbial taxa in rows.",
    ),
    output_file: Optional[str] = typer.Option(
        None,
        "-o",
        "--output",
        help="Path to the output CSV file. The script will restructure the data and save it here.",
    ),
) -> None:
    """Reads a TXT file, reorganizes the data, and converts it into a CSV file."""
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
        convert_to_csv(input_file, output_file)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
