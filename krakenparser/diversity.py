#!/usr/bin/env python

import pandas as pd
import numpy as np
import sys
import shutil
import argparse
from pathlib import Path
from skbio.diversity import beta_diversity
from skbio.stats import subsample_counts


# Define Shannon index
def shannon_index(counts):
    counts = np.array(counts)
    counts = counts[counts > 0]
    proportions = counts / counts.sum()
    return -np.sum(proportions * np.log(proportions))


# Define Pielou's evenness
def pielou_evenness(counts):
    counts = np.array(counts)
    counts = counts[counts > 0]
    H = shannon_index(counts)
    S = len(counts)
    return H / np.log(S) if S > 1 else 0


# Define Chao1 richness estimator
def chao1_index(counts):
    counts = np.array(counts)
    S_obs = np.sum(counts > 0)
    F1 = np.sum(counts == 1)
    F2 = np.sum(counts == 2)
    if F2 == 0:
        return S_obs + F1 * (F1 - 1) / 2
    return S_obs + (F1 * F1) / (2 * F2)


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
        counts = row.values.astype(int)
        if counts.sum() >= rarefaction_depth:
            rarefied = subsample_counts(counts, n=rarefaction_depth)
            rarefied_counts.append(rarefied)
            sample_ids.append(sample)

    if len(rarefied_counts) < 2:
        raise ValueError("Not enough samples passed the rarefaction threshold.")

    bray_df = beta_diversity(
        "braycurtis", rarefied_counts, ids=sample_ids
    ).to_data_frame()
    jaccard_df = beta_diversity(
        "jaccard", rarefied_counts, ids=sample_ids
    ).to_data_frame()

    bray_df.to_csv(output_path / "beta_div_bray.csv")
    jaccard_df.to_csv(output_path / "beta_div_jaccard.csv")


if __name__ == "__main__":
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
    args = parser.parse_args()

    input_file = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_file, index_col=0)

    calc_alpha_div(df, output_dir)
    calc_beta_div(df, output_dir, args.depth)
    print(
        f"α & β-diversities have been successfully calculated and saved to '{output_dir}'."
    )

    pycache_dir = Path(__file__).resolve().parent / "__pycache__"
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)
