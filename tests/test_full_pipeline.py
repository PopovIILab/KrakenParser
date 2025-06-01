import zipfile
import shutil
import subprocess
import pytest
from pathlib import Path


@pytest.fixture
def demo_run(tmp_path):
    repo_root = Path(__file__).parent.parent.resolve()
    zip_src = repo_root / "demo_data.zip"
    if not zip_src.exists():
        pytest.skip("demo_data.zip not found")

    local_zip = tmp_path / "demo_data.zip"
    shutil.copy(zip_src, local_zip)
    with zipfile.ZipFile(local_zip, "r") as z:
        z.extractall(tmp_path)

    demo_data_dir = tmp_path / "demo_data"
    run_dir = tmp_path / "demo_run"
    run_dir.mkdir()
    (demo_data_dir / "kreports").rename(run_dir / "kreports")

    return {"run_dir": run_dir}


def test_full_pipeline_end_to_end(demo_run):
    run_dir = demo_run["run_dir"]
    kreports_path = run_dir / "kreports"

    # 1. Run KrakenParser
    cmd = ["KrakenParser", "--complete", "-i", str(kreports_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Pipeline failed:\n{result.stderr}"

    # 2. Assert each rank‐level CSV exists and is non‐empty
    ranks = ["phylum", "class", "order", "family", "genus", "species"]
    for rank in ranks:
        csv_path = run_dir / "counts" / "csv" / f"counts_{rank}.csv"
        assert csv_path.exists(), f"Missing counts_{rank}.csv"
        assert csv_path.stat().st_size > 0, f"counts_{rank}.csv is empty"

    # 3. Assert relative‐abundance CSVs exist and are non‐empty
    rel_dir = run_dir / "counts" / "csv_relabund"
    assert rel_dir.exists(), "csv_relabund directory is missing"
    rel_species = rel_dir / "counts_species.csv"
    assert rel_species.exists(), "Missing counts_species.csv in csv_relabund"
    assert rel_species.stat().st_size > 0, "counts_species.csv is empty"
