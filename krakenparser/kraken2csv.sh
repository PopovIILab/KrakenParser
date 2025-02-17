#!/bin/bash

# Check if the correct number of arguments was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 PATH_TO_SOURCE"
    exit 1
fi

# Determine the directory of this script
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# PART 1: CONVERT KRAKEN2 TO MPA

# Setting the path to the source file directory and destination directory
SOURCE_DIR=$1
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

echo "All steps completed successfully!"