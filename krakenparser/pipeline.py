#!/usr/bin/env python
"""Full KrakenParser pipeline: kreport → MPA → combined → counts → rel_abund → diversity."""

import argparse
import logging
import shutil
import sys
from pathlib import Path

import pandas as pd

from krakenparser.counts.convert2csv import convert_to_csv
from krakenparser.counts.processing_script import process_files
from krakenparser.counts.split_mpa import split_mpa
from krakenparser.mpa.mpa_table import combine_mpa
from krakenparser.mpa.transform2mpa import kreport_to_mpa
from krakenparser.stats.diversity import calc_alpha_div, calc_beta_div
from krakenparser.stats.relabund import calculate_rel_abund

_log = logging.getLogger(__name__)


def _is_processable(path: Path) -> bool:
    """Return False for hidden files, files with null bytes, or non-UTF-8 files."""
    if path.name.startswith("."):
        return False
    try:
        chunk = path.read_bytes()[:1024]
        if b"\x00" in chunk:
            return False
        chunk.decode("utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        return False


_OUTPUT_SUBDIRS = ("intermediate", "counts", "rel_abund", "diversity")


def run_pipeline(
    input_dir: str,
    output_dir: str | None = None,
    keep_human: bool = False,
    rarefaction_depth: int = 1000,
    seed: int | None = None,
    overwrite: bool = False,
) -> None:
    source_dir = Path(input_dir)
    if not source_dir.is_dir():
        sys.exit(f"Error: input directory not found: {source_dir}")

    out_dir = Path(output_dir) if output_dir else source_dir.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    existing = [out_dir / d for d in _OUTPUT_SUBDIRS if (out_dir / d).exists()]
    if existing and not overwrite:
        names = ", ".join(d.name for d in existing)
        sys.exit(
            f"Error: output already exists in '{out_dir}' ({names}).\n"
            "Use --overwrite to overwrite it."
        )
    if overwrite:
        for d in existing:
            shutil.rmtree(d)
            _log.info("Removed existing directory: %s", d)

    intermediate_dir = out_dir / "intermediate"
    intermediate_dir.mkdir(exist_ok=True)

    # Part 1: kreport → MPA
    mpa_dir = intermediate_dir / "mpa"
    mpa_dir.mkdir(exist_ok=True)
    for f in sorted(source_dir.iterdir()):
        if not f.is_file():
            continue
        if not _is_processable(f):
            _log.info("Skipping: %s", f.name)
            continue
        out_name = f.stem + ".MPA.TXT"
        kreport_to_mpa(str(f), str(mpa_dir / out_name), display_header=True)

    # Part 2: combine MPAs
    mpa_files = sorted(mpa_dir.glob("*.MPA.TXT"))
    if not mpa_files:
        sys.exit("Error: no MPA files found after conversion.")
    combined_file = intermediate_dir / "COMBINED.txt"
    combine_mpa([str(f) for f in mpa_files], str(combined_file))
    _log.info("MPA files combined. Output: %s", combined_file)

    # Part 3: split combined MPA by rank
    split_mpa(str(combined_file), str(intermediate_dir), keep_human=keep_human)
    txt_dir = intermediate_dir / "txt"

    # Part 4: clean taxa names and add sample header
    for txt_file in sorted(txt_dir.glob("counts_*.txt")):
        process_files(str(combined_file), str(txt_file))

    # Part 5: TXT → CSV
    counts_dir = out_dir / "counts"
    counts_dir.mkdir(exist_ok=True)
    for txt_file in sorted(txt_dir.glob("counts_*.txt")):
        csv_file = counts_dir / txt_file.with_suffix(".csv").name
        convert_to_csv(str(txt_file), str(csv_file))

    # Part 6: relative abundance
    rel_abund_dir = out_dir / "rel_abund"
    rel_abund_dir.mkdir(exist_ok=True)
    for csv_file in sorted(counts_dir.glob("counts_*.csv")):
        ra_file = rel_abund_dir / csv_file.name.replace("counts_", "ra_")
        calculate_rel_abund(str(csv_file), str(ra_file))

    # Part 7: α & β-diversities
    species_csv = counts_dir / "counts_species.csv"
    if not species_csv.exists():
        sys.exit(f"Error: species counts not found: {species_csv}")
    diversity_dir = out_dir / "diversity"
    diversity_dir.mkdir(exist_ok=True)
    df = pd.read_csv(species_csv, index_col=0)
    calc_alpha_div(df, diversity_dir)
    calc_beta_div(df, diversity_dir, rarefaction_depth=rarefaction_depth, seed=seed)

    _log.info("All steps completed successfully!")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="Run the full KrakenParser pipeline.")
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Directory containing Kraken2 report files",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output directory (default: parent of input)",
    )
    parser.add_argument(
        "--keep-human",
        action="store_true",
        default=False,
        help="Do not filter human-related taxa (default: filtered)",
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=1000,
        help="Rarefaction depth for β-diversity (default: 1000)",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible rarefaction (default: random)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite the output directory if it already exists",
    )
    args = parser.parse_args()
    run_pipeline(
        args.input,
        args.output,
        keep_human=args.keep_human,
        rarefaction_depth=args.depth,
        seed=args.seed,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
