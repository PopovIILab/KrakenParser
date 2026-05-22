"""Smoke tests for CLI entry-points (main() functions via sys.argv monkeypatching)."""

import shutil
import sys
import warnings

import pandas as pd
import pytest

from krakenparser.counts.convert2csv import main as convert2csv_main
from krakenparser.counts.processing_script import main as processing_main
from krakenparser.counts.split_mpa import main as split_mpa_main
from krakenparser.mpa.mpa_table import main as mpa_table_main
from krakenparser.mpa.transform2mpa import main as transform2mpa_main
from krakenparser.pipeline import main as pipeline_main
from krakenparser.stats.diversity import main as diversity_main
from krakenparser.stats.relabund import main as relabund_main

_MPA_A = "#Classification\tsample1\nd__Bacteria|s__Pseudomonas_aeruginosa\t300\n"
_MPA_B = "#Classification\tsample2\nd__Bacteria|s__Pseudomonas_aeruginosa\t100\n"

_COMBINED_MPA = (
    "#Classification\tsample1\tsample2\n"
    "d__Bacteria|p__Pseudomonadota|g__Pseudomonas|s__Pseudomonas_aeruginosa\t300\t100\n"
    "d__Bacteria|p__Bacteroidota\t100\t80\n"
)


# ---------------------------------------------------------------------------
# convert2csv
# ---------------------------------------------------------------------------


def test_convert2csv_main(counts_txt_file, tmp_path, monkeypatch):
    out = tmp_path / "out.csv"
    monkeypatch.setattr(sys, "argv", ["c2c", "-i", str(counts_txt_file), "-o", str(out)])
    convert2csv_main()
    assert out.exists()


# ---------------------------------------------------------------------------
# processing_script
# ---------------------------------------------------------------------------


def test_processing_main(tmp_path, monkeypatch):
    source = tmp_path / "COMBINED.txt"
    source.write_text("#Classification\tsample1.kreport\n")
    dest = tmp_path / "counts.txt"
    dest.write_text("s__Pseudomonas_aeruginosa\t100\n")
    monkeypatch.setattr(sys, "argv", ["ps", "-i", str(source), "-o", str(dest)])
    processing_main()


# ---------------------------------------------------------------------------
# split_mpa
# ---------------------------------------------------------------------------


def test_split_mpa_main(tmp_path, monkeypatch):
    combined = tmp_path / "COMBINED.txt"
    combined.write_text(_COMBINED_MPA)
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["sm", "-i", str(combined), "-o", str(out)])
    split_mpa_main()
    assert (out / "txt" / "counts_species.txt").exists()


def test_split_mpa_main_viruses_only(tmp_path, monkeypatch):
    combined = tmp_path / "COMBINED.txt"
    combined.write_text(_COMBINED_MPA + "d__Viruses|s__Virus_X\t5\t3\n")
    out = tmp_path / "out"
    monkeypatch.setattr(
        sys, "argv", ["sm", "-i", str(combined), "-o", str(out), "--viruses-only"]
    )
    split_mpa_main()


def test_split_mpa_main_keep_human(tmp_path, monkeypatch):
    combined = tmp_path / "COMBINED.txt"
    combined.write_text(_COMBINED_MPA)
    out = tmp_path / "out"
    monkeypatch.setattr(
        sys, "argv", ["sm", "-i", str(combined), "-o", str(out), "--keep-human"]
    )
    split_mpa_main()


# ---------------------------------------------------------------------------
# mpa_table
# ---------------------------------------------------------------------------


def test_mpa_table_main(tmp_path, monkeypatch):
    a, b = tmp_path / "a.MPA.TXT", tmp_path / "b.MPA.TXT"
    a.write_text(_MPA_A)
    b.write_text(_MPA_B)
    out = tmp_path / "COMBINED.txt"
    monkeypatch.setattr(
        sys, "argv", ["mt", "-i", str(a), str(b), "-o", str(out)]
    )
    mpa_table_main()
    assert out.exists()


# ---------------------------------------------------------------------------
# transform2mpa
# ---------------------------------------------------------------------------


def test_transform2mpa_main_single(kreport_file, tmp_path, monkeypatch):
    out = tmp_path / "out.MPA.TXT"
    monkeypatch.setattr(
        sys, "argv", ["t2m", "-r", str(kreport_file), "-o", str(out)]
    )
    transform2mpa_main()
    assert out.exists()


def test_transform2mpa_main_batch(kreport_file, tmp_path, monkeypatch):
    kreports_dir = tmp_path / "kreports"
    kreports_dir.mkdir()
    shutil.copy(kreport_file, kreports_dir / kreport_file.name)
    out_dir = tmp_path / "mpa_out"
    monkeypatch.setattr(
        sys, "argv", ["t2m", "-i", str(kreports_dir), "-o", str(out_dir)]
    )
    transform2mpa_main()
    assert out_dir.is_dir()


# ---------------------------------------------------------------------------
# diversity
# ---------------------------------------------------------------------------


def test_diversity_main_with_seed(counts_csv_file, tmp_path, monkeypatch):
    out_dir = tmp_path / "div"
    monkeypatch.setattr(
        sys,
        "argv",
        ["div", "-i", str(counts_csv_file), "-o", str(out_dir), "-d", "1000", "-s", "42"],
    )
    diversity_main()
    assert (out_dir / "alpha_div.csv").exists()


def test_diversity_main_no_seed(counts_csv_file, tmp_path, monkeypatch):
    out_dir = tmp_path / "div"
    monkeypatch.setattr(
        sys, "argv", ["div", "-i", str(counts_csv_file), "-o", str(out_dir), "-d", "1000"]
    )
    diversity_main()


# ---------------------------------------------------------------------------
# relabund
# ---------------------------------------------------------------------------


def test_relabund_main(counts_csv_file, tmp_path, monkeypatch):
    out = tmp_path / "ra.csv"
    monkeypatch.setattr(sys, "argv", ["ra", "-i", str(counts_csv_file), "-o", str(out)])
    relabund_main()
    assert out.exists()


def test_relabund_main_with_other_threshold(counts_csv_file, tmp_path, monkeypatch):
    out = tmp_path / "ra.csv"
    monkeypatch.setattr(
        sys, "argv", ["ra", "-i", str(counts_csv_file), "-o", str(out), "-O", "50"]
    )
    relabund_main()


def test_relabund_warns_zero_abundance_sample(tmp_path):
    df = pd.DataFrame(
        {"Sample_id": ["S1", "S2"], "Taxon_A": [0, 100], "Taxon_B": [0, 200]}
    )
    csv_in = tmp_path / "counts.csv"
    df.to_csv(csv_in, index=False)
    out = tmp_path / "ra.csv"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        from krakenparser.stats.relabund import calculate_rel_abund

        calculate_rel_abund(str(csv_in), str(out))
    assert any("zero total abundance" in str(w.message) for w in caught)


# ---------------------------------------------------------------------------
# pipeline (error paths only — success path covered by test_full_pipeline.py)
# ---------------------------------------------------------------------------


def test_pipeline_main_missing_input_exits(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["pipeline", "-i", str(tmp_path / "ghost")])
    with pytest.raises(SystemExit):
        pipeline_main()
