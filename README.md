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

### Total abundance output

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

### Relative abundance `.csv` output

`counts_phylum.csv` parsed from 7 kraken2 reports of metagenomic samples using `KrakenParser`:

```
Sample_id,taxon,rel_abund_perc
X12,Pseudomonadota,59.45772220448566
X12,Euryarchaeota,18.31670744178662
X12,Actinomycetota,8.996761322991876
X12,Other (<3.5%),7.299742374085121
X12,Thermodesulfobacteriota,5.929066656650726
X13,Euryarchaeota,43.13026941990481
X13,Pseudomonadota,39.23287866024437
X13,Other (<3.5%),7.276209401617095
X13,Thermodesulfobacteriota,5.639854274215032
X13,Actinomycetota,4.72078824401869
X14,Bacillota,34.34990866595965
X14,Pseudomonadota,24.631178075323472
X14,Euryarchaeota,19.192448404834906
X14,Thermodesulfobacteriota,11.065854871125346
X14,Other (<3.5%),10.760609982756622
X17,Pseudomonadota,39.388087541135384
X17,Thermodesulfobacteriota,34.62882760036646
X17,Other (<3.5%),10.126568180629615
X17,Actinomycetota,5.762973020610789
X17,Euryarchaeota,5.326536027721231
X17,Bacillota,4.767007629536514
X18,Thermodesulfobacteriota,44.61072552960362
X18,Pseudomonadota,30.31998388150275
X18,Other (<3.5%),12.935751468859937
X18,Actinomycetota,6.21567616670579
X18,Bacillota,5.9178629533279015
```

## Quick Start (Full Pipeline)
To run the full pipeline, use the following command:
```bash
KrakenParser --complete -i data/kreports
#Having troubles? Run KrakenParser --complete -h
```
This will:
1. Convert Kraken2 reports to MPA format
2. Combine MPA files into a single file
3. Extract taxonomic levels into separate text files
4. Process extracted text files
5. Convert them into CSV format
6. Calculate relative abundance

### **Input Requirements**
- The Kraken2 reports must be inside a **subdirectory** (e.g., `data/kreports`).
- The script automatically creates output directories and processes the data.

## Installation

```
pip install krakenparser
```

## Using Individual Modules
You can also run each step manually if needed.

### **Step 1: Convert Kraken2 Reports to MPA Format**
```bash
KrakenParser --kreport2mpa -i data/kreports -o data/mpa
#Having troubles? Run KrakenParser --kreport2mpa -h
```
This script converts Kraken2 `.kreport` files into **MPA format** using KrakenTools.

### **Step 2: Combine MPA Files**
```bash
KrakenParser --combine_mpa -i data/mpa/* -o data/COMBINED.txt
#Having troubles? Run KrakenParser --combine_mpa -h
```
This merges multiple MPA files into a single combined file.

### **Step 3: Extract Taxonomic Levels**
```bash
KrakenParser --deconstruct -i data/COMBINED.txt -o data/counts
#Having troubles? Run KrakenParser --deconstruct -h
```

If user wants to inspect **Viruses** domain separately:
```bash
KrakenParser --deconstruct_viruses -i data/COMBINED.txt -o data/counts_viruses
#Having troubles? Run KrakenParser --deconstruct_viruses -h
```

This step extracts only species-level data (excluding human reads).

### **Step 4: Process Extracted Taxonomic Data**
```bash
KrakenParser --process -i data/COMBINED.txt -o data/counts/txt/counts_phylum.txt
#Having troubles? Run KrakenParser --process -h
```

Repeat on other 5 taxonomical levels (class, order, family, genus, species) or wrap up `KrakenParser --process` to a loop!

This script cleans up taxonomic names (removes prefixes, replaces underscores with spaces).

### **Step 5: Convert TXT to CSV**
```bash
KrakenParser --txt2csv -i data/counts/txt/counts_phylum.txt -o data/counts/csv/counts_phylum.csv
#Having troubles? Run KrakenParser --txt2csv -h
```
Repeat on other 5 taxonomical levels (class, order, family, genus, species) or wrap up `KrakenParser --txt2csv` to a loop!

This converts the processed text files into structured CSV format.

### **Step 6: Calculate relative abundance**
```bash
KrakenParser --relabund -i data/counts/csv/counts_phylum.csv -o data/counts/csv_relabund/counts_phylum.csv
#Having troubles? Run KrakenParser --txt2csv -h
```
Repeat on other 5 taxonomical levels (class, order, family, genus, species) or wrap up `KrakenParser --relabund` to a loop!

This calculates relative abundance and saves as CSV format.

If user wants to group low abundant taxa in "Other" group:
```bash
KrakenParser --relabund -i data/counts/csv/counts_phylum.csv -o data/counts/csv_relabund/counts_phylum.csv --other 3.5
#Having troubles? Run KrakenParser --deconstruct_viruses -h
```

This will group all the taxa that have abundance <3.5 into "Other <3.5%" group. Other parameters are welcome!

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
- Uses `KrakenTools/combine_mpa.py`.

### **--deconstruct** & **--deconstruct_viruses** (Step 3)
- Extracts **phylum, class, order, family, genus, species** into separate text files.
- Removes human-related reads (**--deconstruct** only).

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
├─ kreports/           # Input Kraken2 reports
├─ mpa/                # Converted MPA files
├─ COMBINED.txt        # Merged MPA file
└─ counts/
   ├─ txt/             # Extracted taxonomic levels in TXT
   │  ├─ counts_species.txt
   │  ├─ counts_genus.txt
   │  ├─ counts_family.txt
   │  ├─ ...
   └─ csv/             # Total abundance CSV output
   │  ├─ counts_species.csv
   │  ├─ counts_genus.csv
   │  ├─ counts_family.csv
   │  ├─ ...
   └─ csv_relabund/    # Relative abundance CSV output
   │  ├─ counts_species.csv
   │  ├─ counts_genus.csv
   │  ├─ counts_family.csv
   │  ├─ ...
```

## Conclusion
KrakenParser provides a **simple and automated** way to convert Kraken2 reports into usable CSV files for downstream analysis. You can run the **full pipeline** with a single command or use **individual scripts** as needed.

For any issues or feature requests, feel free to open an issue on GitHub!

🚀 Happy analyzing!
