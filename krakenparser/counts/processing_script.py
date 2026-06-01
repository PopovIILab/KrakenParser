#!/usr/bin/env python

import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

import typer

_log = logging.getLogger(__name__)

app = typer.Typer(
    name="process",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def modify_taxa_names(line: str) -> str:
    prefixes = ["s__", "g__", "f__", "o__", "c__", "p__"]
    for prefix in prefixes:
        if line.startswith(prefix):
            parts = line[len(prefix) :].split("\t")
            parts[0] = parts[0].replace("_", " ")
            return "\t".join(parts)
    return line


def process_files(source_file: str, destination_file: str) -> None:
    src_path = Path(source_file)
    if not src_path.is_file():
        raise FileNotFoundError(f"Source file not found: {src_path}")
    dest_path = Path(destination_file)
    if not dest_path.is_file():
        raise FileNotFoundError(f"Destination file not found: {dest_path}")

    # Read the first line from the source file and modify it
    with open(src_path, "r") as file:
        first_line_source = file.readline()
    modified_first_line = "\t".join(
        word.split(".")[0] for word in first_line_source.split()
    )

    # Read all content from the destination file and modify taxa names
    with open(dest_path, "r") as file:
        lines = file.readlines()
    modified_lines = [modify_taxa_names(line.strip()) for line in lines]

    # Combine the modified first line with the modified content of the destination file
    updated_content = modified_first_line + "\n" + "\n".join(modified_lines)

    # Write atomically: write to a temp file in the same directory, then replace
    with tempfile.NamedTemporaryFile(
        mode="w", dir=dest_path.parent, delete=False, suffix=".tmp"
    ) as tmp:
        tmp.write(updated_content)
        tmp_path = tmp.name
    os.replace(tmp_path, dest_path)

    _log.info(f"Processed {destination_file} successfully.")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    input_file: Optional[str] = typer.Option(
        None,
        "-i",
        "--input",
        help="Path to the source file. This file's first line will be read and modified.",
    ),
    output_file: Optional[str] = typer.Option(
        None,
        "-o",
        "--output",
        help="Path to the destination file. This file's contents will be updated with cleaned taxa names.",
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
