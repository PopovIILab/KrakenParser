#!/usr/bin/env python
"""Convert a Kraken2 report to MetaPhlAn (MPA) format."""

import argparse
import os
import sys
from pathlib import Path

# Maps Kraken2 single-letter rank codes to MPA prefixes
_RANK_PREFIX = {
    "D": "d",
    "K": "k",
    "P": "p",
    "C": "c",
    "O": "o",
    "F": "f",
    "G": "g",
    "S": "s",
}


def _parse_line(line: str):
    """
    Parse one Kraken2 report line.

    Standard format (6 columns):
        pct  cum_reads  direct_reads  rank  taxid  name(indented)

    Returns (name, depth, rank, cum_reads, pct) or None on malformed input.
    """
    parts = line.rstrip("\n").split("\t")
    if len(parts) < 5:
        return None
    try:
        pct = float(parts[0])
        cum_reads = int(parts[1])
    except ValueError:
        return None

    rank = parts[3].strip()
    name_field = parts[-1]  # always the last column regardless of format variant

    depth = 0
    for ch in name_field:
        if ch == " ":
            depth += 1
        else:
            break
    name = name_field.strip()

    return name, depth // 2, rank, cum_reads, pct


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

    Uses a stack to track the current taxonomic path. Each entry is
    (structural_depth, mpa_segment, is_standard_rank). When a node at
    depth d is encountered, all stack entries with depth >= d are popped
    before the new entry is pushed, keeping the path consistent.
    """
    # Stack entries: (structural_depth, mpa_segment, is_standard_rank)
    stack: list[tuple[int, str, bool]] = []

    with open(report_path) as r_fh, open(output_path, "w") as o_fh:
        if display_header:
            o_fh.write("#Classification\t" + os.path.basename(report_path) + "\n")

        for line in r_fh:
            parsed = _parse_line(line)
            if parsed is None:
                continue
            name, depth, rank, cum_reads, pct = parsed

            # Skip unclassified and root — never appear in MPA output
            if rank in ("U", "R"):
                continue

            # Strip numeric suffix to get base rank (e.g. "S1" → "S", "G2" → "G")
            rank_base = rank.rstrip("0123456789")
            is_standard = rank_base in _RANK_PREFIX and rank == rank_base

            if not is_standard and not include_intermediate:
                continue

            prefix = _RANK_PREFIX.get(rank_base, "x")
            seg_name = name.replace(" ", "_") if remove_spaces else name
            mpa_seg = f"{prefix}__{seg_name}"

            # Trim stack to the current structural depth
            while stack and stack[-1][0] >= depth:
                stack.pop()
            stack.append((depth, mpa_seg, is_standard))

            # Build the full MPA path; omit intermediate (x__) segments when not requested
            path = "|".join(
                seg for (_, seg, std) in stack if include_intermediate or std
            )

            value = str(cum_reads) if use_reads else str(pct)
            o_fh.write(f"{path}\t{value}\n")


def main() -> None:
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
        print(f"Converted to MPA successfully. Output stored in {output_dir}")
    else:
        kreport_to_mpa(args.r_file, args.o_file, **kwargs)


if __name__ == "__main__":
    main()
