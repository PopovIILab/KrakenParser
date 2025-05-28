#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $(basename "$0") -i|--input PATH_TO_SOURCE"
    echo
    echo "  -i, --input   Path to the source directory — Kraken2 reports must be inside a subdirectory (e.g., data/kreports)"
    echo "  -h            Show this help message"
    exit 0
}

# Parse command-line arguments
SOURCE_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -i|--input) SOURCE_DIR="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

# Ensure SOURCE_DIR is set
if [ -z "$SOURCE_DIR" ]; then
    echo "Error: input is required."
    usage
fi

# Determine the directory of this script
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# PART 1: CONVERT KRAKEN2 TO MPA

# Setting the path to the source file directory and destination directory
PARENT_DIR=$(dirname "$SOURCE_DIR")
MPA_DIR="$PARENT_DIR/mpa"

# Run the old script with the correct paths
"$SCRIPT_DIR/run_kreport2mpa.sh" -i "$SOURCE_DIR" -o "$MPA_DIR"

# PART 2: COMBINING MPAs

COMBINED_FILE="$PARENT_DIR/COMBINED.txt"
python "$SCRIPT_DIR/combine_mpa.py" -i "$MPA_DIR"/* -o "$COMBINED_FILE"
if [ $? -ne 0 ]; then
    echo "Error: Failed to run combine_mpa.py"
    exit 1
fi
echo "MPA files combined successfully. Output stored in $COMBINED_FILE"

# PART 3: DECOMBINING MPAs

COUNTS_DIR="$PARENT_DIR/counts"

"$SCRIPT_DIR/decombine.sh" -i "$COMBINED_FILE" -o "$COUNTS_DIR"

# PART 4: PROCESS COUNTS TXT FILES

for file in "$COUNTS_DIR"/txt/counts_*.txt; do
    python "$SCRIPT_DIR/processing_script.py" -i "$COMBINED_FILE" -o "$file"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to process $file"
        exit 1
    fi
    echo "Processed $file successfully."
done

# PART 5: CONVERT TXT FILES TO CSV

for file in "$COUNTS_DIR"/txt/counts_*.txt; do
    CSV_FILE="$COUNTS_DIR/csv/$(basename "$file" .txt).csv"
    python "$SCRIPT_DIR/convert2csv.py" -i "$file" -o "$CSV_FILE"
done

# PART 6: CALCULATE RELATIVE ABUNDANCE

for file in "$COUNTS_DIR"/csv/counts_*.csv; do
    CSV_RA_FILE="$COUNTS_DIR/csv_relabund/$(basename "$file")"
    python "$SCRIPT_DIR/relabund.py" -i "$file" -o "$CSV_RA_FILE"
done

echo "All steps completed successfully!"