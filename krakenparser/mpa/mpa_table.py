#!/usr/bin/env python
"""Combine multiple MPA-format files into a single merged table."""

import argparse
import logging
from pathlib import Path

from krakenparser.utils import ensure_output_dir

_log = logging.getLogger(__name__)


def combine_mpa(in_files: list[str], o_file: str) -> None:
    out_path = ensure_output_dir(o_file, is_file=True)

    samples: dict[int, str] = {}
    values: dict[str, dict[int, str]] = {}
    parent2child: dict[str, list[str]] = {}
    toparse: list[str] = []
    sample_count = 0

    _log.info("Number of files to parse: %d", len(in_files))

    for in_path in in_files:
        if not Path(in_path).is_file():
            raise FileNotFoundError(f"Input file not found: {in_path}")

    for in_path in in_files:
        sample_count += 1
        sample_name = f"Sample #{sample_count}"

        with open(in_path) as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line:
                    continue
                if line.startswith("#"):
                    cols = line.split("\t")
                    if len(cols) >= 2:
                        sample_name = cols[-1]
                    continue

                cols = line.split("\t", 1)
                if len(cols) < 2:
                    continue
                classification, val = cols[0], cols[1]

                split_vals = classification.split("|")
                curr_parent = ""
                for i in range(len(split_vals)):
                    test_val = "|".join(split_vals[:i])  # при i=0 → ""
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

    n_taxa = len(values)
    _log.info("Number of classifications to write: %d", n_taxa)

    count_written = 0
    with open(out_path, "w") as fh:
        header = "#Classification\t" + "\t".join(
            samples[i] for i in range(1, sample_count + 1)
        )
        fh.write(header + "\n")

        stack = list(toparse)
        while stack:
            curr = stack.pop(0)
            if curr in parent2child:
                stack = parent2child[curr] + stack
            row = "\t".join(
                values[curr].get(i, "0") for i in range(1, sample_count + 1)
            )
            fh.write(curr + "\t" + row + "\n")
            count_written += 1

    _log.info("%d classifications written", count_written)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(
        description="Combine MPA files into a single tab-delimited table."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        nargs="+",
        dest="in_files",
        help="Input MPA files (one per sample)",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        dest="o_file",
        help="Output merged MPA file",
    )
    args = parser.parse_args()
    combine_mpa(args.in_files, args.o_file)


if __name__ == "__main__":
    main()
