"""Smoke tests for CLI entry-points via Typer CliRunner.

Each command is exercised for three standard error paths:
  1. No arguments → usage help (exit 0).
  2. Missing one required option → validation error (exit 1).
  3. Non-existent input file → runtime error (exit 1).

Happy paths for commands that produce file output are covered separately in
test_integration.py and test_full_pipeline.py.
"""

import shutil

import pandas as pd
import pytest
from conftest import SAMPLE_MPA_A, SAMPLE_MPA_B

from krakenparser.counts.convert2csv import app as convert2csv_app
from krakenparser.counts.processing_script import app as processing_app
from krakenparser.counts.split_mpa import app as split_mpa_app
from krakenparser.mpa.mpa_table import app as mpa_table_app
from krakenparser.mpa.transform2mpa import app as transform2mpa_app
from krakenparser.pipeline import app as pipeline_app
from krakenparser.stats.diversity import app as diversity_app
from krakenparser.stats.relabund import app as relabund_app

_COMBINED_MPA = (
    "#Classification\tsample1\tsample2\n"
    "d__Bacteria|p__Pseudomonadota|g__Pseudomonas|s__Pseudomonas_aeruginosa\t300\t100\n"
    "d__Bacteria|p__Bacteroidota\t100\t80\n"
)


# ---------------------------------------------------------------------------
# Parametrized standard error-path suite
# ---------------------------------------------------------------------------

# Each tuple: (app, no-arg exit code, partial-args list, file-not-found args factory)
# The factory is a callable(tmp_path) → list[str].
_CLI_SPECS = [
    (
        convert2csv_app,
        ["-i", "{{ghost}}"],
        ["-i", "{{ghost}}", "-o", "{{out}}"],
    ),
    (
        processing_app,
        ["-i", "{{ghost}}"],
        ["-i", "{{ghost}}", "-o", "{{dest}}"],
    ),
    (
        split_mpa_app,
        ["-i", "{{ghost}}"],
        ["-i", "{{ghost}}", "-o", "{{out}}"],
    ),
    (
        diversity_app,
        ["-o", "{{out}}"],
        ["-i", "{{ghost}}", "-o", "{{out}}"],
    ),
    (
        relabund_app,
        ["-i", "{{ghost}}"],
        ["-i", "{{ghost}}", "-o", "{{out}}"],
    ),
]


def _resolve(args: list[str], tmp_path) -> list[str]:
    """Substitute placeholder tokens with concrete tmp_path paths."""
    mapping = {
        "{{ghost}}": str(tmp_path / "ghost.txt"),
        "{{out}}": str(tmp_path / "out.csv"),
        "{{dest}}": str(tmp_path / "dest.txt"),
    }
    return [mapping.get(a, a) for a in args]


@pytest.mark.parametrize("app,_,__", _CLI_SPECS)
def test_no_args_shows_help(app, _, __, runner):
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage" in result.output


@pytest.mark.parametrize("app,partial_args,__", _CLI_SPECS)
def test_missing_required_option(app, partial_args, __, runner, tmp_path):
    result = runner.invoke(app, _resolve(partial_args, tmp_path))
    assert result.exit_code == 1
    assert "Missing required options" in result.output


@pytest.mark.parametrize("app,_,fnf_args", _CLI_SPECS)
def test_file_not_found(app, _, fnf_args, runner, tmp_path):
    result = runner.invoke(app, _resolve(fnf_args, tmp_path))
    assert result.exit_code == 1
    assert "Error" in result.output


# ---------------------------------------------------------------------------
# mpa_table — happy path (two valid input files → combined output)
# ---------------------------------------------------------------------------


def test_mpa_table_combines_two_files(runner, tmp_path):
    a, b = tmp_path / "a.MPA.TXT", tmp_path / "b.MPA.TXT"
    a.write_text(SAMPLE_MPA_A)
    b.write_text(SAMPLE_MPA_B)
    out = tmp_path / "COMBINED.txt"

    result = runner.invoke(mpa_table_app, ["-i", str(a), "-i", str(b), "-o", str(out)])

    assert result.exit_code == 0
    assert out.exists()


# ---------------------------------------------------------------------------
# transform2mpa — single file and batch directory modes
# ---------------------------------------------------------------------------


def test_transform2mpa_single_file(kreport_file, runner, tmp_path):
    out = tmp_path / "out.MPA.TXT"
    result = runner.invoke(transform2mpa_app, ["-r", str(kreport_file), "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_transform2mpa_batch_directory(kreport_file, runner, tmp_path):
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
# pipeline CLI — error paths (success path covered by test_full_pipeline.py)
# ---------------------------------------------------------------------------


def test_pipeline_empty_kreports_dir_raises(runner, tmp_path):
    empty_dir = tmp_path / "kreports"
    empty_dir.mkdir()
    result = runner.invoke(pipeline_app, ["-i", str(empty_dir)])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_pipeline_missing_input_dir_raises(runner, tmp_path):
    result = runner.invoke(pipeline_app, ["-i", str(tmp_path / "ghost")])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_pipeline_existing_output_without_overwrite_raises(
    runner, tmp_path, kreport_file
):
    kreports_dir = tmp_path / "kreports"
    kreports_dir.mkdir()
    shutil.copy(kreport_file, kreports_dir / kreport_file.name)

    runner.invoke(pipeline_app, ["-i", str(kreports_dir), "--overwrite"])
    result = runner.invoke(pipeline_app, ["-i", str(kreports_dir)])

    assert result.exit_code == 1
    assert "Error" in result.output


# ---------------------------------------------------------------------------
# diversity — domain-specific validation
# ---------------------------------------------------------------------------


def test_diversity_not_enough_samples_for_beta(runner, tmp_path):
    csv_in = tmp_path / "single.csv"
    pd.DataFrame({"Taxon_A": [100], "Taxon_B": [200]}, index=["S1"]).to_csv(csv_in)  # ty:ignore[invalid-argument-type]
    out_dir = tmp_path / "div"

    result = runner.invoke(
        diversity_app,
        ["-i", str(csv_in), "-o", str(out_dir), "-d", "50"],
    )

    assert result.exit_code == 1
    assert "Error" in result.output
