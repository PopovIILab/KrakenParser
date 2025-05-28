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
Sample_id,Cercozoa,Ciliophora,Evosea,Fornicata,Parabasalia,Euglenozoa,Bacillariophyta,Apicomplexa,Microsporidia,Basidiomycota,Ascomycota,Thermosulfidibacterota,Coprothermobacterota,Candidatus Absconditabacteria,Caldisericota,Thermodesulfobiota,Calditrichota,Atribacterota,Elusimicrobiota,Dictyoglomota,Candidatus Bipolaricaulota,Candidatus Fervidibacterota,Candidatus Saccharibacteria,Nitrospinota,Chrysiogenota,Aquificota,Fusobacteriota,Nitrospirota,Synergistota,Thermotogota,Bdellovibrionota,Acidobacteriota,Campylobacterota,Myxococcota,Spirochaetota,Deferribacterota,Fibrobacterota,Gemmatimonadota,Candidatus Cloacimonadota,Balneolota,Ignavibacteriota,Rhodothermota,Chlorobiota,Bacteroidota,Candidatus Omnitrophota,Lentisphaerota,Chlamydiota,Kiritimatiellota,Verrucomicrobiota,Planctomycetota,Thermodesulfobacteriota,Thermomicrobiota,Vulcanimicrobiota,Armatimonadota,Mycoplasmatota,Chloroflexota,Cyanobacteriota,Deinococcota,Bacillota,Actinomycetota,Pseudomonadota,Nanoarchaeota,Candidatus Nanohalarchaeota,Candidatus Micrarchaeota,Candidatus Lokiarchaeota,Candidatus Korarchaeota,Nitrososphaerota,Thermoproteota,Candidatus Thermoplasmatota,Euryarchaeota,Taleaviricota,Saleviricota,Artverviricota,Lenarviricota,Duplornaviricota,Kitrinoviricota,Negarnaviricota,Pisuviricota,Preplasmiviricota,Nucleocytoviricota,Peploviricota,Uroviricota,Phixviricota,Hofneiviricota,Cossaviricota,Cressdnaviricota
X12,0,0,0,1,7,75,12,213,0,619,3361,0,0,0,2,4,4,5,16,23,2,5,34,57,65,94,125,206,365,512,781,894,1083,1296,1305,3372,7,65,70,8,22,114,410,8722,3,5,21,194,756,25626,69457,26,33,62,138,575,1709,11456,19610,105394,696527,0,0,0,2,1,16,58,82,214574,0,0,0,0,0,0,9,12,5,19,2,470,3,194,0,471
X13,0,0,6,0,67,136,11,450,0,731,4204,8,8,2,2,11,18,23,34,17,7,4,36,69,145,185,492,271,521,1068,2193,1303,1350,1362,9272,14473,11,73,106,20,66,191,987,13963,6,10,59,590,1032,25916,125332,8,16,119,392,748,2951,7468,66347,104908,871855,0,0,2,14,2,44,177,93,958465,0,0,1,0,1,2,17,48,2,56,23,1094,1,0,0,561
X14,0,35,144,1,322,147,9,1983,9,1009,5675,16,79,30,42,175,129,216,128,219,23,1,82,206,235,541,7375,812,2374,5434,684,2027,10044,1562,7480,4103,51,137,380,75,435,333,1660,69771,14,146,491,900,1490,8199,235713,35,9,116,5052,2433,10799,1935,731685,66706,524667,1,5,2,43,2,888,1098,227,408817,1,1,2,1,1,2,155,75,21,329,10,1686,4,2,31,106
X17,5,2,90,3,258,345,209,1303,103,996,5835,256,6,15,19,31,297,119,220,47,62,159,154,138,5005,332,964,1597,2723,8999,984,7242,21739,5174,30158,842,23,735,93,58,452,528,5405,51595,174,33,354,1539,4876,10581,715131,242,17,384,2957,8519,16706,4874,98445,119013,813416,1,0,4,50,8,356,581,112,110000,2,2,1,2,3,3,45,25,76,154,16,1063,8,0,1,38
X18,0,1,69,1,283,509,283,1645,191,1575,8357,433,12,10,9,30,285,52,253,39,51,278,86,194,7353,425,1094,2687,4059,4774,1632,9596,10543,6941,89344,921,14,1317,43,31,433,843,9514,56724,93,23,267,2551,6433,14313,1153566,348,10,497,2371,4568,23113,7157,153027,160728,784029,0,0,2,23,1,525,776,125,46762,0,0,3,6,0,6,50,8,73,103,22,1269,24,0,3,40
```

### Relative abundance output

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
   │  ├─ counts_species.csv
   │  ├─ counts_genus.csv
   │  ├─ counts_family.csv
   │  ├─ ...
```

## Conclusion
KrakenParser provides a **simple and automated** way to convert Kraken2 reports into usable CSV files for downstream analysis. You can run the **full pipeline** with a single command or use **individual scripts** as needed.

For any issues or feature requests, feel free to open an issue on GitHub!

🚀 Happy analyzing!
