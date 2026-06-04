#!/usr/bin/env python3
"""Post-processing matrix utility for metadata refinement and taxonomic sanitization.

This module cleans upstream pipeline artifacts by removing technical file extensions
from sample headers and restoring canonical spaces to underscore-separated taxonomic
nomenclature strings (e.g., converting 's__Escherichia_coli' to 'Escherichia coli').
File mutations are executed via atomic filesystem transactions.
"""

import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

import typer

# Initialize module-level isolated logger
_log: logging.Logger = logging.getLogger(__name__)

# Dedicated Typer routing application instantiation
app: typer.Typer = typer.Typer(
    name="process",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def modify_taxa_names(line: str) -> str:
    """Sanitize taxonomic names by replacing internal underscores with spaces.

    Scans the line for standard taxonomic rank prefixes (s__, g__, etc.). If found,
    the primary taxon descriptor string is decoupled, sanitized of internal
    technical underscores, and reconstructed while preserving tailing tab metrics.

    Args:
        line: A raw text row from the matrix containing taxonomic descriptors.

    Returns:
        str: The structurally preserved string with restored space characters.
    """
    prefixes: list[str] = ["s__", "g__", "f__", "o__", "c__", "p__"]
    for prefix in prefixes:
        if line.startswith(prefix):
            # Clean string parsing utilizing standard tab separation matrices
            parts: list[str] = line.removeprefix(prefix).split("\t")
            parts[0] = parts[0].replace("_", " ")
            return "\t".join(parts)
    return line


def process_files(source_file: Path, destination_file: Path) -> None:
    """Synchronize matrix headers and sanitize taxonomic profiles atomically.

    Extracts clean cohort descriptors from the header of a source tracker,
    applies string cleaning to a targeted taxonomy mapping spreadsheet,
    and updates the destination file utilizing atomic replacement blocks.

    Args:
        source_file: Validated Path to the template matrix containing pristine headers.
        destination_file: Target Path to the file undergoing line-by-line taxonomy cleaning.

    Raises:
        FileNotFoundError: Triggered if either the source or destination targets are absent.
    """
    if not source_file.is_file():
        raise FileNotFoundError(f"Source file not found: {source_file}")
    if not destination_file.is_file():
        raise FileNotFoundError(f"Destination file not found: {destination_file}")

    # Step 1: Read and truncate raw pipeline suffixes from sample headers
    with open(source_file, "r", encoding="utf-8") as file:
        first_line_source: str = file.readline()

    modified_first_line: str = "\t".join(
        word.split(".")[0] for word in first_line_source.split()
    )

    # Step 2: Read targets and map taxonomic updates lazily across lists
    with open(destination_file, "r", encoding="utf-8") as file:
        lines: list[str] = file.readlines()

    modified_lines: list[str] = [modify_taxa_names(line.strip()) for line in lines]

    # Step 3: Integrate matrices and commit layout modifications to disk
    joined_lines: str = "\n".join(modified_lines)
    updated_content: str = f"{modified_first_line}\n{joined_lines}"

    # Secure atomic writer operations targeting adjacent scratch space regions
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=destination_file.parent,
        delete=False,
        suffix=".tmp",
        encoding="utf-8",
    ) as tmp:
        tmp.write(updated_content)
        tmp_path: str = tmp.name

    # Commit transactions atomically across POSIX virtual environments
    os.replace(tmp_path, destination_file)
    _log.info("Processed '%s' successfully.", destination_file)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    input_file: Optional[Path] = typer.Option(
        None,
        "-i",
        "--input",
        help="Path to the source file (used to extract and truncate header labels).",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Path to the destination matrix undergoing taxonomic name sanitation.",
    ),
) -> None:
    """Reads a source file, processes its first line, modifies taxa names in a destination file, and updates it."""
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
        process_files(input_file, output_file)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
