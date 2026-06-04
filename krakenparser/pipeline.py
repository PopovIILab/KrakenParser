#!/usr/bin/env python3
"""Core orchestration engine for the KrakenParser execution pipeline.

This module consolidates independent taxonomic processing steps into a seamless,
end-to-end automated pipeline. It handles file validation, directory structure
sanitization, data transformations, statistical scaling, and diversity indexing.
"""

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

# Initialize module-level isolated logger
_log: logging.Logger = logging.getLogger(__name__)

# Primary pipeline subcommand routing sub-app
app: typer.Typer = typer.Typer(
    name="run",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Structural database directory map enforced by the pipeline architecture
_OUTPUT_SUBDIRS: tuple[str, ...] = ("intermediate", "counts", "rel_abund", "diversity")


def _is_processable(filepath: Path) -> bool:
    """Validate file integrity prior to feeding it to text-parsing utilities.

    Ensures the target file is not a hidden system artifact, does not contain
    binary null-byte contamination, and safely decodes via UTF-8 standard.

    Args:
        path: A Path object referencing the target text file.

    Returns:
        bool: True if the file matches structural sanity baselines, False otherwise.
    """
    if filepath.name.startswith("."):
        return False

    try:
        if b"\x00" in filepath.read_bytes():
            return False
    except Exception:
        return False

    # 3. СТРОГАЯ проверка на UTF-8 (вот здесь косяк)
    try:
        # Добавляем errors="strict", чтобы не глотать BOM и левые кодировки
        with open(filepath, "r", encoding="utf-8", errors="strict") as f:
            # Читаем небольшой кусок файла для проверки
            f.read(1024)
        return True
    except UnicodeDecodeError:
        return False
    except Exception:
        return False


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
    """Execute the sequential programmatic workflow blocks of KrakenParser.

    Validates resources, purges legacy directories under explicit overwrite rules,
    converts raw reports to structured matrices, strips structural taxonomic strings,
    scales measurements, and exports ecological diversity indices.

    Args:
        input_dir: Path pointing to the source directory containing raw reports.
        output_dir: Custom export destination path. Defaults to input_dir parent if None.
        keep_human: If True, biological filtering blocks skipping human contamination are disabled.
        viruses_only: Restricts the processing scope exclusively to the Viruses domain.
        bacteria_only: Restricts the processing scope exclusively to the Bacteria domain.
        fungi_only: Restricts the processing scope exclusively to the Fungi kingdom.
        archaea_only: Restricts the processing scope exclusively to the Archaea domain.
        rarefaction_depth: Absolute uniform read metrics applied during beta-dissimilarity calculation.
        seed: Random state state-initializer utilized to force deterministic rarefaction.
        overwrite: Overrides local path locks, destroying conflicting outputs matching pipeline subdirs.

    Raises:
        FileNotFoundError: Triggered if the declared input resource directory is absent.
        FileExistsError: Safety exception raised if targeted locations hold pre-existing outputs
            and overwrite locks are set to active.
        typer.Exit: Gracefully intercepts runtime aborts if critical files disappear mid-run.
    """
    source_dir: Path = input_dir
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {source_dir}")

    out_dir: Path = output_dir if output_dir else source_dir.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Protect pre-existing data matrices from unintended deletion mutations
    existing: list[Path] = [
        out_dir / d for d in _OUTPUT_SUBDIRS if (out_dir / d).exists()
    ]
    if existing and not overwrite:
        names: str = ", ".join(d.name for d in existing)
        raise FileExistsError(
            f"Output already exists in '{out_dir}' ({names}).\n"
            "Use --overwrite to overwrite it."
        )
    if overwrite:
        for d in existing:
            shutil.rmtree(d)
            _log.info("Removed existing directory: %s", d)

    # Step 1: Initialize structural staging environment layers
    intermediate_dir: Path = out_dir / "intermediate"
    intermediate_dir.mkdir(exist_ok=True)

    mpa_dir: Path = intermediate_dir / "mpa"
    mpa_dir.mkdir(exist_ok=True)

    # Step 2: Compile independent text reports to unified MetaPhlAn format
    for f in sorted(source_dir.iterdir()):
        if not f.is_file():
            continue
        if not _is_processable(f):
            _log.info("Skipping: %s", f.name)
            continue
        out_name: str = f.stem + ".MPA.TXT"
        kreport_to_mpa(f, mpa_dir / out_name, display_header=True)

    mpa_files: list[Path] = sorted(mpa_dir.glob("*.MPA.TXT"))
    if not mpa_files:
        print("Error: no MPA files found after conversion.", file=sys.stderr)
        raise typer.Exit(code=1)

    # Step 3: Matrix aggregation across multiple samples
    combined_file: Path = intermediate_dir / "COMBINED.txt"
    combine_mpa(mpa_files, combined_file)
    _log.info("MPA files combined. Output: %s", combined_file)

    # Step 4: Isolate targeted biological taxonomic strata and domains
    split_mpa(
        combined_file,
        intermediate_dir,
        keep_human=keep_human,
        viruses_only=viruses_only,
        bacteria_only=bacteria_only,
        fungi_only=fungi_only,
        archaea_only=archaea_only,
    )
    txt_dir: Path = intermediate_dir / "txt"

    # Step 5: Clean prefix tags and syntactic formatting anomalies
    for txt_file in sorted(txt_dir.glob("counts_*.txt")):
        process_files(combined_file, txt_file)

    # Step 6: Construct tidy row/column layout structures within CSV tables
    counts_dir: Path = out_dir / "counts"
    counts_dir.mkdir(exist_ok=True)
    for txt_file in sorted(txt_dir.glob("counts_*.txt")):
        csv_file: Path = counts_dir / txt_file.with_suffix(".csv").name
        convert_to_csv(txt_file, csv_file)

    # Step 7: Apply normalization metrics to convert counts to relative distribution percentages
    rel_abund_dir: Path = out_dir / "rel_abund"
    rel_abund_dir.mkdir(exist_ok=True)
    for csv_file in sorted(counts_dir.glob("counts_*.csv")):
        ra_file: Path = rel_abund_dir / csv_file.name.replace("counts_", "ra_")
        calculate_rel_abund(csv_file, ra_file)

    # Step 8: Parse ecological matrices to capture microbial diversity indices
    species_csv: Path = counts_dir / "counts_species.csv"
    if not species_csv.exists():
        print(f"Error: species counts not found: {species_csv}", file=sys.stderr)
        raise typer.Exit(code=1)

    diversity_dir: Path = out_dir / "diversity"
    diversity_dir.mkdir(exist_ok=True)

    df: pd.DataFrame = pd.read_csv(species_csv, index_col=0)
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
    """CLI exposure wrapper for the unified run_pipeline automated execution loop.

    Args:
        input_dir: Dynamic input target. Passed directly via options.
        output_dir: Custom export destination route.
        keep_human: Host containment configuration option.
        viruses: Viral isolation target selector.
        bacteria: Bacterial isolation target selector.
        fungi: Mycological isolation target selector.
        archaea: Archaeal isolation target selector.
        depth: Uniform sequence metric baseline threshold.
        seed: Execution randomization initialization state.
        overwrite: Overrides data locks protecting directories.

    Raises:
        typer.Exit: Aborts execution with a system error code 1 when intercepts system faults.
    """
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
