#!/usr/bin/env python

import os
import sys
import tempfile
import argparse
from pathlib import Path


def modify_taxa_names(line):
    prefixes = ["s__", "g__", "f__", "o__", "c__", "p__"]
    for prefix in prefixes:
        if line.startswith(prefix):
            parts = line[len(prefix):].split("\t")
            parts[0] = parts[0].replace("_", " ")
            return "\t".join(parts)
    return line


def process_files(source_file, destination_file):
    src_path = Path(source_file)
    if not src_path.is_file():
        raise FileNotFoundError(f"Source file not found: {src_path}")
    dest_path = Path(destination_file)
    if not dest_path.is_file():
        raise FileNotFoundError(f"Destination file not found: {dest_path}")

    # Read the first line from the source file and modify it
    with open(src_path, "r") as file:
        first_line_source = file.readline()
    modified_first_line = "\t".join(
        word.split(".")[0] for word in first_line_source.split()
    )

    # Read all content from the destination file and modify taxa names
    with open(dest_path, "r") as file:
        lines = file.readlines()
    modified_lines = [modify_taxa_names(line.strip()) for line in lines]

    # Combine the modified first line with the modified content of the destination file
    updated_content = modified_first_line + "\n" + "\n".join(modified_lines)

    # Write atomically: write to a temp file in the same directory, then replace
    with tempfile.NamedTemporaryFile(
        mode="w", dir=dest_path.parent, delete=False, suffix=".tmp"
    ) as tmp:
        tmp.write(updated_content)
        tmp_path = tmp.name
    os.replace(tmp_path, dest_path)

    print(f"Processed {destination_file} successfully.")


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
