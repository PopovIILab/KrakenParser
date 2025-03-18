#!/bin/bash

# Function to display detailed usage information
usage() {
    echo "Usage: $(basename "$0") -i PATH_TO_SOURCE_FILE -o PATH_TO_DESTINATION"
    echo
    echo "  -i, --input    PATH_TO_SOURCE_FILE    Path to the Combined MPA input file to be processed."
    echo "  -o, --output   PATH_TO_DESTINATION    Path to the directory where processed output files will be stored."
    echo "  -h, --help                           Display this help message and exit."
    echo
    echo "Description:"
    echo "  This script processes a combined mpa file by extracting different taxonomic levels using only VIRUSES domain"
    echo "  (species, genus, family, order, class, and phylum) and saving the results as separate text files."
    echo
    echo "Processing Details:"
    echo "  - Extracts taxonomic levels only on VIRUSES domain using 'grep' with specific patterns."
    echo "  - Outputs are stored as text files inside the specified destination directory."
    exit 0
}

# Initialize variables
SOURCE_FILE=""
DESTINATION_DIR=""

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -i|--input) SOURCE_FILE="$2"; shift 2 ;;
        -o|--output) DESTINATION_DIR="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Error: Unknown option $1"; usage ;;
    esac
done

# Check if required arguments are provided
if [[ -z "$SOURCE_FILE" || -z "$DESTINATION_DIR" ]]; then
    echo "Error: Both input (-i) and output (-o) paths are required."
    usage
fi

# Check if source file exists
if [[ ! -f "$SOURCE_FILE" ]]; then
    echo "Error: Input file '$SOURCE_FILE' not found!"
    exit 1
fi

# Create destination directories
mkdir -p "${DESTINATION_DIR}/txt"
mkdir -p "${DESTINATION_DIR}/csv"

VIRUSES_BUFFER=$(grep -E "d__Viruses" "${SOURCE_FILE}")

# Process input file and generate output files
echo "$VIRUSES_BUFFER" | grep -E "s__" \
    | grep -v "t__" \
    | sed "s/^.*|//g" \
    | sed "s/SRS[0-9]*-//g" \
    > "${DESTINATION_DIR}/txt/counts_species.txt"

echo "$VIRUSES_BUFFER" | grep -E "g__" \
    | grep -v "t__" \
    | grep -v "s__" \
    | sed "s/^.*|//g" \
    | sed "s/SRS[0-9]*-//g" \
    > "${DESTINATION_DIR}/txt/counts_genus.txt"

echo "$VIRUSES_BUFFER" | grep -E "f__" \
    | grep -v "t__" \
    | grep -v "s__" \
    | grep -v "g__" \
    | sed "s/^.*|//g" \
    | sed "s/SRS[0-9]*-//g" \
    > "${DESTINATION_DIR}/txt/counts_family.txt"

echo "$VIRUSES_BUFFER" | grep -E "o__" \
    | grep -v "t__" \
    | grep -v "s__" \
    | grep -v "g__" \
    | grep -v "f__" \
    | sed "s/^.*|//g" \
    | sed "s/SRS[0-9]*-//g" \
    > "${DESTINATION_DIR}/txt/counts_order.txt"

echo "$VIRUSES_BUFFER" | grep -E "c__" \
    | grep -v "t__" \
    | grep -v "s__" \
    | grep -v "g__" \
    | grep -v "f__" \
    | grep -v "o__" \
    | sed "s/^.*|//g" \
    | sed "s/SRS[0-9]*-//g" \
    > "${DESTINATION_DIR}/txt/counts_class.txt"

echo "$VIRUSES_BUFFER" | grep -E "p__" \
    | grep -v "t__" \
    | grep -v "s__" \
    | grep -v "g__" \
    | grep -v "f__" \
    | grep -v "o__" \
    | grep -v "c__" \
    | sed "s/^.*|//g" \
    | sed "s/SRS[0-9]*-//g" \
    > "${DESTINATION_DIR}/txt/counts_phylum.txt"

# Check for errors
if [ $? -ne 0 ]; then
    echo "Error: Failed to run decombine_viruses.sh"
    exit 1
fi

echo "MPA file decombined successfully. Output stored in $DESTINATION_DIR"