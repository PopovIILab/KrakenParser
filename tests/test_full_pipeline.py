"""End-to-end pipeline tests using real demo data.

These tests exercise the full ``run_pipeline`` call stack — kreport → MPA →
counts CSV → relative abundance → diversity — and are skipped automatically
when ``demo_data.zip`` is absent from the repository root.

Execution time is dominated by I/O and rarefaction; they are intentionally
kept out of the default fast-test run and should be executed in CI via a
dedicated ``pytest -m integration`` marker (or equivalent).
"""

import shutil
import zipfile
from pathlib import Path

import pytest

from krakenparser.pipeline import run_pipeline

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def demo_run(tmp_path):
    """Unpack demo_data.zip into a fresh tmp directory and return the run dir.

    Skips the test session if the zip is not present so that the suite can
    still pass in environments that only have unit/integration data.
    """
    repo_root = Path(__file__).parent.parent.resolve()
    zip_src = repo_root / "demo_data.zip"
    if not zip_src.exists():
        pytest.skip("demo_data.zip not found — skipping end-to-end tests")

    local_zip = tmp_path / "demo_data.zip"
    shutil.copy(zip_src, local_zip)
    with zipfile.ZipFile(local_zip, "r") as z:
        z.extractall(tmp_path)

    demo_data_dir = tmp_path / "demo_data"
    run_dir = tmp_path / "demo_run"
    run_dir.mkdir()
    (demo_data_dir / "kreports").rename(run_dir / "kreports")

    return {"run_dir": run_dir}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_full_pipeline_produces_all_expected_outputs(demo_run):
    run_dir = demo_run["run_dir"]
    kreports_path = run_dir / "kreports"

    run_pipeline(kreports_path)

    # Per-rank count CSVs
    for rank in ("phylum", "class", "order", "family", "genus", "species"):
        csv_path = run_dir / "counts" / f"counts_{rank}.csv"
        assert csv_path.exists(), f"Missing counts_{rank}.csv"
        assert csv_path.stat().st_size > 0, f"counts_{rank}.csv is empty"

    # Relative-abundance outputs
    rel_dir = run_dir / "rel_abund"
    assert rel_dir.exists(), "rel_abund directory is missing"
    ra_species = rel_dir / "ra_species.csv"
    assert ra_species.exists(), "Missing ra_species.csv"
    assert ra_species.stat().st_size > 0, "ra_species.csv is empty"

    # Diversity outputs
    assert (run_dir / "diversity" / "alpha_div.csv").exists()

    # Intermediate combined MPA
    assert (run_dir / "intermediate" / "COMBINED.txt").exists()


def test_pipeline_overwrite_protection_raises_on_second_run(demo_run):
    kreports_path = demo_run["run_dir"] / "kreports"

    run_pipeline(kreports_path)

    with pytest.raises(FileExistsError):
        run_pipeline(kreports_path)


def test_pipeline_overwrite_flag_allows_second_run(demo_run):
    kreports_path = demo_run["run_dir"] / "kreports"

    run_pipeline(kreports_path)
    run_pipeline(kreports_path, overwrite=True)  # must not raise
