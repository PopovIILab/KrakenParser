# KrakenParser: Convert Kraken2 Reports to CSV

![License](https://img.shields.io/badge/License-MIT-steelblue)
[![Downloads](https://static.pepy.tech/badge/krakenparser)](https://pepy.tech/project/krakenparser)
[![CI](https://github.com/PopovIILab/KrakenParser/actions/workflows/python-package.yml/badge.svg)](https://github.com/PopovIILab/KrakenParser/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/gh/PopovIILab/KrakenParser/graph/badge.svg)](https://codecov.io/gh/PopovIILab/KrakenParser)

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

`ra_phylum.csv` calculated from 7 kraken2 reports of metagenomic samples using `KrakenParser`:

```
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

### α-diversity output

`alpha_div.csv` calculated from 7 kraken2 reports of metagenomic samples using `KrakenParser`:

```
Sample,Shannon,Pielou,Chao1
X1,3.911345447107001,0.5269245043289149,2274.533185840708
X2,3.9944130792536563,0.4906424221265042,4155.0
...
X8,3.442077115880119,0.42753293021330063,4177.251358695652
X9,4.033664950188261,0.5050385978575492,3492.16
```

### β-diversity output

`beta_div_bray.csv` calculated from 7 kraken2 reports of metagenomic samples using `KrakenParser`:

```
,X1,X2,...,X8,X9
X1,0.0,0.398,...,0.61,0.353
X2,0.398,0.0,...,0.723,0.388
...
X8,0.61,0.723,...,0.0,0.665
X9,0.353,0.388,...,0.665,0.0
```

`beta_div_jaccard.csv` calculated from 7 kraken2 reports of metagenomic samples using `KrakenParser`:

```
,X1,X2,...,X8,X9
X1,0.0,0.7073170731707317,...,0.8223938223938224,0.7232472324723247
X2,0.7073170731707317,0.0,...,0.835016835016835,0.7352941176470589
...
X8,0.8223938223938224,0.835016835016835,...,0.0,0.8066914498141264
X9,0.7232472324723247,0.7352941176470589,...,0.8066914498141264,0.0
```

### Visualization examples gallery

|[Stacked Barplot](https://github.com/PopovIILab/KrakenParser/wiki/Stacked-Barplot-API)|[Streamgraph](https://github.com/PopovIILab/KrakenParser/wiki/Streamgraph-API)|
|-------|-------|
|![kpstbar](https://github.com/user-attachments/assets/916b0164-28be-4f49-9634-707408487b85)|![kpstream](https://github.com/user-attachments/assets/8fc09fdb-e397-4c39-9290-ad11da5335a8)|

[Stacked Barplot + Streamgraph](https://github.com/PopovIILab/KrakenParser/wiki/Combined-Stacked-Barplot-&-Streamgraph)|[Clustermap](https://github.com/PopovIILab/KrakenParser/wiki/Clustermap)|
|-------|-------|
|![combined_white](https://github.com/user-attachments/assets/48b3f6e3-6dd5-4298-a793-23dcd549e90c)|![kpclust](https://github.com/user-attachments/assets/98a4d540-7c43-4802-8f77-277a5637a7a1)|

## Quick Start (Full Pipeline)
To run the full pipeline, use the following command:
```bash
KrakenParser --complete -i data/kreports -o results/
#Having troubles? Run KrakenParser --complete -h
```

This will:
1. Convert Kraken2 reports to MPA format
2. Combine MPA files into a single file
3. Extract taxonomic levels into separate text files
4. Process extracted text files
5. Convert them into CSV format
6. Calculate relative abundance
7. Calculate α & β-diversities

## Installation

```
pip install krakenparser
```

## Before Visualization: Grouping Low-Abundance Taxa

The full pipeline automatically calculates relative abundance. Before passing data to visualization, it is strongly recommended to re-run `--relabund` with the `-O` flag — this collapses all taxa below the chosen threshold into a single **"Other"** group, producing much cleaner and more readable plots.

```bash
KrakenParser --relabund -i data/counts/counts_species.csv -o data/rel_abund/ra_species.csv -O 4
```

This groups every taxon with relative abundance **< 4 %** into `Other (<4.0%)`. Adjust the threshold to your data.

> **Note:** The pipeline-generated `rel_abund/ra_*.csv` files (no `-O`) preserve the full unfiltered data — use them for statistical analysis. Use the `-O` variant specifically for visualization.

---

<details>
<summary><b>Using Individual Modules (Advanced)</b></summary>
<br>

Each step of the pipeline can also be run individually. This is useful for re-running a single step, debugging, or integrating KrakenParser into a custom workflow.

### **Step 1: Convert Kraken2 Reports to MPA Format**
```bash
# Batch mode (directory)
KrakenParser --kreport2mpa -i data/kreports -o data/intermediate/mpa
# Single file
KrakenParser --kreport2mpa -r data/kreports/sample.kreport -o data/intermediate/mpa/sample.MPA.TXT
#Having troubles? Run KrakenParser --kreport2mpa -h
```
Converts Kraken2 `.kreport` files into **MPA format**.

### **Step 2: Combine MPA Files**
```bash
KrakenParser --combine_mpa -i data/intermediate/mpa/* -o data/intermediate/COMBINED.txt
#Having troubles? Run KrakenParser --combine_mpa -h
```
Merges multiple MPA files into a single combined table.

### **Step 3: Extract Taxonomic Levels**
```bash
KrakenParser --deconstruct -i data/intermediate/COMBINED.txt -o data/intermediate
#Having troubles? Run KrakenParser --deconstruct -h
```

By default, human-related taxa (Homo sapiens, Hominidae, Primates, Mammalia, Chordata) are removed. To keep them:
```bash
KrakenParser --deconstruct -i data/intermediate/COMBINED.txt -o data/intermediate --keep-human
```

To inspect the **Viruses** domain separately:
```bash
KrakenParser --deconstruct_viruses -i data/intermediate/COMBINED.txt -o data/counts_viruses
#Having troubles? Run KrakenParser --deconstruct_viruses -h
```

### **Step 4: Process Extracted Taxonomic Data**
```bash
KrakenParser --process -i data/intermediate/COMBINED.txt -o data/intermediate/txt/counts_phylum.txt
#Having troubles? Run KrakenParser --process -h
```

Repeat on other 5 taxonomical levels (class, order, family, genus, species) or wrap up `KrakenParser --process` in a loop.

Cleans up taxonomic names: removes prefixes (`s__`, `g__`, etc.) and replaces underscores with spaces.

### **Step 5: Convert TXT to CSV**
```bash
KrakenParser --txt2csv -i data/intermediate/txt/counts_phylum.txt -o data/counts/counts_phylum.csv
#Having troubles? Run KrakenParser --txt2csv -h
```
Repeat on other 5 taxonomical levels or wrap in a loop. Transposes data so that sample names become rows.

### **Step 6: Calculate Relative Abundance**
```bash
KrakenParser --relabund -i data/counts/counts_phylum.csv -o data/rel_abund/ra_phylum.csv
#Having troubles? Run KrakenParser --relabund -h
```
Repeat on other 5 taxonomical levels or wrap in a loop.

With "Other" grouping:
```bash
KrakenParser --relabund -i data/counts/counts_phylum.csv -o data/rel_abund/ra_phylum.csv -O 3.5
```
Groups all taxa with abundance < 3.5 % into `Other (<3.5%)`.

### **Step 7: Calculate α & β-Diversities**
```bash
KrakenParser --diversity -i data/counts/counts_species.csv -o data/diversity
#Having troubles? Run KrakenParser --diversity -h
```

With a custom rarefaction depth for β-diversity:
```bash
KrakenParser --diversity -i data/counts/counts_species.csv -o data/diversity --depth 750
```

---

## Arguments Breakdown

### **--complete** (Full Pipeline)
- Requires `-i`: path to the Kraken2 reports directory (e.g., `data/kreports`).
- Optional `-o`: output directory (default: parent of `-i`).
- Optional `--keep-human`: retain human-related taxa (default: filtered out).

### **--kreport2mpa** (Step 1)
- Batch mode: `-i DIR -o DIR` — converts all files in a directory.
- Single-file mode: `-r FILE -o FILE`.

### **--combine_mpa** (Step 2)
- `-i FILE [FILE ...]`: one or more MPA files.
- `-o FILE`: output merged table.

### **--deconstruct** & **--deconstruct_viruses** (Step 3)
- Extracts **phylum, class, order, family, genus, species** into separate text files.
- `--deconstruct` removes human-related reads by default; use `--keep-human` to retain them.
- `--deconstruct_viruses` extracts only the Viruses domain.

### **--process** (Step 4)
- Removes prefixes (`s__`, `g__`, etc.), replaces underscores with spaces.
- `-i`: COMBINED.txt (source for sample-name header); `-o`: target txt file.

### **--txt2csv** (Step 5)
- Transposes a processed txt file into a CSV with sample names as rows.

### **--relabund** (Step 6)
- Calculates relative abundance from a total-counts CSV.
- `-O FLOAT`: group taxa below FLOAT % into `Other (<FLOAT%)`.

### **--diversity** (Step 7)
- Shannon, Pielou & Chao1 for α-diversity.
- Bray-Curtis & Jaccard for β-diversity.
- `-d INT`: rarefaction depth for β-diversity (default: 1000).

</details>

## Example Output Structure
After running the full pipeline, the output directory will look like this:
```
data/
├─ kreports/               # Input Kraken2 reports
├─ counts/                 # Total abundance CSV output
│  ├─ counts_species.csv
│  ├─ counts_genus.csv
│  ├─ ...
│  └─ counts_phylum.csv
├─ rel_abund/              # Relative abundance CSV output
│  ├─ ra_species.csv
│  ├─ ra_genus.csv
│  ├─ ...
│  └─ ra_phylum.csv
├─ diversity/              # Diversity metrics
│  ├─ alpha_div.csv
│  ├─ beta_div_bray.csv
│  └─ beta_div_jaccard.csv
└─ intermediate/           # Intermediate files
   ├─ mpa/                 # Converted MPA files
   │  ├─ sample.MPA.TXT
   │  ├─ ...
   ├─ COMBINED.txt         # Merged MPA table
   └─ txt/                 # Extracted taxonomic levels in TXT
      ├─ counts_species.txt
      ├─ counts_genus.txt
      ├─ ...
      └─ counts_phylum.txt
```

## Conclusion
KrakenParser provides a **simple and automated** way to convert Kraken2 reports into usable CSV files for downstream analysis. You can run the **full pipeline** with a single command or use **individual scripts** as needed.

For any issues or feature requests, feel free to open an issue on GitHub!

🚀 Happy analyzing!
