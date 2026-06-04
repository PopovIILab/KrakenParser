#!/usr/bin/env python3
"""Main command-line interface entry point for KrakenParser.

This module orchestrates the entire KrakenParser suite, exposing an end-to-end
automated pipeline alongside granular subcommands for step-by-step control
over metagenomic report parsing, normalization, and statistical analysis.
"""

import logging
import sys
from importlib.metadata import PackageNotFoundError as _PNF
from importlib.metadata import version as _pkg_version
from pathlib import Path
from typing import Optional

import typer

from krakenparser.counts.convert2csv import app as csv_app
from krakenparser.counts.processing_script import app as process_app
from krakenparser.counts.split_mpa import app as split_app
from krakenparser.mpa.mpa_table import app as combine_app
from krakenparser.mpa.transform2mpa import app as mpa_app
from krakenparser.pipeline import run_pipeline
from krakenparser.stats.diversity import app as diversity_app
from krakenparser.stats.relabund import app as relabund_app

# Fetch package version dynamically from metadata or fall back to unknown
try:
    __version__: str = _pkg_version("krakenparser")
except _PNF:
    __version__ = "unknown"

# Initialize primary Typer interface with global configuration
app: typer.Typer = typer.Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

PANEL_NAME: str = "Advanced (Step-by-step pipeline control)"

# Register individual step subcommands under a isolated help panel
app.add_typer(mpa_app, name="mpa", rich_help_panel=PANEL_NAME)
app.add_typer(combine_app, name="combine", rich_help_panel=PANEL_NAME)
app.add_typer(split_app, name="split", rich_help_panel=PANEL_NAME)
app.add_typer(process_app, name="process", rich_help_panel=PANEL_NAME)
app.add_typer(csv_app, name="csv", rich_help_panel=PANEL_NAME)
app.add_typer(relabund_app, name="relabund", rich_help_panel=PANEL_NAME)
app.add_typer(diversity_app, name="diversity", rich_help_panel=PANEL_NAME)


def _version_callback(value: bool) -> None:
    """Eager callback executing the version flag logic.

    Args:
        value: Boolean trigger provided by the Typer parameter evaluation.

    Raises:
        typer.Exit: Gracefully terminates the runtime execution upon displaying version.
    """
    if value:
        print(f"KrakenParser {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    input_dir: Optional[Path] = typer.Option(
        None, "-i", "--input", help="Directory containing Kraken2 report files."
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "-o", "--output", help="Output directory."
    ),
    viruses: bool = typer.Option(
        False,
        "-viruses",
        "--viruses",
        help="Extract only VIRUSES domain taxa in the pipeline.",
    ),
    bacteria: bool = typer.Option(
        False,
        "-bacteria",
        "--bacteria",
        help="Extract only BACTERIA domain taxa in the pipeline.",
    ),
    fungi: bool = typer.Option(
        False,
        "-fungi",
        "--fungi",
        help="Extract only FUNGI kingdom taxa in the pipeline.",
    ),
    archaea: bool = typer.Option(
        False,
        "-archaea",
        "--archaea",
        help="Extract only ARCHAEA domain taxa in the pipeline.",
    ),
    keep_human: bool = typer.Option(
        False, "-keep-human", "--keep-human", help="Do not filter human-related taxa."
    ),
    version: Optional[bool] = typer.Option(
        None,
        "-V",
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    depth: int = typer.Option(
        1000, "-d", "--depth", help="Rarefaction depth for β-diversity."
    ),
    seed: Optional[int] = typer.Option(
        None, "-s", "--seed", help="Random seed for reproducible rarefaction."
    ),
    overwrite: bool = typer.Option(
        False,
        "-overwrite",
        "--overwrite",
        help="Overwrite the output directory if it already exists.",
    ),
) -> None:
    """
    KrakenParser: Convert Kraken2 Reports to CSV and analyze microbial diversity.

    To execute the full pipeline automatically, just use the global options.

    Alternatively, you can run specific parts of the pipeline manually in the following order:

    mpa ➔ combine ➔ split ➔ process ➔ csv ➔ relabund ➔ diversity

    Each step behaves as an independent tool. Type 'krakenparser <command> --help' to see options for a specific step.
    """
    # Prevent execution loop if the engine passes control down to registered subcommands
    if ctx.invoked_subcommand is not None:
        return

    # Execute monolithic end-to-end automation workflow if input targets are declared
    if input_dir:
        print("KrakenParser by Ilia V. Popov")

        out_path: Path = output_dir if output_dir else input_dir.parent
        out_path.mkdir(parents=True, exist_ok=True)
        log_file_path: Path = out_path / "krakenparser.log"

        # Dynamically attach logging engine dedicated to current run output context
        log_handler: logging.FileHandler = logging.FileHandler(log_file_path, mode="w")
        log_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.basicConfig(level=logging.INFO, handlers=[log_handler])

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

        print("All steps completed successfully!")
        print(f"Logs saved to {log_file_path}")

        out_str: str = out_path.as_posix()

        # Interrogate parameter sources to tailor downstream recommendations accurately
        has_custom_depth: bool = (
            str(ctx.get_parameter_source("depth")) != "ParameterSource.DEFAULT"
        )
        has_custom_seed: bool = (
            str(ctx.get_parameter_source("seed")) != "ParameterSource.DEFAULT"
        )

        print("\n" + "=" * 95)

        if not has_custom_depth and not has_custom_seed:
            print(
                f"""
[INFO] Pipeline completed using default rarefaction parameters (depth={depth}, seed=random).
       To calibrate beta-diversity sensitivity metrics for this specific dataset,
       manually execute the diversity sub-module with custom thresholds.
       Example:
       krakenparser diversity \\
       -i {out_str}/counts/counts_species.csv \\
       -o {out_str}/diversity \\
       --depth 1500 \\
       --seed 42""".rstrip()
            )

        print(
            f"""
[TIP] Downstream Data Visualization Prerequisite:
      Relative abundance normalization is required to group low-abundance taxa
      using the -O / --other <float> parameter. Without filtering the 'long tail'
      of rare taxa, the resulting visualization will suffer from overplotting
      and significant loss of interpretability.
      Example:
      krakenparser relabund \\
      -i {out_str}/counts/counts_species.csv \\
      -o {out_str}/rel_abund/counts_species_relabund_3_5.csv \\
      -O 3.5

{"=" * 95}""".rstrip()
        )

        raise typer.Exit()

    # Fallback default interaction pattern rendering global help usage diagnostics
    print("KrakenParser by Ilia V. Popov")
    print(ctx.get_help())


def entry_point() -> None:
    """Consolidated main system application executor wrapper.

    Handles external runtime events like manual cancellation securely to protect
    terminal trace sanity.
    """
    try:
        app()
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    entry_point()
