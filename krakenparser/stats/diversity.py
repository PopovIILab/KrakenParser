#!/usr/bin/env python

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform


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


def _subsample_counts(counts: np.ndarray, n: int) -> np.ndarray:
    """Rarefy counts to n reads by sampling without replacement."""
    indices = np.repeat(np.arange(len(counts)), counts)
    sampled = np.random.choice(indices, size=n, replace=False)
    return np.bincount(sampled, minlength=len(counts)).astype(int)


def calc_alpha_div(df, output_path):
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
    alpha_df.to_csv(output_path / "alpha_div.csv")


def calc_beta_div(df, output_path, rarefaction_depth):
    rarefied_counts = []
    sample_ids = []

    for sample, row in df.iterrows():
        counts = np.round(row.values).astype(int)
        if counts.sum() >= rarefaction_depth:
            rarefied = _subsample_counts(counts, n=rarefaction_depth)
            rarefied_counts.append(rarefied)
            sample_ids.append(sample)

    if len(rarefied_counts) < 2:
        raise ValueError("Not enough samples passed the rarefaction threshold.")

    X = np.array(rarefied_counts, dtype=float)

    bray_df = pd.DataFrame(
        squareform(pdist(X, metric="braycurtis")),
        index=sample_ids, columns=sample_ids,
    )
    jaccard_df = pd.DataFrame(
        squareform(pdist(X.astype(bool).astype(float), metric="jaccard")),
        index=sample_ids, columns=sample_ids,
    )

    bray_df.to_csv(output_path / "beta_div_bray.csv")
    jaccard_df.to_csv(output_path / "beta_div_jaccard.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate α & β-diversities.")
    parser.add_argument("-i", "--input", required=True,
                        help="Input total count table CSV (species level).")
    parser.add_argument("-o", "--output", required=True,
                        help="Output directory path.")
    parser.add_argument("-d", "--depth", type=int, default=1000,
                        help="Rarefaction depth for β diversity (default: 1000).")
    args = parser.parse_args()

    input_file = Path(args.input)
    if not input_file.is_file():
        sys.exit(f"Error: input file not found: {input_file}")
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_file, index_col=0)

    calc_alpha_div(df, output_dir)
    calc_beta_div(df, output_dir, args.depth)
    print(
        f"α & β-diversities have been successfully calculated and saved to '{output_dir}'."
    )
