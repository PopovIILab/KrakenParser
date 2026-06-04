#!/usr/bin/env python3
"""Decomposition utility to partition master MPA matrices into rank-specific text tables.

This module splits combined multi-sample MetaPhlAn files into separate tables grouped
by taxonomic rank (species, genus, family, etc.). It supports on-the-fly filtering
for specific biological domains (e.g., Viruses, Bacteria) and filters out host
contamination profiles using predefined taxonomic blacklists.
"""

import logging
import re
import sys
from pathlib import Path
from typing import Optional

import typer

from krakenparser.utils import ensure_output_dir

# Initialize module-level isolated logger
_log: logging.Logger = logging.getLogger(__name__)

# Dedicated Typer routing application instantiation
app: typer.Typer = typer.Typer(
    name="split",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Immutable configuration schema mapping ranks, targets, and descendents to drop
_RANKS: list[tuple[str, str, list[str]]] = [
    ("species", "s__", []),
    ("genus", "g__", ["s__"]),
    ("family", "f__", ["s__", "g__"]),
    ("order", "o__", ["s__", "g__", "f__"]),
    ("class", "c__", ["s__", "g__", "f__", "o__"]),
    ("phylum", "p__", ["s__", "g__", "f__", "o__", "c__"]),
]

# Host/human filtering target taxonomy markers
_HUMAN_MARKERS: frozenset[str] = frozenset(
    [
        "s__Homo_sapiens",
        "g__Homo",
        "f__Hominidae",
        "o__Primates",
        "c__Mammalia",
        "p__Chordata",
    ]
)

# Regular expression matching SRA/ENA run technical accession sub-strings
_ACCESSION_RE: re.Pattern[str] = re.compile(
    r"(SRS|SRR|SRX|ERS|ERR|ERX|DRS|DRR|DRX)\d*-"
)


def _strip_path_prefix(line: str) -> str:
    """Isolate the terminal taxonomic clade and purge short-read archive prefixes.

    Extracts the right-most node classification component from pipe-separated
    lineage string paths and trims technical sequencing metadata tags.

    Args:
        line: Raw tab-separated line from an MPA summary matrix.

    Returns:
        str: Cleansed and isolated clade metric description row.
    """
    tab: int = line.find("\t")
    if tab == -1:
        return line
    path, rest = line[:tab], line[tab:]
    pipe: int = path.rfind("|")
    segment: str = path[pipe + 1 :] if pipe != -1 else path
    return _ACCESSION_RE.sub("", segment + rest)


def _human_in_line(line: str) -> bool:
    """Verify if the taxonomic lineage contains human contamination markers.

    Args:
        line: Raw text line containing structural pipe-separated classifications.

    Returns:
        bool: True if the lineage intersects with monitored human host constraints.
    """
    tab: int = line.find("\t")
    path: str = line[:tab] if tab != -1 else line
    segments: set[str] = set(path.split("|"))
    return bool(segments & _HUMAN_MARKERS)


def split_mpa(
    input_file: Path,
    output_dir: Path,
    viruses_only: bool = False,
    bacteria_only: bool = False,
    fungi_only: bool = False,
    archaea_only: bool = False,
    keep_human: bool = False,
) -> None:
    """Deconstruct an MPA layout spreadsheet into separate single-rank count matrices.

    Applies selective biological domain filters, drops non-target sub-clades,
    performs host background depletion checks, and exports isolated text matrices
    under an independent 'txt' directory layout structure.

    Args:
        input_file: Validated Path to the incoming source master MPA file.
        output_dir: Path locating the destination output root workspace directory.
        viruses_only: If True, blocks all entries missing 'd__Viruses' tokens.
        bacteria_only: If True, blocks all entries missing 'd__Bacteria' tokens.
        fungi_only: If True, blocks all entries missing 'k__Fungi' tokens.
        archaea_only: If True, blocks all entries missing 'd__Archaea' tokens.
        keep_human: If True, skips host background depletion steps.

    Raises:
        FileNotFoundError: Triggered if the targeted raw matrix file cannot be loaded.
    """
    if not input_file.is_file():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    out_path: Path = ensure_output_dir(output_dir, is_file=False)
    (out_path / "txt").mkdir(exist_ok=True)

    # High-performance streaming line extractor skipping comments and layout whitespace
    with open(input_file, "r", encoding="utf-8") as fh:
        all_lines: list[str] = [
            ln for line in fh if (ln := line.strip()) and not ln.startswith("#")
        ]

    data_lines: list[str] = all_lines.copy()
    if viruses_only:
        data_lines = [ln for ln in data_lines if "d__Viruses" in ln]
    if bacteria_only:
        data_lines = [ln for ln in data_lines if "d__Bacteria" in ln]
    if fungi_only:
        data_lines = [ln for ln in data_lines if "k__Fungi" in ln]
    if archaea_only:
        data_lines = [ln for ln in data_lines if "d__Archaea" in ln]

    # Re-integrate target host sequences if preservation flags are set
    if keep_human:
        human_lines: list[str] = [ln for ln in all_lines if _human_in_line(ln)]
        data_lines = list(dict.fromkeys(data_lines + human_lines))

    # Iteratively evaluate taxons and construct independent files
    for rank_name, rank_prefix, exclude_prefixes in _RANKS:
        result: list[str] = []

        for line in data_lines:
            if rank_prefix not in line:
                continue
            if "t__" in line:  # Skip raw strain-level markers
                continue
            if any(ep in line for ep in exclude_prefixes):
                continue
            if not keep_human and _human_in_line(line):
                continue
            result.append(_strip_path_prefix(line))

        out_file: Path = out_path / "txt" / f"counts_{rank_name}.txt"

        # Python 3.10 validation: isolate conditional trailing slashes from f-strings
        trailing_newline: str = "\n" if result else ""
        out_file.write_text("\n".join(result) + trailing_newline, encoding="utf-8")

    _log.info("MPA file split successfully. Output stored in %s", output_dir)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    input_file: Optional[Path] = typer.Option(
        None,
        "-i",
        "--input",
        help="Input combined MPA file.",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output directory root pathway.",
    ),
    viruses_only: bool = typer.Option(
        False,
        "--viruses",
        help="Extract only VIRUSES domain taxa.",
    ),
    bacteria_only: bool = typer.Option(
        False,
        "--bacteria",
        help="Extract only BACTERIA domain taxa.",
    ),
    fungi_only: bool = typer.Option(
        False,
        "--fungi",
        help="Extract only FUNGI kingdom taxa.",
    ),
    archaea_only: bool = typer.Option(
        False,
        "--archaea",
        help="Extract only ARCHAEA domain taxa.",
    ),
    keep_human: bool = typer.Option(
        False,
        "--keep-human",
        help="Retain human-related taxa (default: filtered out).",
    ),
) -> None:
    """Split a combined MPA table into per-rank TXT files."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if input_file is None and output_dir is None:
        print(ctx.get_help())
        raise typer.Exit()

    if not input_file or not output_dir:
        print(
            "Error: Missing required options '-i / --input' and '-o / --output'.",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)

    try:
        split_mpa(
            input_file,
            output_dir,
            viruses_only=viruses_only,
            bacteria_only=bacteria_only,
            fungi_only=fungi_only,
            archaea_only=archaea_only,
            keep_human=keep_human,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
