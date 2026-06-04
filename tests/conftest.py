"""Shared pytest fixtures and sample data for the krakenparser test suite.

Fixture hierarchy
-----------------
conftest.py          ← file objects, DataFrames, CLI runner  (all tests)
test_units.py        ← pure-function tests, no I/O
test_cli.py          ← Typer CliRunner smoke / error-path tests
test_integration.py  ← library-function I/O + reproducibility tests
test_kpplot.py       ← plotting smoke + parameter-validation tests
test_full_pipeline.py← end-to-end pipeline tests (requires demo_data.zip)
"""

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest
from typer.testing import CliRunner

# ---------------------------------------------------------------------------
# Raw sample data — module-level constants shared across test files
# ---------------------------------------------------------------------------

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

# MPA-format single-sample files used across CLI and integration tests
SAMPLE_MPA_A = "#Classification\tsample1\nd__Bacteria|s__Pseudomonas_aeruginosa\t300\n"
SAMPLE_MPA_B = "#Classification\tsample2\nd__Bacteria|s__Pseudomonas_aeruginosa\t100\n"


# ---------------------------------------------------------------------------
# File-based fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def kreport_file(tmp_path):
    """A single valid Kraken2 report file covering common ranks."""
    f = tmp_path / "sample.kreport"
    f.write_text(SAMPLE_KREPORT)
    return f


@pytest.fixture
def counts_txt_file(tmp_path):
    """Tab-delimited counts file as produced by processing_script.py."""
    f = tmp_path / "counts_species.txt"
    f.write_text(SAMPLE_COUNTS_TXT)
    return f


@pytest.fixture
def counts_csv_file(tmp_path):
    """Wide-format CSV with Sample_id index column and per-taxon count columns."""
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


# ---------------------------------------------------------------------------
# DataFrame fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def relabund_df():
    """Long-format relative-abundance DataFrame with two samples and three taxa."""
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


@pytest.fixture
def two_sample_metadata():
    """Minimal metadata DataFrame mapping S1→TypeA and S2→TypeB."""
    return pd.DataFrame({"Sample_id": ["S1", "S2"], "Group": ["TypeA", "TypeB"]})


# ---------------------------------------------------------------------------
# CLI runner
# ---------------------------------------------------------------------------


@pytest.fixture
def runner():
    """Typer CliRunner instance, shared by all CLI smoke tests."""
    return CliRunner()
