"""Smoke tests for CLI entry-points via Typer CliRunner."""

import shutil

import pandas as pd
import pytest
from typer.testing import CliRunner

from krakenparser.counts.convert2csv import app as convert2csv_app
from krakenparser.counts.processing_script import app as processing_app
from krakenparser.counts.split_mpa import app as split_mpa_app
from krakenparser.mpa.mpa_table import app as mpa_table_app
from krakenparser.mpa.transform2mpa import app as transform2mpa_app
from krakenparser.pipeline import app as pipeline_app
from krakenparser.stats.diversity import app as diversity_app
from krakenparser.stats.relabund import app as relabund_app

_MPA_A = "#Classification\tsample1\nd__Bacteria|s__Pseudomonas_aeruginosa\t300\n"
_MPA_B = "#Classification\tsample2\nd__Bacteria|s__Pseudomonas_aeruginosa\t100\n"

_COMBINED_MPA = (
    "#Classification\tsample1\tsample2\n"
    "d__Bacteria|p__Pseudomonadota|g__Pseudomonas|s__Pseudomonas_aeruginosa\t300\t100\n"
    "d__Bacteria|p__Bacteroidota\t100\t80\n"
)


@pytest.fixture
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# convert2csv
# ---------------------------------------------------------------------------


def test_convert2csv_no_args_shows_help(runner):
    result = runner.invoke(convert2csv_app, [])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_convert2csv_missing_one_option(runner, tmp_path):
    result = runner.invoke(convert2csv_app, ["-i", str(tmp_path / "x.txt")])
    assert result.exit_code == 1
    assert "Missing required options" in result.output


def test_convert2csv_file_not_found(runner, tmp_path):
    result = runner.invoke(
        convert2csv_app,
        ["-i", str(tmp_path / "ghost.txt"), "-o", str(tmp_path / "out.csv")],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


# ---------------------------------------------------------------------------
# processing_script
# ---------------------------------------------------------------------------


def test_processing_no_args_shows_help(runner):
    result = runner.invoke(processing_app, [])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_processing_missing_one_option(runner, tmp_path):
    result = runner.invoke(processing_app, ["-i", str(tmp_path / "x.txt")])
    assert result.exit_code == 1
    assert "Missing required options" in result.output


def test_processing_file_not_found(runner, tmp_path):
    result = runner.invoke(
        processing_app,
        ["-i", str(tmp_path / "ghost.txt"), "-o", str(tmp_path / "dest.txt")],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


# ---------------------------------------------------------------------------
# split_mpa
# ---------------------------------------------------------------------------


def test_split_mpa_no_args_shows_help(runner):
    result = runner.invoke(split_mpa_app, [])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_split_mpa_missing_one_option(runner, tmp_path):
    result = runner.invoke(split_mpa_app, ["-i", str(tmp_path / "x.txt")])
    assert result.exit_code == 1
    assert "Missing required options" in result.output


def test_split_mpa_file_not_found(runner, tmp_path):
    result = runner.invoke(
        split_mpa_app,
        ["-i", str(tmp_path / "ghost.txt"), "-o", str(tmp_path / "out")],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


# ---------------------------------------------------------------------------
# mpa_table
# ---------------------------------------------------------------------------


def test_mpa_table_main(tmp_path, runner):
    a, b = tmp_path / "a.MPA.TXT", tmp_path / "b.MPA.TXT"
    a.write_text(_MPA_A)
    b.write_text(_MPA_B)
    out = tmp_path / "COMBINED.txt"

    result = runner.invoke(mpa_table_app, ["-i", str(a), "-i", str(b), "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()


# ---------------------------------------------------------------------------
# transform2mpa
# ---------------------------------------------------------------------------


def test_transform2mpa_main_single(kreport_file, tmp_path, runner):
    out = tmp_path / "out.MPA.TXT"
    result = runner.invoke(transform2mpa_app, ["-r", str(kreport_file), "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_transform2mpa_main_batch(kreport_file, tmp_path, runner):
    kreports_dir = tmp_path / "kreports"
    kreports_dir.mkdir()
    shutil.copy(kreport_file, kreports_dir / kreport_file.name)
    out_dir = tmp_path / "mpa_out"

    result = runner.invoke(
        transform2mpa_app, ["-i", str(kreports_dir), "-o", str(out_dir)]
    )
    assert result.exit_code == 0
    assert out_dir.is_dir()


# ---------------------------------------------------------------------------
# diversity
# ---------------------------------------------------------------------------


def test_diversity_no_args_shows_help(runner):
    result = runner.invoke(diversity_app, [])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_diversity_missing_one_option(runner, tmp_path):
    result = runner.invoke(diversity_app, ["-o", str(tmp_path / "out")])
    assert result.exit_code == 1
    assert "Missing required options" in result.output


def test_diversity_file_not_found(runner, tmp_path):
    result = runner.invoke(
        diversity_app,
        ["-i", str(tmp_path / "ghost.csv"), "-o", str(tmp_path / "out")],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_diversity_not_enough_samples_for_beta(runner, tmp_path):
    csv_in = tmp_path / "single.csv"
    pd.DataFrame({"Taxon_A": [100], "Taxon_B": [200]}, index=["S1"]).to_csv(csv_in)
    out_dir = tmp_path / "div"
    result = runner.invoke(
        diversity_app,
        ["-i", str(csv_in), "-o", str(out_dir), "-d", "50"],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


# ---------------------------------------------------------------------------
# relabund
# ---------------------------------------------------------------------------


def test_relabund_no_args_shows_help(runner):
    result = runner.invoke(relabund_app, [])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_relabund_missing_one_option(runner, tmp_path):
    result = runner.invoke(relabund_app, ["-i", str(tmp_path / "x.csv")])
    assert result.exit_code == 1
    assert "Missing required options" in result.output


def test_relabund_file_not_found(runner, tmp_path):
    result = runner.invoke(
        relabund_app,
        ["-i", str(tmp_path / "ghost.csv"), "-o", str(tmp_path / "out.csv")],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


# ---------------------------------------------------------------------------
# pipeline (error paths only — success path covered by test_full_pipeline.py)
# ---------------------------------------------------------------------------


def test_pipeline_no_mpa_files(runner, tmp_path):
    empty_dir = tmp_path / "kreports"
    empty_dir.mkdir()
    result = runner.invoke(pipeline_app, ["-i", str(empty_dir)])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_pipeline_file_exists_error(runner, tmp_path, kreport_file):
    kreports_dir = tmp_path / "kreports"
    kreports_dir.mkdir()
    shutil.copy(kreport_file, kreports_dir / kreport_file.name)

    runner.invoke(pipeline_app, ["-i", str(kreports_dir), "--overwrite"])

    result = runner.invoke(pipeline_app, ["-i", str(kreports_dir)])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_pipeline_missing_input_dir(runner, tmp_path):
    result = runner.invoke(pipeline_app, ["-i", str(tmp_path / "ghost")])
    assert result.exit_code == 1
    assert "Error" in result.output
