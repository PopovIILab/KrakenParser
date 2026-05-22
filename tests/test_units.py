"""Pure-function unit tests — no I/O, fully deterministic."""

import math
from pathlib import Path

import pytest

from krakenparser.counts.processing_script import modify_taxa_names
from krakenparser.counts.split_mpa import _strip_path_prefix
from krakenparser.mpa.transform2mpa import _parse_line
from krakenparser.stats.diversity import chao1_index, pielou_evenness, shannon_index
from krakenparser.utils import ensure_output_dir

# ---------------------------------------------------------------------------
# _parse_line
# ---------------------------------------------------------------------------


def test_parse_line_standard_rank():
    line = "50.00\t500000\t100000\tP\t1224\t    Pseudomonadota\n"
    name, depth, rank, cum_reads, pct = _parse_line(line)
    assert name == "Pseudomonadota"
    assert depth == 2  # 4 leading spaces // 2
    assert rank == "P"
    assert cum_reads == 500000
    assert pct == 50.0


def test_parse_line_root_no_indent():
    line = "99.98\t999980\t0\tR\t1\troot\n"
    name, depth, rank, cum_reads, pct = _parse_line(line)
    assert name == "root"
    assert depth == 0
    assert rank == "R"


def test_parse_line_intermediate_rank():
    line = "5.00\t50000\t0\tS1\t12345\t          Some subspecies\n"
    name, depth, rank, _, _ = _parse_line(line)
    assert name == "Some subspecies"
    assert rank == "S1"
    assert depth == 5  # 10 spaces // 2


def test_parse_line_too_few_columns():
    assert _parse_line("50.00\t500000\n") is None


def test_parse_line_non_numeric_pct():
    assert _parse_line("not_a_float\t500000\t0\tP\t1224\tBacteria\n") is None


def test_parse_line_non_numeric_reads():
    assert _parse_line("50.00\tnot_int\t0\tP\t1224\tBacteria\n") is None


# ---------------------------------------------------------------------------
# shannon_index
# ---------------------------------------------------------------------------


def test_shannon_uniform_four_species():
    assert abs(shannon_index([1, 1, 1, 1]) - math.log(4)) < 1e-10


def test_shannon_single_species_is_zero():
    assert shannon_index([100]) == pytest.approx(0.0)


def test_shannon_ignores_zero_counts():
    assert abs(shannon_index([1, 1, 1, 1, 0, 0]) - math.log(4)) < 1e-10


def test_shannon_two_equal_species():
    assert abs(shannon_index([50, 50]) - math.log(2)) < 1e-10


# ---------------------------------------------------------------------------
# pielou_evenness
# ---------------------------------------------------------------------------


def test_pielou_single_species_returns_nan():
    assert math.isnan(pielou_evenness([100]))


def test_pielou_all_zeros_returns_nan():
    assert math.isnan(pielou_evenness([0, 0, 0]))


def test_pielou_uniform_equals_one():
    assert pielou_evenness([1, 1, 1, 1]) == pytest.approx(1.0)


def test_pielou_range_zero_to_one():
    result = pielou_evenness([10, 2, 1, 1])
    assert 0.0 < result < 1.0


# ---------------------------------------------------------------------------
# chao1_index
# ---------------------------------------------------------------------------


def test_chao1_f2_zero_uses_f1_formula():
    # F1=3, F2=0 → S_obs + F1*(F1-1)/2
    counts = [1, 1, 1, 5, 10]  # F1=3, F2=0, S_obs=5
    expected = 5 + 3 * (3 - 1) / 2  # 5 + 3 = 8
    assert chao1_index(counts) == pytest.approx(expected)


def test_chao1_normal():
    # F1=2, F2=2, S_obs=5 → S_obs + F1²/(2*F2)
    counts = [1, 1, 2, 2, 5]
    expected = 5 + (2 * 2) / (2 * 2)  # 5 + 1 = 6
    assert chao1_index(counts) == pytest.approx(expected)


def test_chao1_no_singletons():
    counts = [5, 10, 15, 20]
    # F1=0, F2=0 → uses F2==0 branch: S_obs + 0
    assert chao1_index(counts) == pytest.approx(4.0)


# ---------------------------------------------------------------------------
# modify_taxa_names
# ---------------------------------------------------------------------------


def test_modify_taxa_names_strips_prefix_and_replaces_underscores():
    assert modify_taxa_names("s__Homo_sapiens\t100\t200") == "Homo sapiens\t100\t200"


def test_modify_taxa_names_genus():
    assert modify_taxa_names("g__Escherichia_coli\t50") == "Escherichia coli\t50"


def test_modify_taxa_names_all_prefixes():
    for prefix in ["s__", "g__", "f__", "o__", "c__", "p__"]:
        result = modify_taxa_names(f"{prefix}Some_name\t10")
        assert result == "Some name\t10"


def test_modify_taxa_names_no_prefix_unchanged():
    line = "unclassified_reads\t100"
    assert modify_taxa_names(line) == line


def test_modify_taxa_names_count_fields_not_modified():
    # Underscores in tab-separated count fields must be preserved
    result = modify_taxa_names("s__My_taxon\t1_000\t2_000")
    assert result == "My taxon\t1_000\t2_000"


# ---------------------------------------------------------------------------
# _strip_path_prefix
# ---------------------------------------------------------------------------


def test_strip_path_prefix_tab_less_line():
    assert _strip_path_prefix("no_tab_here") == "no_tab_here"


def test_strip_path_prefix_normal():
    assert (
        _strip_path_prefix("d__Bacteria|s__E_coli\t100\t200") == "s__E_coli\t100\t200"
    )


# ---------------------------------------------------------------------------
# ensure_output_dir
# ---------------------------------------------------------------------------


def test_ensure_output_dir_file_creates_parent(tmp_path):
    p = ensure_output_dir(tmp_path / "subdir" / "output.csv", is_file=True)
    assert (tmp_path / "subdir").is_dir()
    assert not p.exists()  # only the parent is created, not the file itself


def test_ensure_output_dir_dir_creates_directory(tmp_path):
    p = ensure_output_dir(tmp_path / "output_dir", is_file=False)
    assert p.is_dir()


def test_ensure_output_dir_nested_creates_all_parents(tmp_path):
    p = ensure_output_dir(tmp_path / "a" / "b" / "c", is_file=False)
    assert p.is_dir()


def test_ensure_output_dir_returns_path_object(tmp_path):
    p = ensure_output_dir(str(tmp_path / "out.csv"), is_file=True)
    assert isinstance(p, Path)


def test_ensure_output_dir_idempotent_for_existing_dir(tmp_path):
    existing = tmp_path / "already_exists"
    existing.mkdir()
    p = ensure_output_dir(existing, is_file=False)
    assert p == existing
    assert p.is_dir()
