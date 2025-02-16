# Kraken2CSV: Convert Kraken2 Reports to CSV

## Overview
Kraken2CSV is a collection of scripts designed to process Kraken2 reports and convert them into CSV format. This pipeline extracts taxonomic abundance data at six levels:
- **Phylum**
- **Class**
- **Order**
- **Family**
- **Genus**
- **Species**

## Output example

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

You can run the entire pipeline with **a single command**, or use the scripts **individually** depending on your needs.

## Quick Start (Full Pipeline)
To run the full pipeline, use the following command:
```bash
! ./Kraken2CSV/kraken2csv.sh data/kreports
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

## Installation & Dependencies
Ensure you have the following installed:
- **Python 3**
- **pandas** (`pip install pandas`)
- **KrakenTools** (https://github.com/jenniferlu717/KrakenTools)

## Using Individual Scripts
You can also run each step manually if needed.

### **Step 1: Convert Kraken2 Reports to MPA Format**
```bash
! ./scripts/run_kreport2mpa.sh data/kreports data/mpa
```
This script converts Kraken2 `.kreport` files into **MPA format** using KrakenTools.

### **Step 2: Combine MPA Files**
```bash
%run KrakenTools/combine_mpa.py -i data/mpa/* -o data/COMBINED.txt
```
This merges multiple MPA files into a single combined file.

### **Step 3: Extract Taxonomic Levels**
```bash
%%bash
grep -E "s__" data/COMBINED.txt \
| grep -v "t__" \
| grep -v "s__Homo_sapiens" \
| sed "s/^.*|//g" \
| sed "s/SRS[0-9]*-//g" \
> counts/txt/counts_species.txt
```
This step extracts only species-level data (excluding human reads). Similar commands apply for other levels.

### **Step 4: Process Extracted Taxonomic Data**
```bash
%%bash
for file in counts/txt/counts_*.txt
do
    python scripts/processing_script.py data/COMBINED.txt "$file"
done
```
This script cleans up taxonomic names (removes prefixes, replaces underscores with spaces).

### **Step 5: Convert TXT to CSV**
```bash
%%bash
for file in counts/txt/counts_*.txt
do
    python scripts/convert2csv.py "$file" counts/csv/$(basename "$file" .txt).csv
done
```
This converts the processed text files into structured CSV format.

## Script Breakdown
### **kraken2csv.sh** (Main Pipeline)
- Automates the entire workflow.
- Takes **one argument**: the path to Kraken2 reports (`data/kreports`).
- Runs all the scripts in sequence.

### **run_kreport2mpa.sh** (Step 1)
- Converts Kraken2 reports to MPA format.
- Uses `KrakenTools/kreport2mpa.py`.

### **combine_mpa.py** (Step 2)
- Combines multiple MPA files into one.

### **decombine.sh** (Step 3)
- Extracts **phylum, class, order, family, genus, species** into separate text files.
- Removes human-related reads.

### **processing_script.py** (Step 4)
- Cleans and formats extracted taxonomic data.
- Removes prefixes (`s__`, `g__`, etc.), replaces underscores with spaces.

### **convert2csv.py** (Step 5)
- Converts cleaned text files to CSV.
- Transposes data so that sample names become rows.

## Example Output Structure
After running the full pipeline, the output directory will look like this:
```
data/
├── kreports/            # Input Kraken2 reports
├── mpa/                 # Converted MPA files
├── COMBINED.txt         # Merged MPA file
├── counts/
│   ├── txt/             # Extracted taxonomic levels in TXT
│   │   ├── counts_species.txt
│   │   ├── counts_genus.txt
│   │   ├── counts_family.txt
│   │   ├── ...
│   ├── csv/             # Final CSV output
│   │   ├── counts_species.csv
│   │   ├── counts_genus.csv
│   │   ├── counts_family.csv
│   │   ├── ...
```

## Conclusion
Kraken2CSV provides a **simple and automated** way to convert Kraken2 reports into usable CSV files for downstream analysis. You can run the **full pipeline** with a single command or use **individual scripts** as needed.

For any issues or feature requests, feel free to open an issue on GitHub!

🚀 Happy analyzing!