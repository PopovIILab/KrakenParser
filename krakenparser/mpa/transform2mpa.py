#!/usr/bin/env python
"""Convert a Kraken2 report to MetaPhlAn (MPA) format."""

import argparse
import logging
import os
import sys
from pathlib import Path

from krakenparser.utils import ensure_output_dir

_log = logging.getLogger(__name__)

_MAIN_LVLS = {"R", "K", "D", "P", "C", "O", "F", "G", "S"}


def _parse_line(line: str, remove_spaces: bool = False) -> list:
    """
    Parse one Kraken2 report line.

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
    report_path: str,
    output_path: str,
    display_header: bool = False,
    include_intermediate: bool = False,
    use_reads: bool = True,
    remove_spaces: bool = True,
) -> None:
    """
    Convert a single Kraken2 report to MPA format.

    Tracks the current taxonomic path via curr_path and prev_lvl_num,
    popping the stack when moving back up the tree — exactly as the
    original script does.
    """
    if not Path(report_path).is_file():
        raise FileNotFoundError(f"Input file not found: {report_path}")
    out_path = ensure_output_dir(output_path, is_file=True)

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

            # Пропускаем unclassified
            if level_type == "U":
                continue

            # Нормализуем тип уровня
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


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(
        description="Convert a Kraken2 report to MetaPhlAn (MPA) format."
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "-r",
        "--report-file",
        "--report",
        dest="r_file",
        help="Single input Kraken2 report file",
    )
    mode.add_argument(
        "-i",
        "--input",
        dest="input_dir",
        help="Input directory containing Kraken2 report files (batch mode)",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        dest="o_file",
        help="Output MPA file (single mode) or output directory (batch mode)",
    )
    parser.add_argument(
        "--display-header",
        action="store_true",
        dest="add_header",
        default=False,
        help="Write a header line with the sample name (filename)",
    )
    parser.add_argument(
        "--read_count",
        action="store_true",
        dest="use_reads",
        default=True,
        help="Output clade read counts [default]",
    )
    parser.add_argument(
        "--percentages",
        action="store_false",
        dest="use_reads",
        help="Output percentages instead of read counts",
    )
    parser.add_argument(
        "--intermediate-ranks",
        action="store_true",
        dest="x_include",
        default=False,
        help="Include non-standard taxonomic ranks in output",
    )
    parser.add_argument(
        "--no-intermediate-ranks",
        action="store_false",
        dest="x_include",
        help="Exclude non-standard taxonomic ranks [default]",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--remove-spaces",
        action="store_true",
        dest="remove_spaces",
        default=True,
        help="Replace spaces with underscores in taxon names [default]",
    )
    group.add_argument(
        "--keep-spaces",
        action="store_false",
        dest="remove_spaces",
        help="Keep spaces in taxon names",
    )
    args = parser.parse_args()

    kwargs = dict(
        display_header=args.add_header,
        include_intermediate=args.x_include,
        use_reads=args.use_reads,
        remove_spaces=args.remove_spaces,
    )

    if args.input_dir:
        input_dir = Path(args.input_dir)
        if not input_dir.is_dir():
            sys.exit(f"Error: input directory not found: {input_dir}")
        output_dir = Path(args.o_file)
        output_dir.mkdir(parents=True, exist_ok=True)
        for f in sorted(input_dir.iterdir()):
            if not f.is_file():
                continue
            out_name = f.name.replace(".kreport", ".MPA.TXT")
            kreport_to_mpa(str(f), str(output_dir / out_name), **kwargs)
        _log.info("Converted to MPA successfully. Output stored in %s", output_dir)
    else:
        kreport_to_mpa(args.r_file, args.o_file, **kwargs)


if __name__ == "__main__":
    main()
