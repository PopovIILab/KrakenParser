import argparse
import logging
import subprocess
import sys
from importlib.metadata import PackageNotFoundError as _PNF
from importlib.metadata import version as _pkg_version
from pathlib import Path

try:
    __version__ = _pkg_version("krakenparser")
except _PNF:
    __version__ = "unknown"


# Main function to run the tool
def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print("KrakenParser by Ilia V. Popov")
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="KrakenParser: Convert Kraken2 Reports to CSV.",
        add_help=False,
    )
    parser.add_argument(
        "--complete",
        action="store_true",
        help="Run the full pipeline (also the default when -i is given)",
    )
    parser.add_argument(
        "--kreport2mpa",
        action="store_true",
        help="Convert Kraken2 Reports to MPA Format",
    )
    parser.add_argument(
        "--combine_mpa",
        action="store_true",
        help="Combine MPA Files",
    )
    parser.add_argument(
        "--deconstruct",
        action="store_true",
        help="Extract Taxonomic Levels from combined MPA file",
    )
    parser.add_argument(
        "--deconstruct_viruses",
        action="store_true",
        help="Extract Taxonomic Levels from combined MPA file using only VIRUSES domain",
    )
    parser.add_argument(
        "--process",
        action="store_true",
        help="Process Extracted Taxonomic Data",
    )
    parser.add_argument(
        "--txt2csv",
        action="store_true",
        help="Convert TXT to CSV",
    )
    parser.add_argument(
        "--relabund",
        action="store_true",
        help="Calculate relative abundance",
    )
    parser.add_argument(
        "--diversity",
        action="store_true",
        help="Calculate α & β-diversities",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args, extra_args = parser.parse_known_args()

    for _a in extra_args:
        if "\x00" in _a:
            sys.exit("Error: argument contains invalid null byte.")

    package_dir = Path(__file__).resolve().parent  # Directory of the current script

    # Map flags to (script_path, base_args_to_prepend)
    command_map = {
        "complete": (package_dir / "pipeline.py", []),
        "kreport2mpa": (package_dir / "mpa" / "transform2mpa.py", []),
        "combine_mpa": (package_dir / "mpa" / "mpa_table.py", []),
        "deconstruct": (package_dir / "counts" / "split_mpa.py", []),
        "deconstruct_viruses": (
            package_dir / "counts" / "split_mpa.py",
            ["--viruses-only"],
        ),
        "process": (package_dir / "counts" / "processing_script.py", []),
        "txt2csv": (package_dir / "counts" / "convert2csv.py", []),
        "relabund": (package_dir / "stats" / "relabund.py", []),
        "diversity": (package_dir / "stats" / "diversity.py", []),
    }

    if "-h" in sys.argv or "--help" in sys.argv:
        if not any(getattr(args, key) for key in command_map):
            parser.print_help()
            return

    def _build_cmd(
        script: Path, base_args: list[str], user_args: list[str]
    ) -> list[str]:
        if script.suffix == ".py":
            # Run as module (-m) so the krakenparser package stays importable.
            # Derive dotted module name from path relative to the package root.
            module = ".".join(
                script.relative_to(package_dir.parent).with_suffix("").parts
            )
            return [sys.executable, "-m", module] + base_args + user_args
        return [str(script)] + base_args + user_args

    # Find which argument was given and run the corresponding script
    for arg, (script, base_args) in command_map.items():
        if getattr(args, arg):
            subprocess.run(_build_cmd(script, base_args, extra_args), check=True)
            return

    # Default to full pipeline when -i/--input is given without a subcommand
    if "-i" in extra_args or "--input" in extra_args:
        complete_script, complete_base = command_map["complete"]
        subprocess.run(
            _build_cmd(complete_script, complete_base, extra_args), check=True
        )
        return

    parser.print_help()


if __name__ == "__main__":
    main()
