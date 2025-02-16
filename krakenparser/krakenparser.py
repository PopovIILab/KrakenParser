import argparse
import subprocess
import shutil
from pathlib import Path
from .version import __version__

# Main function to run the tool
def main():
    print("KrakenParser by Ilia V. Popov")
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="KrakenParser: Convert Kraken2 Reports to CSV."
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
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args, extra_args = parser.parse_known_args()

    package_dir = Path(__file__).resolve().parent  # Directory of the current script

    # Map flags to corresponding scripts
    command_map = {
        "kreport2mpa": package_dir/"run_kreport2mpa.sh",
        "combine_mpa": package_dir/"combine_mpa.py",
        "deconstruct": package_dir/"decombine.sh",
        "process": package_dir/"processing_script.py",
        "txt2csv": package_dir/"convert2csv.py",
    }

    # Find which argument was given and run the corresponding script
    for arg, script in command_map.items():
        if getattr(args, arg):
            subprocess.run([script] + extra_args, check=True)  # Pass extra arguments to the script
            return

    subprocess.run([package_dir/"kraken2csv.sh"] + extra_args, check=True)


    # Get the path to the current directory (same location as the script)
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"

    # Check if __pycache__ exists and remove it
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)


if __name__ == "__main__":
    main()
