#!/bin/bash

# Check if the correct number of arguments was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 PATH_TO_SOURCE"
    exit 1
fi

# PART 1: CONVERT KRAKEN2 TO MPA

# Setting the path to the source file directory and destination directory
SOURCE_DIR=$1
PARENT_DIR=$(dirname "$SOURCE_DIR")
MPA_DIR="$PARENT_DIR/mpa"

# Run the old script with the correct paths
./scripts/run_kreport2mpa.sh "$SOURCE_DIR" "$MPA_DIR"

# PART 2: COMBINING MPAs

COMBINED_FILE="$PARENT_DIR/COMBINED.txt"
python KrakenTools/combine_mpa.py -i "$MPA_DIR"/* -o "$COMBINED_FILE"
if [ $? -ne 0 ]; then
    echo "Error: Failed to run combine_mpa.py"
    exit 1
fi
echo "MPA files combined successfully. Output stored in $COMBINED_FILE"

# PART 3: DECOMBINING MPAs

COUNTS_DIR="$PARENT_DIR/counts"

# Create the destination directory if it doesn't exist
mkdir -p "$COUNTS_DIR"
mkdir -p "${COUNTS_DIR}"/txt
mkdir -p "${COUNTS_DIR}"/csv

./scripts/decombine.sh "$COMBINED_FILE" "$COUNTS_DIR"

# PART 4: PROCESS COUNTS TXT FILES

for file in "$COUNTS_DIR"/txt/counts_*.txt; do
    python scripts/processing_script.py "$COMBINED_FILE" "$file"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to process $file"
        exit 1
    fi
    echo "Processed $file successfully."
done

# PART 5: CONVERT TXT FILES TO CSV

for file in "$COUNTS_DIR"/txt/counts_*.txt; do
    CSV_FILE="$COUNTS_DIR/csv/$(basename "$file" .txt).csv"
    python scripts/convert2csv.py "$file" "$CSV_FILE"
done

echo "All steps completed successfully!"