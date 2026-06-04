#!/usr/bin/env python3
"""Taxonomic format converter translating Kraken2 reports to MetaPhlAn (MPA) layout.

This module parses standard space-indented hierarchical Kraken2 and KrakenUniq output
reports, tracks taxonomic depth changes through parent lineage state machines,
and converts records into pipe-separated '|' multi-level lineage tracks.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Optional

import typer

from krakenparser.utils import ensure_output_dir

# Initialize module-level isolated logger
_log: logging.Logger = logging.getLogger(__name__)

# Dedicated Typer routing application instantiation
app: typer.Typer = typer.Typer(
    name="mpa",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Standard strict taxonomic reference limits
_MAIN_LVLS: set[str] = {"R", "K", "D", "P", "C", "O", "F", "G", "S"}


def _parse_line(line: str, remove_spaces: bool = False) -> list:
    """Parse a single Kraken2 or KrakenUniq report row and extract vital stats.

    Handles standard kraken formats alongside KrakenUniq outputs by mapping text
    labels to fixed-width single-character taxonomic rank designators.

    Args:
        line: A raw tab-delimited line from the report file.
        remove_spaces: If True, internal spaces within organism nomenclature
            strings are mapped securely to structural underscores.

    Returns:
        list: A data list containing [cleaned_name, level_num, level_type, total_reads, relative_percentage]
            or an empty list [] if the line format violates parser syntactic assumptions.
    """
    parts: list[str] = line.rstrip("\n").split("\t")
    if len(parts) < 4:
        return []

    try:
        percents: float = float(parts[0])
        all_reads: int = int(parts[1])
    except ValueError:
        return []

    # Detect and handle alternative KrakenUniq columns format if applicable
    try:
        int(parts[-3])
        level_type: str = parts[-2].strip()
        map_kuniq: dict[str, str] = {
            "species": "S",
            "genus": "G",
            "family": "F",
            "order": "O",
            "class": "C",
            "phylum": "P",
            "superkingdom": "D",
            "kingdom": "K",
        }
        level_type = map_kuniq.get(level_type, "-")
    except ValueError:
        level_type = parts[-3].strip()

    raw_name: str = parts[-1]

    # High-performance calculation of leading double-space indentation metrics
    spaces: int = len(raw_name) - len(raw_name.lstrip(" "))
    name: str = raw_name.strip()

    if remove_spaces:
        name = name.replace(" ", "_")

    level_num: float = spaces / 2
    return [name, level_num, level_type, all_reads, percents]


def kreport_to_mpa(
    report_path: Path,
    output_path: Path,
    display_header: bool = False,
    include_intermediate: bool = False,
    use_reads: bool = True,
    remove_spaces: bool = True,
) -> None:
    """Transform an individual Kraken2 report matrix file into an MPA lineage table.

    Iterates over lines sequentially, dynamically collapsing or expanding an internal
    lineage stack buffer when tracking changes in indentation depths.

    Args:
        report_path: Path to the validated incoming raw text file.
        output_path: Path where the converted tracking table will be dumped.
        display_header: If True, writes a header indicating source provenance metadata.
        include_intermediate: If True, non-standard ranks are preserved under 'x__' tags.
        use_reads: If True, maps absolute counts. If False, streams relative percentage scores.
        remove_spaces: If True, replaces standard word spaces inside strings with underscores.

    Raises:
        FileNotFoundError: Triggered if the target source input file is not found.
    """
    if not report_path.is_file():
        raise FileNotFoundError(f"Input file not found: {report_path}")

    out_path: Path = ensure_output_dir(output_path, is_file=True)

    curr_path: list[str] = []
    prev_lvl_num: float = -1.0

    with (
        open(report_path, encoding="utf-8") as r_fh,
        open(out_path, "w", encoding="utf-8") as o_fh,
    ):
        if display_header:
            o_fh.write(f"#Classification\t{report_path.name}\n")

        for line in r_fh:
            report_vals = _parse_line(line, remove_spaces)
            if report_vals is None:
                continue

            name, level_num, level_type, all_reads, percents = report_vals

            # Safely drop unclassified sequencing categories ('U')
            if level_type == "U":
                continue

            # Standardize non-canonical levels to match MetaPhlAn structural styles
            if level_type not in _MAIN_LVLS:
                level_type = "x"
            elif level_type == "K":
                level_type = "k"
            elif level_type == "D":
                level_type = "d"

            level_str: str = f"{level_type.lower()}__{name}"

            # Setup baseline root node conditions
            if prev_lvl_num == -1.0:
                prev_lvl_num = level_num
                curr_path.append(level_str)
                continue

            # Step out of current lineage stack frames if depth levels step backward
            while level_num != (prev_lvl_num + 1.0):
                prev_lvl_num -= 1.0
                curr_path.pop()

            # Conditionally pipe clean taxonomy paths down to file IO streams
            if (level_type == "x" and include_intermediate) or level_type != "x":
                ancestors: list[str] = [
                    seg
                    for seg in curr_path
                    if (seg[0] != "x" or include_intermediate) and seg[0] != "r"
                ]
                path: str = "|".join(ancestors + [level_str])
                value: str = str(all_reads) if use_reads else str(percents)
                o_fh.write(f"{path}\t{value}\n")

            curr_path.append(level_str)
            prev_lvl_num = level_num


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    r_file: Optional[Path] = typer.Option(
        None,
        "-r",
        "--report-file",
        "--report",
        help="Single input Kraken2 report file.",
    ),
    input_dir: Optional[Path] = typer.Option(
        None,
        "-i",
        "--input",
        help="Input directory containing Kraken2 report files (batch mode).",
    ),
    o_file: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output MPA file (single mode) or output directory (batch mode).",
    ),
    display_header: bool = typer.Option(
        False,
        "--display-header",
        help="Write a header line with the sample name (filename).",
    ),
    percentages: bool = typer.Option(
        False,
        "--percentages",
        help="Output percentages instead of read counts.",
    ),
    intermediate_ranks: bool = typer.Option(
        False,
        "--intermediate-ranks",
        help="Include non-standard taxonomic ranks in output.",
    ),
    keep_spaces: bool = typer.Option(
        False,
        "--keep-spaces",
        help="Keep spaces in taxon names instead of replacing them with underscores.",
    ),
) -> None:
    """Convert a Kraken2 report to MetaPhlAn (MPA) format."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if r_file is None and input_dir is None and o_file is None:
        print(ctx.get_help())
        raise typer.Exit()

    if o_file is None:
        print("Error: Missing required option '-o / --output'.", file=sys.stderr)
        raise typer.Exit(code=1)

    if r_file is None and input_dir is None:
        print(
            "Error: Either -r/--report-file or -i/--input must be provided.",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)

    if r_file is not None and input_dir is not None:
        print(
            "Error: Cannot use both -r/--report-file and -i/--input simultaneously.",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)

    use_reads: bool = not percentages
    remove_spaces: bool = not keep_spaces

    kwargs: dict[str, Any] = dict(
        display_header=display_header,
        include_intermediate=intermediate_ranks,
        use_reads=use_reads,
        remove_spaces=remove_spaces,
    )

    try:
        if input_dir:
            if not input_dir.is_dir():
                print(f"Error: input directory not found: {input_dir}", file=sys.stderr)
                raise typer.Exit(code=1)

            o_file.mkdir(parents=True, exist_ok=True)
            for f in sorted(input_dir.iterdir()):
                if not f.is_file():
                    continue
                out_name: str = f.name.replace(".kreport", ".MPA.TXT")
                kreport_to_mpa(f, o_file / out_name, **kwargs)
            _log.info("Converted to MPA successfully. Output stored in %s", o_file)
        else:
            assert r_file is not None, (
                "Internal error: r_file is missing in singleton mode."
            )
            kreport_to_mpa(r_file, o_file, **kwargs)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
