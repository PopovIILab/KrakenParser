#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 -i PATH_TO_SOURCE_FILE -o PATH_TO_DESTINATION"
    exit 1
}

# Initialize variables
SOURCE_FILE=""
DESTINATION_DIR=""

# Parse command-line options
while getopts "i:o:" opt; do
    case $opt in
        i) SOURCE_FILE="$OPTARG" ;;
        o) DESTINATION_DIR="$OPTARG" ;;
        *) usage ;;
    esac
done

# Check if both options were provided
if [ -z "$SOURCE_FILE" ] || [ -z "$DESTINATION_DIR" ]; then
    usage
fi

# Create destination directories
mkdir -p "${DESTINATION_DIR}/txt"
mkdir -p "${DESTINATION_DIR}/csv"

# Process input file and generate output files
grep -E "s__" "${SOURCE_FILE}" \
| grep -v "t__" \
| grep -v "s__Homo_sapiens" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> "${DESTINATION_DIR}/txt/counts_species.txt"

grep -E "g__" "${SOURCE_FILE}" \
| grep -v "t__" \
| grep -v "s__" \
| grep -v "g__Homo" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> "${DESTINATION_DIR}/txt/counts_genus.txt"

grep -E "f__" "${SOURCE_FILE}" \
| grep -v "t__" \
| grep -v "s__" \
| grep -v "g__" \
| grep -v "f__Hominidae" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> "${DESTINATION_DIR}/txt/counts_family.txt"

grep -E "o__" "${SOURCE_FILE}" \
| grep -v "t__" \
| grep -v "s__" \
| grep -v "g__" \
| grep -v "f__" \
| grep -v "o__Primates" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> "${DESTINATION_DIR}/txt/counts_order.txt"

grep -E "c__" "${SOURCE_FILE}" \
| grep -v "t__" \
| grep -v "s__" \
| grep -v "g__" \
| grep -v "f__" \
| grep -v "o__" \
| grep -v "c__Mammalia" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> "${DESTINATION_DIR}/txt/counts_class.txt"

grep -E "p__" "${SOURCE_FILE}" \
| grep -v "t__" \
| grep -v "s__" \
| grep -v "g__" \
| grep -v "f__" \
| grep -v "o__" \
| grep -v "c__" \
| grep -v "p__Chordata" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> "${DESTINATION_DIR}/txt/counts_phylum.txt"

# Check for errors
if [ $? -ne 0 ]; then
    echo "Error: Failed to run decombine.sh"
    exit 1
fi

echo "MPA file decombined successfully. Output stored in $DESTINATION_DIR"