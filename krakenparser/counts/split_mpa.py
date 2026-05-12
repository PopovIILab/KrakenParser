#!/usr/bin/env python
"""Split a combined MPA table into per-rank TXT files.

Replaces decombine.sh and decombine_viruses.sh.
"""

import argparse
import logging
import re
import sys
from pathlib import Path

_log = logging.getLogger(__name__)


_RANKS = [
    ("species", "s__", []),
    ("genus",   "g__", ["s__"]),
    ("family",  "f__", ["s__", "g__"]),
    ("order",   "o__", ["s__", "g__", "f__"]),
    ("class",   "c__", ["s__", "g__", "f__", "o__"]),
    ("phylum",  "p__", ["s__", "g__", "f__", "o__", "c__"]),
]

_HUMAN_TAXA = {
    "species": "s__Homo_sapiens",
    "genus":   "g__Homo",
    "family":  "f__Hominidae",
    "order":   "o__Primates",
    "class":   "c__Mammalia",
    "phylum":  "p__Chordata",
}

_ACCESSION_RE = re.compile(r"(SRS|SRR|SRX|ERS|ERR|ERX|DRS|DRR|DRX)\d*-")


def _strip_path_prefix(line: str) -> str:
    """'d__X|p__Y|s__Z\t10\t20' → 's__Z\t10\t20'"""
    tab = line.find("\t")
    if tab == -1:
        return line
    path, rest = line[:tab], line[tab:]
    pipe = path.rfind("|")
    segment = path[pipe + 1:] if pipe != -1 else path
    return _ACCESSION_RE.sub("", segment + rest)


def split_mpa(
    input_file: str,
    output_dir: str,
    viruses_only: bool = False,
    keep_human: bool = False,
) -> None:
    in_path = Path(input_file)
    if not in_path.is_file():
        raise FileNotFoundError(f"Input file not found: {in_path}")
    out_path = Path(output_dir)
    (out_path / "txt").mkdir(parents=True, exist_ok=True)

    lines = in_path.read_text().splitlines()
    data_lines = [ln for ln in lines if not ln.startswith("#") and ln.strip()]

    if viruses_only:
        data_lines = [ln for ln in data_lines if "d__Viruses" in ln]

    filter_human = not keep_human and not viruses_only

    for rank_name, rank_prefix, exclude_prefixes in _RANKS:
        result = []
        human_pattern = _HUMAN_TAXA[rank_name]

        for line in data_lines:
            if rank_prefix not in line:
                continue
            if "t__" in line:
                continue
            if any(ep in line for ep in exclude_prefixes):
                continue
            if filter_human and human_pattern in line:
                continue
            result.append(_strip_path_prefix(line))

        out_file = out_path / "txt" / f"counts_{rank_name}.txt"
        out_file.write_text("\n".join(result) + ("\n" if result else ""))

    _log.info("MPA file split successfully. Output stored in %s", output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split a combined MPA table into per-rank TXT files."
    )
    parser.add_argument("-i", "--input", required=True, help="Input combined MPA file")
    parser.add_argument("-o", "--output", required=True, help="Output directory")
    parser.add_argument(
        "--viruses-only",
        action="store_true",
        default=False,
        help="Extract only Viruses domain taxa",
    )
    parser.add_argument(
        "--keep-human",
        action="store_true",
        default=False,
        help="Do not filter human-related taxa (default: filtered)",
    )
    args = parser.parse_args()
    split_mpa(args.input, args.output, viruses_only=args.viruses_only, keep_human=args.keep_human)


if __name__ == "__main__":
    main()
