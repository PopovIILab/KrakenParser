#!/usr/bin/env python
"""Full KrakenParser pipeline: kreport → MPA → combined → counts → rel_abund → diversity."""

import logging
import shutil
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import typer

from krakenparser.counts.convert2csv import convert_to_csv
from krakenparser.counts.processing_script import process_files
from krakenparser.counts.split_mpa import split_mpa
from krakenparser.mpa.mpa_table import combine_mpa
from krakenparser.mpa.transform2mpa import kreport_to_mpa
from krakenparser.stats.diversity import calc_alpha_div, calc_beta_div
from krakenparser.stats.relabund import calculate_rel_abund

_log = logging.getLogger(__name__)

app = typer.Typer(
    name="run",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


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
    input_dir: Path,
    output_dir: Optional[Path] = None,
    keep_human: bool = False,
    viruses_only: bool = False,
    bacteria_only: bool = False,
    fungi_only: bool = False,
    archaea_only: bool = False,
    rarefaction_depth: int = 1000,
    seed: Optional[int] = None,
    overwrite: bool = False,
) -> None:
    source_dir = input_dir
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {source_dir}")

    out_dir = output_dir if output_dir else source_dir.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    existing = [out_dir / d for d in _OUTPUT_SUBDIRS if (out_dir / d).exists()]
    if existing and not overwrite:
        names = ", ".join(d.name for d in existing)
        raise FileExistsError(
            f"Output already exists in '{out_dir}' ({names}).\n"
            "Use --overwrite to overwrite it."
        )
    if overwrite:
        for d in existing:
            shutil.rmtree(d)
            _log.info("Removed existing directory: %s", d)

    intermediate_dir = out_dir / "intermediate"
    intermediate_dir.mkdir(exist_ok=True)

    mpa_dir = intermediate_dir / "mpa"
    mpa_dir.mkdir(exist_ok=True)
    for f in sorted(source_dir.iterdir()):
        if not f.is_file():
            continue
        if not _is_processable(f):
            _log.info("Skipping: %s", f.name)
            continue
        out_name = f.stem + ".MPA.TXT"
        kreport_to_mpa(f, mpa_dir / out_name, display_header=True)

    mpa_files = sorted(mpa_dir.glob("*.MPA.TXT"))
    if not mpa_files:
        print("Error: no MPA files found after conversion.", file=sys.stderr)
        raise typer.Exit(code=1)
    combined_file = intermediate_dir / "COMBINED.txt"
    combine_mpa(mpa_files, combined_file)
    _log.info("MPA files combined. Output: %s", combined_file)

    split_mpa(
        str(combined_file),
        str(intermediate_dir),
        keep_human=keep_human,
        viruses_only=viruses_only,
        bacteria_only=bacteria_only,
        fungi_only=fungi_only,
        archaea_only=archaea_only,
    )
    txt_dir = intermediate_dir / "txt"

    for txt_file in sorted(txt_dir.glob("counts_*.txt")):
        process_files(str(combined_file), str(txt_file))

    counts_dir = out_dir / "counts"
    counts_dir.mkdir(exist_ok=True)
    for txt_file in sorted(txt_dir.glob("counts_*.txt")):
        csv_file = counts_dir / txt_file.with_suffix(".csv").name
        convert_to_csv(str(txt_file), str(csv_file))

    rel_abund_dir = out_dir / "rel_abund"
    rel_abund_dir.mkdir(exist_ok=True)
    for csv_file in sorted(counts_dir.glob("counts_*.csv")):
        ra_file = rel_abund_dir / csv_file.name.replace("counts_", "ra_")
        calculate_rel_abund(csv_file, ra_file)

    species_csv = counts_dir / "counts_species.csv"
    if not species_csv.exists():
        print(f"Error: species counts not found: {species_csv}", file=sys.stderr)
        raise typer.Exit(code=1)
    diversity_dir = out_dir / "diversity"
    diversity_dir.mkdir(exist_ok=True)
    df = pd.read_csv(species_csv, index_col=0)
    calc_alpha_div(df, diversity_dir)
    calc_beta_div(df, diversity_dir, rarefaction_depth=rarefaction_depth, seed=seed)

    _log.info("All steps completed successfully!")


@app.command(
    help="Run the full KrakenParser pipeline.",
    no_args_is_help=True,
)
def main(
    input_dir: Path = typer.Option(
        ...,
        "-i",
        "--input",
        help="Directory containing Kraken2 report files.",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output directory (default: parent of input).",
    ),
    keep_human: bool = typer.Option(
        False,
        "--keep-human",
        help="Do not filter human-related taxa (default: filtered).",
    ),
    viruses: bool = typer.Option(
        False,
        "--viruses",
        help="Extract only Viruses domain taxa.",
    ),
    bacteria: bool = typer.Option(
        False,
        "--bacteria",
        help="Extract only Bacteria domain taxa.",
    ),
    fungi: bool = typer.Option(
        False,
        "--fungi",
        help="Extract only Fungi kingdom taxa.",
    ),
    archaea: bool = typer.Option(
        False,
        "--archaea",
        help="Extract only Archaea domain taxa.",
    ),
    depth: int = typer.Option(
        1000,
        "-d",
        "--depth",
        help="Rarefaction depth for β-diversity.",
    ),
    seed: Optional[int] = typer.Option(
        None,
        "-s",
        "--seed",
        help="Random seed for reproducible rarefaction (default: random).",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite the output directory if it already exists.",
    ),
) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        run_pipeline(
            input_dir=input_dir,
            output_dir=output_dir,
            keep_human=keep_human,
            viruses_only=viruses,
            bacteria_only=bacteria,
            fungi_only=fungi,
            archaea_only=archaea,
            rarefaction_depth=depth,
            seed=seed,
            overwrite=overwrite,
        )
    except (FileNotFoundError, FileExistsError) as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
