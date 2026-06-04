#!/usr/bin/env python3
"""Statistical module for calculating microbial community alpha and beta diversities.

This module provides industry-standard ecological metrics including Shannon Index,
Pielou's Evenness, and Chao1 Richness for alpha diversity, alongside rarefaction-backed
Bray-Curtis and Jaccard distance metrics for beta diversity analysis.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Optional, Sequence

import numpy as np
import pandas as pd
import typer
from scipy.spatial.distance import pdist, squareform

from krakenparser.utils import ensure_output_dir

# Initialize module-level isolated logger
_log: logging.Logger = logging.getLogger(__name__)

# Dedicated Typer routing application instantiation
app: typer.Typer = typer.Typer(
    name="diversity",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def shannon_index(counts: np.ndarray | Sequence[float] | Sequence[int]) -> float:
    """Calculate the Shannon-Wiener diversity index (H') for a count vector.

    The index is computed using the formula: H' = -sum(p_i * ln(p_i)),
    where p_i is the relative abundance of each present taxon.

    Args:
        counts: A sequence or array of absolute taxonomic abundance counts.

    Returns:
        float: The calculated Shannon diversity index.
    """
    counts_arr: np.ndarray = np.array(counts)
    nonzero_counts: np.ndarray = counts_arr[counts_arr > 0]

    if nonzero_counts.size == 0:
        return 0.0

    proportions: np.ndarray = nonzero_counts / nonzero_counts.sum()
    return float(-np.sum(proportions * np.log(proportions)))


def pielou_evenness(counts: np.ndarray | Sequence[float] | Sequence[int]) -> float:
    """Calculate Pielou's Evenness index (J') for a count vector.

    The index is computed as: J' = H' / ln(S), where H' is the Shannon index
    and S is the total number of observed species (richness).

    Args:
        counts: A sequence or array of absolute taxonomic abundance counts.

    Returns:
        float: Pielou's evenness value, or np.nan if species richness <= 1.
    """
    counts_arr: np.ndarray = np.asarray(counts)
    species_richness: int = int(np.sum(counts_arr > 0))

    if species_richness <= 1:
        return float(np.nan)

    return shannon_index(counts_arr) / float(np.log(species_richness))


def chao1_index(counts: np.ndarray | Sequence[float] | Sequence[int]) -> float:
    """Calculate the Chao1 non-parametric richness estimator for a community.

    Accounts for rare unsampled species based on singletons (F1) and doubletons (F2).
    Formula: S_chao1 = S_obs + (F1 * (F1 - 1)) / (2 * (F2 + 1)) if F2 == 0
    else S_obs + (F1^2) / (2 * F2).

    Args:
        counts: A sequence or array of absolute taxonomic abundance counts.

    Returns:
        float: The estimated total species richness.
    """
    counts_arr: np.ndarray = np.array(counts)
    species_observed: int = int(np.sum(counts_arr > 0))
    singletons: int = int(np.sum(counts_arr == 1))
    doubletons: int = int(np.sum(counts_arr == 2))

    if doubletons == 0:
        return float(species_observed + singletons * (singletons - 1) / 2)

    return float(species_observed + (singletons * singletons) / (2 * doubletons))


def _subsample_counts(
    counts: np.ndarray, n: int, rng: np.random.Generator
) -> np.ndarray:
    """Rarefy absolute abundance counts to a uniform depth without replacement.

    Args:
        counts: Array of absolute integers representing community abundances.
        n: Targeted sequencing read subsampling depth (rarefaction size).
        rng: An instantiated NumPy random generator state.

    Returns:
        np.ndarray: A new rarefied absolute abundance vector matching the source shape.
    """
    indices: np.ndarray = np.repeat(np.arange(len(counts)), counts)
    sampled: np.ndarray = rng.choice(indices, size=n, replace=False)
    return np.bincount(sampled, minlength=len(counts)).astype(int)


def calc_alpha_div(df: pd.DataFrame, output_path: Path) -> None:
    """Compute alpha diversity vectors across all profiles within a count matrix.

    Generates a structured CSV data table containing Shannon, Pielou, and Chao1
    indices mapped natively to individual sample identifiers.

    Args:
        df: Input DataFrame where indices represent samples and columns indicate taxa.
        output_path: Target directory Path where results are exported.
    """
    out_path: Path = ensure_output_dir(output_path, is_file=False)
    results: list[dict[str, Any]] = []

    for sample_id, row in df.iterrows():
        counts: np.ndarray = row.values
        results.append(
            {
                "Sample": sample_id,
                "Shannon": shannon_index(counts),
                "Pielou": pielou_evenness(counts),
                "Chao1": chao1_index(counts),
            }
        )

    alpha_df: pd.DataFrame = pd.DataFrame(results).set_index("Sample")
    alpha_df.to_csv(out_path / "alpha_div.csv")

    _log.info(
        "α-diversity has been successfully calculated and saved to '%s'.", output_path
    )


def calc_beta_div(
    df: pd.DataFrame,
    output_path: Path,
    rarefaction_depth: int,
    seed: Optional[int] = None,
) -> None:
    """Compute composition dissimilarity matrices utilizing uniform rarefied values.

    Applies absolute read-filtering limits, performs non-replacement subsampling,
    and scales community metrics via Bray-Curtis and Jaccard distance calculators.

    Args:
        df: Input DataFrame where indices represent samples and columns indicate taxa.
        output_path: Target directory Path where results are exported.
        rarefaction_depth: Integer specifying the strict depth threshold for subsampling.
        seed: Random state state-initializer utilized to force deterministic rarefaction.

    Raises:
        ValueError: Triggered if less than two samples fulfill the minimum rarefaction depth.
    """
    out_path: Path = ensure_output_dir(output_path, is_file=False)
    rng: np.random.Generator = np.random.default_rng(seed)
    rarefied_counts: list[np.ndarray] = []
    sample_ids: list[str] = []

    # Filter cohorts and compress vectors to secure computational scaling equity
    for sample, row in df.iterrows():
        counts: np.ndarray = np.round(row.values).astype(int)
        if counts.sum() >= rarefaction_depth:
            rarefied: np.ndarray = _subsample_counts(
                counts, n=rarefaction_depth, rng=rng
            )
            rarefied_counts.append(rarefied)
            sample_ids.append(str(sample))

    if len(rarefied_counts) < 2:
        raise ValueError("Not enough samples passed the rarefaction threshold.")

    matrix_x: np.ndarray = np.array(rarefied_counts, dtype=float)
    index_labels: pd.Index = pd.Index(sample_ids)

    # Calculate spatial ecological distance metrics matrices
    bray_df: pd.DataFrame = pd.DataFrame(
        squareform(pdist(matrix_x, metric="braycurtis")),
        index=index_labels,
        columns=index_labels,
    )
    jaccard_df: pd.DataFrame = pd.DataFrame(
        squareform(pdist(matrix_x.astype(bool).astype(float), metric="jaccard")),
        index=index_labels,
        columns=index_labels,
    )

    bray_df.to_csv(out_path / "beta_div_bray.csv")
    jaccard_df.to_csv(out_path / "beta_div_jaccard.csv")

    _log.info(
        "β-diversity has been successfully calculated and saved to '%s'.", output_path
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

    seed_label: str = (
        str(seed) if seed is not None else "not set (results will vary between runs)"
    )
    _log.info("Rarefaction depth: %d | seed: %s", depth, seed_label)

    if not input_file.is_file():
        print(f"Error: input file not found: {input_file}", file=sys.stderr)
        raise typer.Exit(code=1)

    output_dir.mkdir(parents=True, exist_ok=True)
    df: pd.DataFrame = pd.read_csv(input_file, index_col=0)

    try:
        calc_alpha_div(df, output_dir)
        calc_beta_div(df, output_dir, depth, seed=seed)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
