#!/usr/bin/env python
"""Combine multiple MPA-format files into a single merged table."""

import argparse
import logging

_log = logging.getLogger(__name__)


def combine_mpa(in_files: list[str], o_file: str) -> None:
    # Plain dict preserves insertion order (Python 3.7+).
    taxa: dict[str, dict[int, str]] = {}
    sample_names: list[str] = []

    _log.info("Number of files to parse: %d", len(in_files))

    for idx, in_path in enumerate(in_files):
        sample_name = f"Sample #{idx + 1}"
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
                taxon, count = cols[0], cols[1]
                if taxon not in taxa:
                    taxa[taxon] = {}
                taxa[taxon][idx] = count
        sample_names.append(sample_name)

    n_samples = len(sample_names)
    n_taxa = len(taxa)
    _log.info("Number of classifications to write: %d", n_taxa)

    with open(o_file, "w") as fh:
        fh.write("#Classification\t" + "\t".join(sample_names) + "\n")
        for taxon, counts in taxa.items():
            row = [counts.get(i, "0") for i in range(n_samples)]
            fh.write(taxon + "\t" + "\t".join(row) + "\n")

    _log.info("%d classifications written", n_taxa)


def main() -> None:
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
