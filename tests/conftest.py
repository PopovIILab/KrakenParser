import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest

SAMPLE_KREPORT = (
    "99.98\t999980\t0\tR\t1\troot\n"
    "99.98\t999980\t0\tD\t2\t  Bacteria\n"
    "85.00\t850000\t0\tP\t1224\t    Pseudomonadota\n"
    "50.00\t500000\t200000\tG\t286\t      Pseudomonas\n"
    "30.00\t300000\t300000\tS\t287\t        Pseudomonas aeruginosa\n"
    "20.00\t200000\t200000\tG\t561\t      Escherichia\n"
    "20.00\t200000\t200000\tS\t562\t        Escherichia coli\n"
    "10.00\t100000\t0\tP\t976\t    Bacteroidota\n"
    "10.00\t100000\t100000\tS\t817\t      Bacteroides fragilis\n"
    "0.02\t200\t200\tU\t0\tunclassified\n"
)

# Tab-delimited TXT as produced by processing_script.py
SAMPLE_COUNTS_TXT = (
    "#Classification\tsample1\tsample2\n"
    "Pseudomonas aeruginosa\t300000\t100000\n"
    "Escherichia coli\t200000\t50000\n"
    "Bacteroides fragilis\t100000\t200000\n"
)


@pytest.fixture
def kreport_file(tmp_path):
    f = tmp_path / "sample.kreport"
    f.write_text(SAMPLE_KREPORT)
    return f


@pytest.fixture
def counts_txt_file(tmp_path):
    f = tmp_path / "counts_species.txt"
    f.write_text(SAMPLE_COUNTS_TXT)
    return f


@pytest.fixture
def counts_csv_file(tmp_path):
    df = pd.DataFrame(
        {
            "Sample_id": ["S1", "S2"],
            "Pseudomonas aeruginosa": [300000, 100000],
            "Escherichia coli": [200000, 50000],
            "Bacteroides fragilis": [100000, 200000],
        }
    )
    f = tmp_path / "counts_species.csv"
    df.to_csv(f, index=False)
    return f


@pytest.fixture
def relabund_df():
    return pd.DataFrame(
        {
            "Sample_id": ["S1", "S1", "S1", "S2", "S2", "S2"],
            "taxon": [
                "Pseudomonadota",
                "Bacillota",
                "Other (<4.0%)",
                "Pseudomonadota",
                "Bacillota",
                "Other (<4.0%)",
            ],
            "rel_abund_perc": [70.0, 20.0, 10.0, 50.0, 35.0, 15.0],
        }
    )
