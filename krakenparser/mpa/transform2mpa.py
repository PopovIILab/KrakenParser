#!/usr/bin/env python
"""Convert a Kraken2 report to MetaPhlAn (MPA) format."""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

import typer

from krakenparser.utils import ensure_output_dir

_log = logging.getLogger(__name__)

app = typer.Typer(
    name="mpa",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

_MAIN_LVLS = {"R", "K", "D", "P", "C", "O", "F", "G", "S"}


def _parse_line(line: str, remove_spaces: bool = False) -> list:
    """Parse one Kraken2 report line.

    Returns [name, level_num, level_type, all_reads, percents]
    or empty list on malformed input.
    """
    parts = line.rstrip("\n").split("\t")
    if len(parts) < 4:
        return []
    try:
        int(parts[1])
    except ValueError:
        return []

    try:
        percents = float(parts[0])
    except ValueError:
        return []
    all_reads = int(parts[1])

    try:
        int(parts[-3])
        level_type = parts[-2].strip()
        map_kuniq = {
            "species": "S",
            "genus": "G",
            "family": "F",
            "order": "O",
            "class": "C",
            "phylum": "P",
            "superkingdom": "D",
            "kingdom": "K",
        }
        if level_type not in map_kuniq:
            level_type = "-"
        else:
            level_type = map_kuniq[level_type]
    except ValueError:
        level_type = parts[-3].strip()

    name = parts[-1]
    spaces = 0
    for ch in name:
        if ch == " ":
            spaces += 1
        else:
            break
    name = name.strip()
    if remove_spaces:
        name = name.replace(" ", "_")

    level_num = spaces / 2
    return [name, level_num, level_type, all_reads, percents]


def kreport_to_mpa(
    report_path: Path,
    output_path: Path,
    display_header: bool = False,
    include_intermediate: bool = False,
    use_reads: bool = True,
    remove_spaces: bool = True,
) -> None:
    """Convert a single Kraken2 report to MPA format."""
    if not report_path.is_file():
        raise FileNotFoundError(f"Input file not found: {report_path}")
    out_path = ensure_output_dir(str(output_path), is_file=True)

    curr_path: list[str] = []
    prev_lvl_num = -1

    with open(report_path) as r_fh, open(out_path, "w") as o_fh:
        if display_header:
            o_fh.write("#Classification\t" + os.path.basename(report_path) + "\n")

        for line in r_fh:
            report_vals = _parse_line(line, remove_spaces)
            if len(report_vals) < 5:
                continue

            name, level_num, level_type, all_reads, percents = report_vals

            if level_type == "U":
                continue

            if level_type not in _MAIN_LVLS:
                level_type = "x"
            elif level_type == "K":
                level_type = "k"
            elif level_type == "D":
                level_type = "d"

            level_str = level_type.lower() + "__" + name

            if prev_lvl_num == -1:
                prev_lvl_num = level_num
                curr_path.append(level_str)
                continue

            while level_num != (prev_lvl_num + 1):
                prev_lvl_num -= 1
                curr_path.pop()

            if (level_type == "x" and include_intermediate) or level_type != "x":
                ancestors = [
                    seg
                    for seg in curr_path
                    if (seg[0] != "x" or include_intermediate) and seg[0] != "r"
                ]
                path = "|".join(ancestors + [level_str])
                value = str(all_reads) if use_reads else str(percents)
                o_fh.write(path + "\t" + value + "\n")

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

    use_reads = not percentages
    remove_spaces = not keep_spaces

    kwargs = dict(
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
                out_name = f.name.replace(".kreport", ".MPA.TXT")
                kreport_to_mpa(f, o_file / out_name, **kwargs)
            _log.info("Converted to MPA successfully. Output stored in %s", o_file)
        else:
            kreport_to_mpa(r_file, o_file, **kwargs)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
