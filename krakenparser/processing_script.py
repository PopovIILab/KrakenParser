#!/usr/bin/env python

import sys
import shutil
import argparse
from pathlib import Path


def modify_taxa_names(line):
    prefixes = ["s__", "g__", "f__", "o__", "c__", "p__"]
    for prefix in prefixes:
        if line.startswith(prefix):
            # Remove the prefix and replace underscores with spaces
            return line[len(prefix) :].replace("_", " ")
    return line


def process_files(source_file, destination_file):
    # Read the first line from the source file and modify it
    with open(source_file, "r") as file:
        first_line_source = file.readline()
    modified_first_line = "\t".join(
        word.split(".")[0] for word in first_line_source.split()
    )

    # Read all content from the destination file and modify taxa names
    with open(destination_file, "r") as file:
        lines = file.readlines()
    modified_lines = [modify_taxa_names(line.strip()) for line in lines]

    # Combine the modified first line with the modified content of the destination file
    updated_content = modified_first_line + "\n" + "\n".join(modified_lines)

    # Write the updated content back to the destination file
    with open(destination_file, "w") as file:
        file.write(updated_content)

    print(f"Processed {destination_file} successfully.")

    # Get the path to the current directory (same location as the script)
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"

    # Check if __pycache__ exists and remove it
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)


if __name__ == "__main__":
    # Use argparse to parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Reads a source file, processes its first line, modifies taxa names in a destination file, and updates it."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to the source file. This file's first line will be read and modified.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to the destination file. This file's contents will be updated with cleaned taxa names.",
    )

    args = parser.parse_args()

    # Call the function with parsed arguments
    process_files(args.input, args.output)
