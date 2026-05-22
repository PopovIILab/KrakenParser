"""Characterization / integration tests — file I/O, reproducibility."""

import hashlib
import itertools

import pandas as pd
import pytest

from krakenparser.counts.convert2csv import convert_to_csv
from krakenparser.counts.processing_script import process_files
from krakenparser.counts.split_mpa import split_mpa
from krakenparser.mpa.mpa_table import combine_mpa
from krakenparser.mpa.transform2mpa import kreport_to_mpa
from krakenparser.pipeline import _is_processable
from krakenparser.stats.diversity import calc_alpha_div, calc_beta_div
from krakenparser.stats.relabund import calculate_rel_abund

SAMPLE_COMBINED_MPA = (
    "#Classification\tsample1\tsample2\n"
    "d__Bacteria|p__Pseudomonadota|g__Pseudomonas|s__Pseudomonas_aeruginosa\t300\t100\n"
    "d__Bacteria|p__Pseudomonadota|g__Pseudomonas\t500\t200\n"
    "d__Bacteria|p__Pseudomonadota|g__Homo|s__Homo_sapiens\t50\t30\n"
    "d__Bacteria|p__Pseudomonadota|g__Homo\t60\t35\n"
    "d__Bacteria|p__Pseudomonadota\t850\t350\n"
    "d__Bacteria|p__Bacteroidota\t100\t80\n"
    "d__Viruses|p__Uroviricota|s__Virus_alpha\t10\t5\n"
)


@pytest.fixture
def combined_mpa_file(tmp_path):
    f = tmp_path / "COMBINED.txt"
    f.write_text(SAMPLE_COMBINED_MPA)
    return f


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# kreport_to_mpa
# ---------------------------------------------------------------------------


def test_kreport_to_mpa_reproducible(kreport_file, tmp_path):
    counter = itertools.count()

    def run():
        out = tmp_path / f"out_{next(counter)}.MPA.TXT"
        kreport_to_mpa(str(kreport_file), str(out), display_header=True)
        return _sha256(out)

    assert run() == run()


def test_kreport_to_mpa_standard_ranks_only(kreport_file, tmp_path):
    out = tmp_path / "out.MPA.TXT"
    kreport_to_mpa(str(kreport_file), str(out))
    lines = out.read_text().splitlines()
    paths = [ln.split("\t")[0] for ln in lines]

    assert any("p__Pseudomonadota" in p for p in paths)
    assert any("s__Pseudomonas_aeruginosa" in p for p in paths)
    assert any(p.startswith("d__Bacteria|") for p in paths)


def test_kreport_to_mpa_excludes_unclassified_and_root(kreport_file, tmp_path):
    out = tmp_path / "out.MPA.TXT"
    kreport_to_mpa(str(kreport_file), str(out))
    content = out.read_text()
    assert "unclassified" not in content
    assert "root" not in content


def test_kreport_to_mpa_display_header(kreport_file, tmp_path):
    out = tmp_path / "out.MPA.TXT"
    kreport_to_mpa(str(kreport_file), str(out), display_header=True)
    first_line = out.read_text().splitlines()[0]
    assert first_line.startswith("#Classification")
    assert kreport_file.name in first_line


def test_kreport_to_mpa_paths_are_hierarchical(kreport_file, tmp_path):
    out = tmp_path / "out.MPA.TXT"
    kreport_to_mpa(str(kreport_file), str(out))
    lines = out.read_text().splitlines()
    for ln in lines:
        path = ln.split("\t")[0]
        segments = path.split("|")
        # Each segment must have a known two-letter prefix
        for seg in segments:
            assert "__" in seg, f"Unexpected MPA segment format: {seg!r}"


# ---------------------------------------------------------------------------
# convert_to_csv
# ---------------------------------------------------------------------------


def test_convert_to_csv_reproducible(counts_txt_file, tmp_path):
    counter = itertools.count()

    def run():
        out = tmp_path / f"out_{next(counter)}.csv"
        convert_to_csv(str(counts_txt_file), str(out))
        return _sha256(out)

    assert run() == run()


def test_convert_to_csv_transposes_correctly(counts_txt_file, tmp_path):
    out = tmp_path / "counts.csv"
    convert_to_csv(str(counts_txt_file), str(out))
    df = pd.read_csv(out)

    assert "Sample_id" in df.columns
    assert set(df["Sample_id"]) == {"sample1", "sample2"}
    assert "Pseudomonas aeruginosa" in df.columns


# ---------------------------------------------------------------------------
# process_files
# ---------------------------------------------------------------------------


def test_process_files_adds_header_and_cleans_names(tmp_path):
    source = tmp_path / "COMBINED.txt"
    source.write_text(
        "#Classification\tsample1.kreport\tsample2.kreport\n"
        "d__Bacteria|p__X|s__Pseudomonas_aeruginosa\t300\t100\n"
    )
    dest = tmp_path / "counts_species.txt"
    dest.write_text(
        "s__Pseudomonas_aeruginosa\t300\t100\ns__Escherichia_coli\t200\t50\n"
    )
    process_files(str(source), str(dest))
    result = dest.read_text()
    lines = result.splitlines()
    assert lines[0] == "#Classification\tsample1\tsample2"
    assert "Pseudomonas aeruginosa" in result
    assert "Escherichia coli" in result
    assert "s__" not in result


def test_process_files_reproducible(tmp_path):
    source = tmp_path / "COMBINED.txt"
    source.write_text("#Classification\tsample1.kreport\n")
    for i in range(2):
        dest = tmp_path / f"counts_{i}.txt"
        dest.write_text("s__Some_species\t10\n")
        process_files(str(source), str(dest))
    assert (tmp_path / "counts_0.txt").read_text() == (
        tmp_path / "counts_1.txt"
    ).read_text()


def test_process_files_missing_source_raises(tmp_path):
    dest = tmp_path / "counts.txt"
    dest.write_text("s__X\t10\n")
    with pytest.raises(FileNotFoundError):
        process_files(str(tmp_path / "ghost.txt"), str(dest))


def test_process_files_missing_dest_raises(tmp_path):
    source = tmp_path / "COMBINED.txt"
    source.write_text("#Classification\tsample1.kreport\n")
    with pytest.raises(FileNotFoundError):
        process_files(str(source), str(tmp_path / "ghost.txt"))


def test_convert_to_csv_missing_input_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        convert_to_csv(str(tmp_path / "ghost.txt"), str(tmp_path / "out.csv"))


# ---------------------------------------------------------------------------
# calculate_rel_abund
# ---------------------------------------------------------------------------


def test_relabund_reproducible(counts_csv_file, tmp_path):
    counter = itertools.count()

    def run():
        out = tmp_path / f"ra_{next(counter)}.csv"
        calculate_rel_abund(str(counts_csv_file), str(out))
        return _sha256(out)

    assert run() == run()


def test_relabund_sums_to_100_per_sample(counts_csv_file, tmp_path):
    out = tmp_path / "ra.csv"
    calculate_rel_abund(str(counts_csv_file), str(out))
    df = pd.read_csv(out)
    for sample, grp in df.groupby("Sample_id"):
        total = grp["rel_abund_perc"].sum()
        assert total == pytest.approx(100.0, abs=1e-6), f"{sample}: sum={total}"


def test_relabund_other_threshold_creates_other_group(counts_csv_file, tmp_path):
    out = tmp_path / "ra.csv"
    calculate_rel_abund(str(counts_csv_file), str(out), other_threshold=99.0)
    df = pd.read_csv(out)
    assert df["taxon"].str.startswith("Other").any()


def test_relabund_no_zero_rows(counts_csv_file, tmp_path):
    out = tmp_path / "ra.csv"
    calculate_rel_abund(str(counts_csv_file), str(out))
    df = pd.read_csv(out)
    assert (df["rel_abund_perc"] > 0).all()


def test_relabund_missing_input_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        calculate_rel_abund(str(tmp_path / "ghost.csv"), str(tmp_path / "out.csv"))


# ---------------------------------------------------------------------------
# calc_alpha_div
# ---------------------------------------------------------------------------


def test_alpha_div_reproducible(counts_csv_file, tmp_path):
    df = pd.read_csv(counts_csv_file, index_col=0)
    counter = itertools.count()

    def run():
        out_dir = tmp_path / f"div_{next(counter)}"
        out_dir.mkdir()
        calc_alpha_div(df, out_dir)
        return _sha256(out_dir / "alpha_div.csv")

    assert run() == run()


def test_alpha_div_output_columns(counts_csv_file, tmp_path):
    df = pd.read_csv(counts_csv_file, index_col=0)
    out_dir = tmp_path / "diversity"
    out_dir.mkdir()
    calc_alpha_div(df, out_dir)
    result = pd.read_csv(out_dir / "alpha_div.csv")
    assert set(result.columns) == {"Sample", "Shannon", "Pielou", "Chao1"}
    assert len(result) == len(df)


def test_alpha_div_shannon_non_negative(counts_csv_file, tmp_path):
    df = pd.read_csv(counts_csv_file, index_col=0)
    out_dir = tmp_path / "diversity"
    out_dir.mkdir()
    calc_alpha_div(df, out_dir)
    result = pd.read_csv(out_dir / "alpha_div.csv")
    assert (result["Shannon"] >= 0).all()


# ---------------------------------------------------------------------------
# calc_beta_div
# ---------------------------------------------------------------------------


def test_beta_div_output_files_exist(counts_csv_file, tmp_path):
    df = pd.read_csv(counts_csv_file, index_col=0)
    out_dir = tmp_path / "diversity"
    out_dir.mkdir()
    calc_beta_div(df, out_dir, rarefaction_depth=1000)
    assert (out_dir / "beta_div_bray.csv").exists()
    assert (out_dir / "beta_div_jaccard.csv").exists()


def test_beta_div_matrix_is_square(counts_csv_file, tmp_path):
    df = pd.read_csv(counts_csv_file, index_col=0)
    out_dir = tmp_path / "diversity"
    out_dir.mkdir()
    calc_beta_div(df, out_dir, rarefaction_depth=1000)
    bray = pd.read_csv(out_dir / "beta_div_bray.csv", index_col=0)
    assert bray.shape[0] == bray.shape[1]


def test_beta_div_diagonal_is_zero(counts_csv_file, tmp_path):
    df = pd.read_csv(counts_csv_file, index_col=0)
    out_dir = tmp_path / "diversity"
    out_dir.mkdir()
    calc_beta_div(df, out_dir, rarefaction_depth=1000)
    bray = pd.read_csv(out_dir / "beta_div_bray.csv", index_col=0)
    import numpy as np

    assert np.allclose(np.diag(bray.values), 0.0)


def test_beta_div_too_few_samples_raises(tmp_path):
    df = pd.DataFrame({"Taxon_A": [100], "Taxon_B": [200]}, index=["S1"])
    out_dir = tmp_path / "diversity"
    out_dir.mkdir()
    with pytest.raises(ValueError, match="rarefaction"):
        calc_beta_div(df, out_dir, rarefaction_depth=1000)


# ---------------------------------------------------------------------------
# split_mpa
# ---------------------------------------------------------------------------


def test_split_mpa_creates_all_rank_files(combined_mpa_file, tmp_path):
    split_mpa(str(combined_mpa_file), str(tmp_path))
    for rank in ("species", "genus", "family", "order", "class", "phylum"):
        assert (tmp_path / "txt" / f"counts_{rank}.txt").exists()


def test_split_mpa_reproducible(combined_mpa_file, tmp_path):
    counter = itertools.count()

    def run():
        out = tmp_path / f"out_{next(counter)}"
        split_mpa(str(combined_mpa_file), str(out))
        return _sha256(out / "txt" / "counts_species.txt")

    assert run() == run()


def test_split_mpa_filters_human_by_default(combined_mpa_file, tmp_path):
    split_mpa(str(combined_mpa_file), str(tmp_path))
    species = (tmp_path / "txt" / "counts_species.txt").read_text()
    assert "Homo_sapiens" not in species
    genus = (tmp_path / "txt" / "counts_genus.txt").read_text()
    assert "g__Homo" not in genus


def test_split_mpa_keep_human_retains_homo(combined_mpa_file, tmp_path):
    split_mpa(str(combined_mpa_file), str(tmp_path), keep_human=True)
    species = (tmp_path / "txt" / "counts_species.txt").read_text()
    assert "Homo_sapiens" in species


def test_split_mpa_viruses_only(combined_mpa_file, tmp_path):
    split_mpa(str(combined_mpa_file), str(tmp_path), viruses_only=True)
    species = (tmp_path / "txt" / "counts_species.txt").read_text()
    assert "Virus_alpha" in species
    assert "Pseudomonas_aeruginosa" not in species


def test_split_mpa_strips_path_prefix(combined_mpa_file, tmp_path):
    split_mpa(str(combined_mpa_file), str(tmp_path))
    species = (tmp_path / "txt" / "counts_species.txt").read_text()
    # No MPA path separators should remain
    assert "|" not in species
    # The rank prefix should remain (processing_script strips it later)
    assert "s__" in species


def test_split_mpa_genus_excludes_species_lines(combined_mpa_file, tmp_path):
    split_mpa(str(combined_mpa_file), str(tmp_path))
    genus = (tmp_path / "txt" / "counts_genus.txt").read_text()
    assert "s__" not in genus


def test_split_mpa_missing_input_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        split_mpa(str(tmp_path / "ghost.txt"), str(tmp_path / "out"))


# ---------------------------------------------------------------------------
# auto-create output directories (ensure_output_dir behaviour)
# ---------------------------------------------------------------------------


def test_kreport_to_mpa_creates_output_dir(kreport_file, tmp_path):
    out = tmp_path / "new_subdir" / "out.MPA.TXT"
    kreport_to_mpa(str(kreport_file), str(out))
    assert out.exists()


def test_kreport_to_mpa_missing_input_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        kreport_to_mpa(str(tmp_path / "ghost.kreport"), str(tmp_path / "out.MPA.TXT"))


def test_convert_to_csv_creates_output_dir(counts_txt_file, tmp_path):
    out = tmp_path / "new_subdir" / "counts.csv"
    convert_to_csv(str(counts_txt_file), str(out))
    assert out.exists()


def test_relabund_creates_output_dir(counts_csv_file, tmp_path):
    out = tmp_path / "new_subdir" / "ra.csv"
    calculate_rel_abund(str(counts_csv_file), str(out))
    assert out.exists()


def test_alpha_div_creates_output_dir(counts_csv_file, tmp_path):
    df = pd.read_csv(counts_csv_file, index_col=0)
    out_dir = tmp_path / "new_dir" / "nested"
    calc_alpha_div(df, out_dir)
    assert (out_dir / "alpha_div.csv").exists()


def test_beta_div_creates_output_dir(counts_csv_file, tmp_path):
    df = pd.read_csv(counts_csv_file, index_col=0)
    out_dir = tmp_path / "new_dir" / "nested"
    calc_beta_div(df, out_dir, rarefaction_depth=1000, seed=42)
    assert (out_dir / "beta_div_bray.csv").exists()


# ---------------------------------------------------------------------------
# combine_mpa — new input validation
# ---------------------------------------------------------------------------

SAMPLE_MPA_A = "#Classification\tsample1\nd__Bacteria|s__Pseudomonas_aeruginosa\t300\n"
SAMPLE_MPA_B = "#Classification\tsample2\nd__Bacteria|s__Pseudomonas_aeruginosa\t100\n"


def test_combine_mpa_creates_output_dir(tmp_path):
    a = tmp_path / "a.MPA.TXT"
    b = tmp_path / "b.MPA.TXT"
    a.write_text(SAMPLE_MPA_A)
    b.write_text(SAMPLE_MPA_B)
    out = tmp_path / "new_subdir" / "COMBINED.txt"
    combine_mpa([str(a), str(b)], str(out))
    assert out.exists()


def test_combine_mpa_missing_input_raises(tmp_path):
    existing = tmp_path / "a.MPA.TXT"
    existing.write_text(SAMPLE_MPA_A)
    with pytest.raises(FileNotFoundError):
        combine_mpa([str(existing), str(tmp_path / "ghost.MPA.TXT")], str(tmp_path / "out.txt"))


# ---------------------------------------------------------------------------
# process_files — destination must already exist (in-place modifier)
# ---------------------------------------------------------------------------


def test_process_files_missing_dest_still_raises(tmp_path):
    source = tmp_path / "COMBINED.txt"
    source.write_text("#Classification\tsample1.kreport\n")
    with pytest.raises(FileNotFoundError):
        process_files(str(source), str(tmp_path / "nonexistent.txt"))


# ---------------------------------------------------------------------------
# split_mpa — t__ rank filter (intermediate terminal nodes)
# ---------------------------------------------------------------------------


def test_split_mpa_filters_terminal_rank_nodes(tmp_path):
    combined = tmp_path / "COMBINED.txt"
    combined.write_text(
        "#Classification\tsample1\n"
        "d__Bacteria|p__Pseudomonadota|s__Pseudomonas_aeruginosa\t300\n"
        "d__Bacteria|p__Pseudomonadota|s__Pseudomonas_aeruginosa|t__strain_X\t10\n"
    )
    split_mpa(str(combined), str(tmp_path / "out"))
    species = (tmp_path / "out" / "txt" / "counts_species.txt").read_text()
    assert "t__" not in species


# ---------------------------------------------------------------------------
# _is_processable — hidden files, null bytes, non-UTF-8
# ---------------------------------------------------------------------------


def test_is_processable_hidden_file(tmp_path):
    f = tmp_path / ".hidden"
    f.write_text("content")
    assert not _is_processable(f)


def test_is_processable_null_bytes(tmp_path):
    f = tmp_path / "binary.bin"
    f.write_bytes(b"hello\x00world")
    assert not _is_processable(f)


def test_is_processable_non_utf8(tmp_path):
    f = tmp_path / "latin1.txt"
    f.write_bytes(b"\xff\xfe bad encoding")
    assert not _is_processable(f)


def test_is_processable_valid_kreport(tmp_path):
    f = tmp_path / "sample.kreport"
    f.write_text("50.0\t500\t100\tS\t1\tBacteria\n")
    assert _is_processable(f)
