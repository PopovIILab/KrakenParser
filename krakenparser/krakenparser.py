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


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    package_dir = Path(__file__).resolve().parent

    # Map of advanced steps for granular pipeline execution control
    step_map = {
        "mpa": (package_dir / "mpa" / "transform2mpa.py", []),
        "combine": (package_dir / "mpa" / "mpa_table.py", []),
        "split": (package_dir / "counts" / "split_mpa.py", []),
        "process": (package_dir / "counts" / "processing_script.py", []),
        "csv": (package_dir / "counts" / "convert2csv.py", []),
        "relabund": (package_dir / "stats" / "relabund.py", []),
        "diversity": (package_dir / "stats" / "diversity.py", []),
    }

    def _build_cmd(
        script: Path, base_args: list[str], user_args: list[str]
    ) -> list[str]:
        if script.suffix == ".py":
            # Execute as module to preserve relative imports within the package
            module = ".".join(
                script.relative_to(package_dir.parent).with_suffix("").parts
            )
            return [sys.executable, "-m", module] + base_args + user_args
        return [str(script)] + base_args + user_args

    # -------------------------------------------------------------------------
    # 1. Intercept --step execution for sub-module isolation
    # -------------------------------------------------------------------------
    if "--step" in sys.argv:
        step_idx = sys.argv.index("--step")
        if step_idx + 1 < len(sys.argv):
            step = sys.argv[step_idx + 1]
            if step in step_map:
                script, base_args = step_map[step]
                passed_args = sys.argv[1:]
                passed_args.remove("--step")
                passed_args.remove(step)

                cmd = _build_cmd(script, base_args, passed_args)
                sys.exit(subprocess.run(cmd).returncode)

    # -------------------------------------------------------------------------
    # 2. Main Argument Parser Definition
    # -------------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="KrakenParser: Convert Kraken2 Reports to CSV.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    core_group = parser.add_argument_group("Core Arguments")
    core_group.add_argument(
        "-i", "--input", help="Directory containing Kraken2 report files"
    )
    core_group.add_argument(
        "-o", "--output", help="Output directory (default: parent of input)"
    )
    core_group.add_argument(
        "--viruses",
        action="store_true",
        help="Extract only VIRUSES domain taxa in the pipeline",
    )
    core_group.add_argument(
        "--keep-human", action="store_true", help="Do not filter human-related taxa"
    )
    core_group.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    pipe_group = parser.add_argument_group("Pipeline Options (Full Run)")
    pipe_group.add_argument(
        "-d",
        "--depth",
        type=int,
        default=1000,
        help="Rarefaction depth for β-diversity (default: 1000)",
    )
    pipe_group.add_argument(
        "-s",
        "--seed",
        type=int,
        help="Random seed for reproducible rarefaction (default: random)",
    )
    pipe_group.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the output directory if it already exists",
    )

    adv_group = parser.add_argument_group("Advanced (Step-by-step control)")
    adv_group.add_argument(
        "--step",
        choices=list(step_map.keys()),
        help="Run only a specific part of the pipeline.\nType 'krakenparser --step <name> -h' for more.",
    )

    # Suppressed routing flags for strict backwards compatibility
    legacy_flags = [
        "--complete",
        "--kreport2mpa",
        "--combine_mpa",
        "--deconstruct",
        "--deconstruct_viruses",
        "--process",
        "--txt2csv",
        "--relabund",
        "--diversity",
    ]
    for flag in legacy_flags:
        parser.add_argument(flag, action="store_true", help=argparse.SUPPRESS)

    # -------------------------------------------------------------------------
    # 3. Routing Logic and Validation
    # -------------------------------------------------------------------------
    for _a in sys.argv:
        if "\x00" in _a:
            sys.exit("Error: argument contains invalid null byte.")

    args, unknown_args = parser.parse_known_args()

    legacy_map = {
        "complete": (package_dir / "pipeline.py", []),
        "kreport2mpa": step_map["mpa"],
        "combine_mpa": step_map["combine"],
        "deconstruct": step_map["split"],
        "deconstruct_viruses": (
            package_dir / "counts" / "split_mpa.py",
            ["--viruses-only"],
        ),
        "process": step_map["process"],
        "txt2csv": step_map["csv"],
        "relabund": step_map["relabund"],
        "diversity": step_map["diversity"],
    }

    passed_legacy_args = [
        arg
        for arg in sys.argv[1:]
        if not arg.startswith("--") or arg.lstrip("--") not in legacy_map
    ]

    for flag, (script, base_args) in legacy_map.items():
        if getattr(args, flag, False):
            cmd = _build_cmd(script, base_args, passed_legacy_args)
            sys.exit(subprocess.run(cmd).returncode)

    # Standard entry point: trigger pipeline execution if input directory is provided
    if args.input:
        script = package_dir / "pipeline.py"
        cmd = _build_cmd(script, [], sys.argv[1:])

        in_path = Path(args.input)
        out_path = Path(args.output) if args.output else in_path.parent
        out_path.mkdir(parents=True, exist_ok=True)
        log_file_path = out_path / "krakenparser.log"

        with open(log_file_path, "w") as log_file:
            result = subprocess.run(cmd, stdout=log_file, stderr=subprocess.STDOUT)

        if result.returncode == 0:
            print("All steps completed successfully!")
            print(f"Logs saved to {log_file_path}")

            has_depth = any(arg in sys.argv for arg in ["-d", "--depth"])
            has_seed = any(arg in sys.argv for arg in ["-s", "--seed"])

            out_str = out_path.as_posix()

            print("\n" + "=" * 95)

            if not has_depth and not has_seed:
                print(
                    f"""
[INFO] Pipeline completed using default rarefaction parameters (depth=1000, seed=random).
       To calibrate beta-diversity sensitivity metrics for this specific dataset,
       manually execute the diversity sub-module with custom thresholds.
       Example:
       krakenparser --step diversity \\
       -i {out_str}/counts/counts_species.csv \\
       -o {out_str}/diversity \\
       --depth 1500 \\
       --seed 42
       """.rstrip()
                )

            print(
                f"""
[TIP] Downstream Data Visualization Prerequisite:
      Relative abundance normalization is required to group low-abundance taxa
      using the -O / --other <float> parameter. Without filtering the 'long tail'
      of rare taxa, the resulting visualization will suffer from overplotting
      and significant loss of interpretability.
      Example:
      krakenparser --step relabund \\
      -i {out_str}/counts/counts_species.csv \\
      -o {out_str}/rel_abund/counts_species_relabund_3_5.csv \\
      -O 3.5

{"=" * 95}
            """.rstrip()
            )
        else:
            print(f"Pipeline failed. Check logs at {log_file_path}")

        sys.exit(result.returncode)

    # Fallback to usage overview if no actionable arguments were provided
    print("KrakenParser by Ilia V. Popov")
    parser.print_help()


if __name__ == "__main__":
    main()
