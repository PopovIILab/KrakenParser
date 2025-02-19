#!/bin/bash

# Function to display detailed usage information
usage() {
    echo "Usage: $0 -i PATH_TO_SOURCE_FILE -o PATH_TO_DESTINATION"
    echo
    echo "  -i, --input    PATH_TO_SOURCE_FILE    Path to the Combined MPA input file to be processed."
    echo "  -o, --output   PATH_TO_DESTINATION    Path to the directory where processed output files will be stored."
    echo "  -h, --help                           Display this help message and exit."
    echo
    echo "Description:"
    echo "  This script processes a combined mpa file by extracting different taxonomic levels"
    echo "  (species, genus, family, order, class, and phylum) and saving the results as separate text files."
    echo "  Additionally, it removes human-related sequences to improve data accuracy."
    echo
    echo "Processing Details:"
    echo "  - Extracts taxonomic levels using 'grep' with specific patterns."
    echo "  - Filters out undesired taxonomic entries such as:"
    echo "    - Species: Homo sapiens"
    echo "    - Genus: Homo"
    echo "    - Family: Hominidae"
    echo "    - Order: Primates"
    echo "    - Class: Mammalia"
    echo "    - Phylum: Chordata"
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