#!/usr/bin/env python3
"""Aggregation engine for merging multiple MetaPhlAn (MPA) files into a unified matrix.

This module parses multi-sample taxonomic report files formatted in the MetaPhlAn
style, extracts their respective abundance sequences, tracks phylogenetic tree
parent-child relationships, and performs a stack-based traversal to output a
structurally ordered, tab-delimited master count matrix.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer

from krakenparser.utils import ensure_output_dir

# Initialize module-level isolated logger
_log: logging.Logger = logging.getLogger(__name__)

# Dedicated Typer routing application instantiation
app: typer.Typer = typer.Typer(
    name="combine",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def combine_mpa(in_files: list[Path], o_file: Path) -> None:
    """Merge separate MPA taxonomic distribution tables into a single master matrix.

    Parses header metadata strings to resolve human-readable sample IDs, caches
    hierarchical dependencies to maintain strict lineage orientation, and combines
    individual abundance values into an integrated layout table.

    Args:
        in_files: List of validated Path objects directing to sample MPA files.
        o_file: Target Path where the combined tab-delimited table will be written.

    Raises:
        FileNotFoundError: Triggered if any referenced input file is absent.
    """
    out_path: Path = ensure_output_dir(o_file, is_file=True)

    # Architectural storage definitions for parsing alignment graphs
    samples: dict[int, str] = {}
    values: dict[str, dict[int, str]] = {}
    parent2child: dict[str, list[str]] = {}
    toparse: list[str] = []
    sample_count: int = 0

    _log.info("Number of files to parse: %d", len(in_files))

    # Atomic verification step protecting IO transactions
    for in_path in in_files:
        if not in_path.is_file():
            raise FileNotFoundError(f"Input file not found: {in_path}")

    # Step 1: Scan individual reports and populate hierarchical graphs
    for in_path in in_files:
        sample_count += 1
        sample_name: str = f"Sample #{sample_count}"

        with open(in_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line:
                    continue

                # Isolate and extract sample identifier mapping embedded within headers
                if line.startswith("#"):
                    cols: list[str] = line.split("\t")
                    if len(cols) >= 2:
                        sample_name = cols[-1]
                    continue

                cols = line.split("\t", 1)
                if len(cols) < 2:
                    continue
                classification, val = cols[0], cols[1]

                # Resolve lineage parent node identities to guarantee structural order
                split_vals: list[str] = classification.split("|")
                curr_parent: str = ""
                for i in range(len(split_vals)):
                    test_val: str = "|".join(split_vals[:i])
                    if test_val in values:
                        curr_parent = test_val

                if curr_parent == "":
                    if classification not in toparse:
                        toparse.append(classification)
                else:
                    if curr_parent not in parent2child:
                        parent2child[curr_parent] = []
                    if classification not in parent2child[curr_parent]:
                        parent2child[curr_parent].append(classification)

                if classification not in values:
                    values[classification] = {}
                values[classification][sample_count] = val

        samples[sample_count] = sample_name

    n_taxa: int = len(values)
    _log.info("Number of classifications to write: %d", n_taxa)

    # Step 2: Traverse graph using a stack buffer to stream records layout-ready
    count_written: int = 0
    with open(out_path, "w", encoding="utf-8") as fh:
        header: str = "#Classification\t" + "\t".join(
            samples[i] for i in range(1, sample_count + 1)
        )
        fh.write(header + "\n")

        stack: list[str] = list(toparse)
        while stack:
            curr: str = stack.pop(0)
            if curr in parent2child:
                stack = parent2child[curr] + stack

            row: str = "\t".join(
                values[curr].get(i, "0") for i in range(1, sample_count + 1)
            )
            fh.write(curr + "\t" + row + "\n")
            count_written += 1

    _log.info("%d classifications written", count_written)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    in_files: Optional[list[Path]] = typer.Option(
        None,
        "-i",
        "--input",
        help="Input MPA files (one per sample). Repeat the '-i' option for multiple files.",
    ),
    o_file: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output merged MPA file path.",
    ),
) -> None:
    """Combine MPA files into a single tab-delimited table."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if not in_files and o_file is None:
        print(ctx.get_help())
        raise typer.Exit()

    if not in_files or o_file is None:
        print(
            "Error: Missing required options '-i / --input' and '-o / --output'.",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)

    try:
        combine_mpa(in_files, o_file)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
