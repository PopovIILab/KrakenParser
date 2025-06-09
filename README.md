# KrakenParser: Convert Kraken2 Reports to CSV

![License](https://img.shields.io/badge/License-MIT-steelblue)
[![Downloads](https://static.pepy.tech/badge/krakenparser)](https://pepy.tech/project/krakenparser)
[![CI](https://github.com/PopovIILab/KrakenParser/actions/workflows/ci.yml/badge.svg)](https://github.com/PopovIILab/KrakenParser/actions/workflows/ci.yml)

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

🔗 Please visit [KrakenParser wiki](https://github.com/PopovIILab/KrakenParser/wiki) page

## Output example

### Total abundance output

`counts_phylum.csv` parsed from 7 kraken2 reports of metagenomic samples using `KrakenParser`:

```
Sample_id,Calditrichota,Caldisericota,Thermosulfidibacterota,Elusimicrobiota,Candidatus Fervidibacterota,Lentisphaerota,Kiritimatiellota,Vulcanimicrobiota,Thermodesulfobiota,Atribacterota,Dictyoglomota,Nitrospinota,Chrysiogenota,Coprothermobacterota,Aquificota,Thermotogota,Bdellovibrionota,Nitrospirota,Deferribacterota,Synergistota,Myxococcota,Acidobacteriota,Candidatus Bipolaricaulota,Candidatus Saccharibacteria,Candidatus Absconditabacteria,Fusobacteriota,Spirochaetota,Candidatus Omnitrophota,Chlamydiota,Verrucomicrobiota,Planctomycetota,Thermodesulfobacteriota,Campylobacterota,Candidatus Cloacimonadota,Fibrobacterota,Gemmatimonadota,Balneolota,Rhodothermota,Ignavibacteriota,Chlorobiota,Bacteroidota,Deinococcota,Thermomicrobiota,Armatimonadota,Chloroflexota,Cyanobacteriota,Mycoplasmatota,Actinomycetota,Bacillota,Pseudomonadota,Heterolobosea,Parabasalia,Fornicata,Evosea,Bacillariophyta,Cercozoa,Euglenozoa,Apicomplexa,Microsporidia,Basidiomycota,Ascomycota,Nanoarchaeota,Candidatus Micrarchaeota,Candidatus Thermoplasmatota,Candidatus Lokiarchaeota,Nitrososphaerota,Euryarchaeota,Thermoproteota,Hofneiviricota,Artverviricota,Nucleocytoviricota,Cossaviricota,Kitrinoviricota,Negarnaviricota,Lenarviricota,Pisuviricota,Peploviricota,Uroviricota
X1,0,0,0,0,0,0,0,0,1,1,1,1,2,3,4,5,7,8,9,17,23,25,5,13,22,47,54,1,6,27,31,128,151,2,6,13,1,3,7,44,14991,7,9,11,61,414,449,3551,55304,438645,0,0,0,0,0,0,1,22,0,4,15,0,0,0,0,0,3,191,0,0,1,88,0,0,0,161,0,1241
X2,1,4,14,20,5,12,15,6,8,15,2,15,109,68,182,97,79,196,70,272,331,149,36,77,35,562,1237,21,33,129,427,1044,543,8,98,25,16,45,11,1043,41374,160,28,161,1348,1196,2709,15864,431170,2747842,22,7,301,373,134,136,107,3239,54,1151,2905,0,0,3,5,6,7,410,0,0,0,736,0,3,11,26,1,1552
...
X8,1,19,0,47,0,1,6,20,28,0,1,1,47,7,336,110,30,32,10,93,85,48,9,7,7,154,386,0,14,19,106,358,242,14,5,134,15,11,7,18,54057,106,10,24,212,340,1128,16220,567908,650264,95,4,193,402,314,300,187,4376,37,9796,8653,0,1,0,1,5,23,1778,1,1,0,1,1,4,66,30,4,1263
X9,0,3,2,16,7,1,23,12,10,9,1,2,134,40,390,289,29,372,27,81,150,90,9,88,32,287,881,14,33,60,319,1045,328,15,22,22,10,72,8,63,35301,127,15,48,412,935,2343,11500,380765,2613854,0,0,0,0,0,0,5,74,0,38,40,3,0,0,0,1,3,275,0,0,0,0,0,2,118,25,0,1675

```

### Relative abundance output

`counts_phylum.csv` parsed from 7 kraken2 reports of metagenomic samples using `KrakenParser`:

```
Sample_id,taxon,rel_abund_perc
Sample_id,taxon,rel_abund_perc
X1,Pseudomonadota,85.03558294577552
X1,Bacillota,10.72121619814011
X1,Other (<4.0%),4.243200856084384
X2,Pseudomonadota,84.28702055549813
X2,Bacillota,13.225663867469137
X2,Other (<4.0%),2.487315577032736
...
X8,Pseudomonadota,49.25373021277305
X8,Bacillota,43.01574040339849
X8,Bacteroidota,4.094504530639667
X8,Other (<4.0%),3.6360248531887933
X9,Pseudomonadota,85.62839981589192
X9,Bacillota,12.473649123439218
X9,Other (<4.0%),1.8979510606688494
```

### Visualization examples gallery

|[Stacked Barplot](https://github.com/PopovIILab/KrakenParser/wiki/Stacked-Barplot-API)|[Streamgraph](https://github.com/PopovIILab/KrakenParser/wiki/Streamgraph-API)|
|-------|-------|
|![kpstbar](https://github.com/user-attachments/assets/916b0164-28be-4f49-9634-707408487b85)|![kpstream](https://github.com/user-attachments/assets/5c6d930c-e85f-4e2e-9dbf-8caefca49a76)|

[Stacked Barplot + Streamgraph](https://github.com/PopovIILab/KrakenParser/wiki/Combined-Stacked-Barplot-&-Streamgraph)|[Clustermap](https://github.com/PopovIILab/KrakenParser/wiki/Clustermap)|
|-------|-------|
|![combined_white](https://github.com/user-attachments/assets/58acea93-f079-46fd-ac4b-d2ac83098c59)|![kpclust](https://github.com/user-attachments/assets/98a4d540-7c43-4802-8f77-277a5637a7a1)|

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
#Having troubles? Run KrakenParser --relabund -h
```
Repeat on other 5 taxonomical levels (class, order, family, genus, species) or wrap up `KrakenParser --relabund` to a loop!

This calculates relative abundance and saves as CSV format.

If user wants to group low abundant taxa in "Other" group:
```bash
KrakenParser --relabund -i data/counts/csv/counts_phylum.csv -o data/counts/csv_relabund/counts_phylum.csv --other 3.5
#Having troubles? Run KrakenParser --relabund -h
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

### **--relabund** (Step 6)
- Calculates relative abundance based on total abundance CSV.
- Optionally can group low abundant taxa.

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
      ├─ counts_species.csv
      ├─ counts_genus.csv
      ├─ counts_family.csv
      ├─ ...
```

## Conclusion
KrakenParser provides a **simple and automated** way to convert Kraken2 reports into usable CSV files for downstream analysis. You can run the **full pipeline** with a single command or use **individual scripts** as needed.

For any issues or feature requests, feel free to open an issue on GitHub!

🚀 Happy analyzing!
