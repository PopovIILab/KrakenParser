#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 -i PATH_TO_SOURCE -o PATH_TO_DESTINATION"
    echo
    echo "  -i, --input PATH_TO_SOURCE       Path to the source directory containing files to convert."
    echo "  -o, --output PATH_TO_DESTINATION  Path to the destination directory where converted files will be stored."
    echo "  -h, --help                       Display this help message and exit."
    echo
    echo "This script converts files in the source directory with the .kreport extension to .MPA.TXT format."
    echo "It uses KrakenTools' \`kreport2mpa.py\` Python script to perform the conversion."
    echo "The converted files will be saved in the specified destination directory."
    exit 0
}

# Initialize variables
SOURCE_DIR=""
DESTINATION_DIR=""

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -i|--input) SOURCE_DIR="$2"; shift 2 ;;
        -o|--output) DESTINATION_DIR="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

# Check if required arguments are provided
if [ -z "$SOURCE_DIR" ] || [ -z "$DESTINATION_DIR" ]; then
    echo "Error: Both input and output paths are required."
    usage
fi

# Determine the directory of this script
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Ensure KrakenTools script exists
KREPORT_SCRIPT="$SCRIPT_DIR/kreport2mpa.py"
if [ ! -f "$KREPORT_SCRIPT" ]; then
    echo "Error: kreport2mpa.py not found in $SCRIPT_DIR"
    exit 1
fi

# Create the destination folder if it does not exist
mkdir -p "${DESTINATION_DIR}"

# Convert files in the source directory
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