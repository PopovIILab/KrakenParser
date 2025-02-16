#!/bin/bash

# Check if the correct number of arguments was provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 PATH_TO_SOURCE PATH_TO_DESTINATION"
    exit 1
fi

# Setting the path to the source file directory and destination directory
SOURCE_DIR=$1
DESTINATION_DIR=$2

# Creating a destination folder if it does not exist
mkdir -p "${DESTINATION_DIR}"

# Cycle through each file in the source file directory
for file in "${SOURCE_DIR}"/*.*; do
    # Getting file name without path
    filename=$(basename "${file}")
    # Forming a command to process a file
    python KrakenTools/kreport2mpa.py -r "${file}" -o "${DESTINATION_DIR}/${filename/.kreport/.MPA.TXT}" --display-header
done

if [ $? -ne 0 ]; then
    echo "Error: Failed to run run_kreport2mpa.sh"
    exit 1
fi
echo "Converted to MPA successfully. Output stored in $DESTINATION_DIR"