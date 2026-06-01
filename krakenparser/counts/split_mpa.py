#!/usr/bin/env python
"""Split a combined MPA table into per-rank TXT files.

Replaces decombine.sh and decombine_viruses.sh.
"""

import logging
import re
import sys
from pathlib import Path
from typing import Optional

import typer

from krakenparser.utils import ensure_output_dir

_log = logging.getLogger(__name__)

app = typer.Typer(
    name="split",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

_RANKS = [
    ("species", "s__", []),
    ("genus", "g__", ["s__"]),
    ("family", "f__", ["s__", "g__"]),
    ("order", "o__", ["s__", "g__", "f__"]),
    ("class", "c__", ["s__", "g__", "f__", "o__"]),
    ("phylum", "p__", ["s__", "g__", "f__", "o__", "c__"]),
]

_HUMAN_MARKERS = frozenset(
    [
        "s__Homo_sapiens",
        "g__Homo",
        "f__Hominidae",
        "o__Primates",
        "c__Mammalia",
        "p__Chordata",
    ]
)

_ACCESSION_RE = re.compile(r"(SRS|SRR|SRX|ERS|ERR|ERX|DRS|DRR|DRX)\d*-")


def _strip_path_prefix(line: str) -> str:
    tab = line.find("\t")
    if tab == -1:
        return line
    path, rest = line[:tab], line[tab:]
    pipe = path.rfind("|")
    segment = path[pipe + 1 :] if pipe != -1 else path
    return _ACCESSION_RE.sub("", segment + rest)


def _human_in_line(line: str) -> bool:
    tab = line.find("\t")
    path = line[:tab] if tab != -1 else line
    segments = set(path.split("|"))
    return bool(segments & _HUMAN_MARKERS)


def split_mpa(
    input_file: str,
    output_dir: str,
    viruses_only: bool = False,
    bacteria_only: bool = False,
    fungi_only: bool = False,
    archaea_only: bool = False,
    keep_human: bool = False,
) -> None:
    in_path = Path(input_file)
    if not in_path.is_file():
        raise FileNotFoundError(f"Input file not found: {in_path}")
    out_path = ensure_output_dir(output_dir, is_file=False)
    (out_path / "txt").mkdir(exist_ok=True)

    all_lines = [
        ln
        for ln in in_path.read_text().splitlines()
        if not ln.startswith("#") and ln.strip()
    ]

    data_lines = all_lines.copy()
    if viruses_only:
        data_lines = [ln for ln in data_lines if "d__Viruses" in ln]
    if bacteria_only:
        data_lines = [ln for ln in data_lines if "d__Bacteria" in ln]
    if fungi_only:
        data_lines = [ln for ln in data_lines if "k__Fungi" in ln]
    if archaea_only:
        data_lines = [ln for ln in data_lines if "d__Archaea" in ln]

    if keep_human:
        human_lines = [ln for ln in all_lines if _human_in_line(ln)]
        data_lines = list(dict.fromkeys(data_lines + human_lines))

    for rank_name, rank_prefix, exclude_prefixes in _RANKS:
        result = []

        for line in data_lines:
            if rank_prefix not in line:
                continue
            if "t__" in line:
                continue
            if any(ep in line for ep in exclude_prefixes):
                continue
            if not keep_human and _human_in_line(line):
                continue
            result.append(_strip_path_prefix(line))

        out_file = out_path / "txt" / f"counts_{rank_name}.txt"
        out_file.write_text("\n".join(result) + ("\n" if result else ""))

    _log.info("MPA file split successfully. Output stored in %s", output_dir)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    input_file: Optional[str] = typer.Option(
        None,
        "-i",
        "--input",
        help="Input combined MPA file.",
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output directory.",
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
