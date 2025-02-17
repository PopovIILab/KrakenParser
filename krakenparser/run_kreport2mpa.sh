#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 -i PATH_TO_SOURCE -o PATH_TO_DESTINATION"
    exit 1
}

# Initialize variables
SOURCE_DIR=""
DESTINATION_DIR=""

# Parse command-line options
while getopts "i:o:" opt; do
    case $opt in
        i) SOURCE_DIR="$OPTARG" ;;
        o) DESTINATION_DIR="$OPTARG" ;;
        *) usage ;;
    esac
done

# Check if both options were provided
if [ -z "$SOURCE_DIR" ] || [ -z "$DESTINATION_DIR" ]; then
    usage
fi

# Determine the directory of this script
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Create the destination folder if it does not exist
mkdir -p "${DESTINATION_DIR}"

# Cycle through each file in the source directory
for file in "${SOURCE_DIR}"/*.*; do
    # Get the file name without path
    filename=$(basename "${file}")
    # Form the command to process the file
    python "$SCRIPT_DIR/kreport2mpa.py" -r "${file}" -o "${DESTINATION_DIR}/${filename/.kreport/.MPA.TXT}" --display-header
done

# Check exit status
if [ $? -ne 0 ]; then
    echo "Error: Conversion process failed."
    exit 1
fi

echo "Converted to MPA successfully. Output stored in $DESTINATION_DIR"