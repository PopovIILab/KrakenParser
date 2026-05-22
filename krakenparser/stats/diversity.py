#!/usr/bin/env python

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform

from krakenparser.utils import ensure_output_dir

_log = logging.getLogger(__name__)


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


def calc_alpha_div(df, output_path):
    out_path = ensure_output_dir(output_path, is_file=False)
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


def calc_beta_div(df, output_path, rarefaction_depth, seed=None):
    out_path = ensure_output_dir(output_path, is_file=False)
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


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="Calculate α & β-diversities.")
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input total count table CSV (species level).",
    )
    parser.add_argument("-o", "--output", required=True, help="Output directory path.")
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=1000,
        help="Rarefaction depth for β diversity (default: 1000).",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible rarefaction (default: random).",
    )
    args = parser.parse_args()

    seed_label = str(args.seed) if args.seed is not None else "not set (results will vary between runs)"
    _log.info("Rarefaction depth: %d | seed: %s", args.depth, seed_label)

    input_file = Path(args.input)
    if not input_file.is_file():
        sys.exit(f"Error: input file not found: {input_file}")
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_file, index_col=0)

    calc_alpha_div(df, output_dir)
    calc_beta_div(df, output_dir, args.depth, seed=args.seed)


if __name__ == "__main__":
    main()
