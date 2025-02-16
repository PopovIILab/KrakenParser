# KrakenParser: Convert Kraken2 Reports to CSV

<img src="https://github.com/PopovIILab/KrakenParser/blob/main/imgs/KrakenParser_logo_light.png#gh-light-mode-only" align="left"/>
<img src="https://github.com/PopovIILab/KrakenParser/blob/main/imgs/KrakenParser_logo_dark.png#gh-dark-mode-only" align="left"/>

## Overview
KrakenParser is a collection of scripts designed to process Kraken2 reports and convert them into CSV format. This pipeline extracts taxonomic abundance data at six levels:
- **Phylum**
- **Class**
- **Order**
- **Family**
- **Genus**
- **Species**

You can run the entire pipeline with **a single command**, or use the scripts **individually** depending on your needs.

## Output example

`counts_phylum.csv` parsed from 7 kraken2 reports of metagenomic samples using `KrakenParser`:

```
Sample_id,Euryarchaeota,Euglenozoa,Parabasalia,Apicomplexa,Basidiomycota,Ascomycota,Acidobacteriota,Bdellovibrionota,Chlorobiota,Ignavibacteriota,Planctomycetota,Spirochaetota,Thermotogota,Fusobacteriota,Cyanobacteriota,Mycoplasmatota,Actinomycetota,Pseudomonadota,Bacteroidota,Deferribacterota,Campylobacterota,Thermodesulfobacteriota,Bacillota,Negarnaviricota,Nucleocytoviricota,Uroviricota,Peploviricota
X1,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
X2,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,4,0,0,0,0
X3,11,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,0,0,0,4,0,0,0,0
X4,1313,0,0,0,0,4,0,0,0,0,0,1,2,2,1,3,3,17,33,4,5,4,112,0,0,0,0
X5,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0
X6,0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0,3,3,0,3,2,13,0,0,0,1
X7,20,1,1,5,1,9,1,6,1,7,1,13,1,3,9,4,10,139,519,0,8,2,81,1,3,1,0
```

This `counts_phylum.csv` is easy to visualize as Relative Abundance Barplot!

## Quick Start (Full Pipeline)
To run the full pipeline, use the following command:
```bash
KrakenParser data/kreports
```
This will:
1. Convert Kraken2 reports to MPA format
2. Combine MPA files into a single file
3. Extract taxonomic levels into separate text files
4. Process extracted text files
5. Convert them into CSV format

### **Input Requirements**
- The Kraken2 reports must be inside a **subdirectory** (e.g., `data/kreports`).
- The script automatically creates output directories and processes the data.

## Installation

```
pip install krakenparser
```

## Using Individual Scripts
You can also run each step manually if needed.

### **Step 1: Convert Kraken2 Reports to MPA Format**
```bash
KrakenParser --kreport2mpa data/kreports data/mpa
```
This script converts Kraken2 `.kreport` files into **MPA format** using KrakenTools.

### **Step 2: Combine MPA Files**
```bash
KrakenParser --combine_mpa -i data/mpa/* -o data/COMBINED.txt
```
This merges multiple MPA files into a single combined file.

### **Step 3: Extract Taxonomic Levels**
```bash
KrakenParser --deconstruct data/COMBINED.txt data/counts
```

<details><summary>
<b>Clipped image from decombine.sh:</b>
</summary><br> 

```bash
#!/bin/bash

# Check if the correct number of arguments was provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 PATH_TO_SOURCE PATH_TO_DESTINATION"
    exit 1
fi

# Setting the path to the source file directory and destination directory
SOURCE_FILE=$1
DESTINATION_DIR=$2

mkdir -p "${DESTINATION_DIR}"
mkdir -p "${DESTINATION_DIR}"/txt
mkdir -p "${DESTINATION_DIR}"/csv

grep -E "s__" "${SOURCE_FILE}" \
| grep -v "t__" \
| grep -v "s__Homo_sapiens" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> "${DESTINATION_DIR}"/txt/counts_species.txt

grep -E "g__" "${SOURCE_FILE}" \
| grep -v "t__" \
| grep -v "s__" \
| grep -v "g__Homo" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> "${DESTINATION_DIR}"/txt/counts_genus.txt

grep -E "f__" "${SOURCE_FILE}" \
| grep -v "t__" \
| grep -v "s__" \
| grep -v "g__" \
| grep -v "f__Hominidae" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> "${DESTINATION_DIR}"/txt/counts_family.txt

grep -E "o__" "${SOURCE_FILE}" \
| grep -v "t__" \
| grep -v "s__" \
| grep -v "g__" \
| grep -v "f__" \
| grep -v "o__Primates" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> "${DESTINATION_DIR}"/txt/counts_order.txt

grep -E "c__" "${SOURCE_FILE}" \
| grep -v "t__" \
| grep -v "s__" \
| grep -v "g__" \
| grep -v "f__" \
| grep -v "o__" \
| grep -v "c__Mammalia" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> "${DESTINATION_DIR}"/txt/counts_class.txt

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
> "${DESTINATION_DIR}"/txt/counts_phylum.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to run decombine.sh"
    exit 1
fi
echo "MPA file decombined successfully. Output stored in $DESTINATION_DIR"
```
  
</details>

This step extracts only species-level data (excluding human reads).

### **Step 4: Process Extracted Taxonomic Data**
```bash
KrakenParser --process data/COMBINED.txt data/counts/txt/counts_phylum.txt
```
```bash
KrakenParser --process data/COMBINED.txt data/counts/txt/counts_class.txt
```
```bash
KrakenParser --process data/COMBINED.txt data/counts/txt/counts_order.txt
```
```bash
KrakenParser --process data/COMBINED.txt data/counts/txt/counts_family.txt
```
```bash
KrakenParser --process data/COMBINED.txt data/counts/txt/counts_genus.txt
```
```bash
KrakenParser --process data/COMBINED.txt data/counts/txt/counts_species.txt
```
This script cleans up taxonomic names (removes prefixes, replaces underscores with spaces).

### **Step 5: Convert TXT to CSV**
```bash
KrakenParser --txt2csv data/counts/txt/counts_phylum.txt data/counts/csv/counts_phylum.csv
```
```bash
KrakenParser --txt2csv data/counts/txt/counts_class.txt data/counts/csv/counts_class.csv
```
```bash
KrakenParser --txt2csv data/counts/txt/counts_order.txt data/counts/csv/counts_order.csv
```
```bash
KrakenParser --txt2csv data/counts/txt/counts_family.txt data/counts/csv/counts_family.csv
```
```bash
KrakenParser --txt2csv data/counts/txt/counts_genus.txt data/counts/csv/counts_genus.csv
```
```bash
KrakenParser --txt2csv data/counts/txt/counts_species.txt data/counts/csv/counts_species.csv
```
This converts the processed text files into structured CSV format.

## Arguments Breakdown
### **KrakenParser** (Main Pipeline)
- Automates the entire workflow.
- Takes **one argument**: the path to Kraken2 reports (`data/kreports`).
- Runs all the scripts in sequence.

### **--kreport2mpa** (Step 1)
- Converts Kraken2 reports to MPA format.
- Uses `KrakenTools/kreport2mpa.py`.

### **--combine_mpa** (Step 2)
- Combines multiple MPA files into one.

### **--deconstruct** (Step 3)
- Extracts **phylum, class, order, family, genus, species** into separate text files.
- Removes human-related reads.

### **--process** (Step 4)
- Cleans and formats extracted taxonomic data.
- Removes prefixes (`s__`, `g__`, etc.), replaces underscores with spaces.

### **--txt2csv** (Step 5)
- Converts cleaned text files to CSV.
- Transposes data so that sample names become rows.

## Example Output Structure
After running the full pipeline, the output directory will look like this:
```
data/
├─ kreports/            # Input Kraken2 reports
├─ mpa/                 # Converted MPA files
├─ COMBINED.txt         # Merged MPA file
└─ counts/
   ├─ txt/             # Extracted taxonomic levels in TXT
   │  ├─ counts_species.txt
   │  ├─ counts_genus.txt
   │  ├─ counts_family.txt
   │  ├── ...
   └─ csv/             # Final CSV output
      ├─ counts_species.csv
      ├─ counts_genus.csv
      ├─ counts_family.csv
      ├─ ...
```

## Conclusion
KrakenParser provides a **simple and automated** way to convert Kraken2 reports into usable CSV files for downstream analysis. You can run the **full pipeline** with a single command or use **individual scripts** as needed.

For any issues or feature requests, feel free to open an issue on GitHub!

🚀 Happy analyzing!
