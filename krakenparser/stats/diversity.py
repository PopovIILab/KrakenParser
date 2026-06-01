#!/usr/bin/env python

import logging
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import typer
from scipy.spatial.distance import pdist, squareform

from krakenparser.utils import ensure_output_dir

_log = logging.getLogger(__name__)

app = typer.Typer(
    name="diversity",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def shannon_index(counts):
    counts = np.array(counts)
    counts = counts[counts > 0]
    proportions = counts / counts.sum()
    return -np.sum(proportions * np.log(proportions))


def pielou_evenness(counts):
    counts = np.asarray(counts)
    S = int(np.sum(counts > 0))
    if S <= 1:
        return np.nan
    return shannon_index(counts) / np.log(S)


def chao1_index(counts):
    counts = np.array(counts)
    S_obs = np.sum(counts > 0)
    F1 = np.sum(counts == 1)
    F2 = np.sum(counts == 2)
    if F2 == 0:
        return S_obs + F1 * (F1 - 1) / 2
    return S_obs + (F1 * F1) / (2 * F2)


def _subsample_counts(
    counts: np.ndarray, n: int, rng: np.random.Generator
) -> np.ndarray:
    """Rarefy counts to n reads by sampling without replacement."""
    indices = np.repeat(np.arange(len(counts)), counts)
    sampled = rng.choice(indices, size=n, replace=False)
    return np.bincount(sampled, minlength=len(counts)).astype(int)


def calc_alpha_div(df: pd.DataFrame, output_path: Path) -> None:
    out_path = ensure_output_dir(str(output_path), is_file=False)
    results = []
    for sample_id, row in df.iterrows():
        counts = row.values
        results.append(
            {
                "Sample": sample_id,
                "Shannon": shannon_index(counts),
                "Pielou": pielou_evenness(counts),
                "Chao1": chao1_index(counts),
            }
        )
    alpha_df = pd.DataFrame(results).set_index("Sample")
    alpha_df.to_csv(out_path / "alpha_div.csv")

    _log.info(
        f"α-diversity has been successfully calculated and saved to '{output_path}'."
    )


def calc_beta_div(
    df: pd.DataFrame,
    output_path: Path,
    rarefaction_depth: int,
    seed: Optional[int] = None,
) -> None:
    out_path = ensure_output_dir(str(output_path), is_file=False)
    rng = np.random.default_rng(seed)
    rarefied_counts: list[np.ndarray] = []
    sample_ids: list[str] = []

    for sample, row in df.iterrows():
        counts = np.round(row.values).astype(int)
        if counts.sum() >= rarefaction_depth:
            rarefied = _subsample_counts(counts, n=rarefaction_depth, rng=rng)
            rarefied_counts.append(rarefied)
            sample_ids.append(str(sample))

    if len(rarefied_counts) < 2:
        raise ValueError("Not enough samples passed the rarefaction threshold.")

    X = np.array(rarefied_counts, dtype=float)
    idx = pd.Index(sample_ids)

    bray_df = pd.DataFrame(
        squareform(pdist(X, metric="braycurtis")),
        index=idx,
        columns=idx,
    )
    jaccard_df = pd.DataFrame(
        squareform(pdist(X.astype(bool).astype(float), metric="jaccard")),
        index=idx,
        columns=idx,
    )

    bray_df.to_csv(out_path / "beta_div_bray.csv")
    jaccard_df.to_csv(out_path / "beta_div_jaccard.csv")

    _log.info(
        f"β-diversity has been successfully calculated and saved to '{output_path}'."
    )


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    input_file: Optional[Path] = typer.Option(
        None,
        "-i",
        "--input",
        help="Input total count table CSV (species level).",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output directory path.",
    ),
    depth: int = typer.Option(
        1000,
        "-d",
        "--depth",
        help="Rarefaction depth for β diversity.",
    ),
    seed: Optional[int] = typer.Option(
        None,
        "-s",
        "--seed",
        help="Random seed for reproducible rarefaction (default: random).",
    ),
) -> None:
    """Calculate α & β-diversities for microbial communities."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if input_file is None and output_dir is None:
        print(ctx.get_help())
        raise typer.Exit()

    if not input_file or not output_dir:
        print(
            "Error: Missing required options '-i / --input' and '-o / --output'.",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)

    seed_label = (
        str(seed) if seed is not None else "not set (results will vary between runs)"
    )
    _log.info("Rarefaction depth: %d | seed: %s", depth, seed_label)

    if not input_file.is_file():
        print(f"Error: input file not found: {input_file}", file=sys.stderr)
        raise typer.Exit(code=1)

    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(input_file, index_col=0)

    try:
        calc_alpha_div(df, output_dir)
        calc_beta_div(df, output_dir, depth, seed=seed)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
