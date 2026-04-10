import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional


class KpPlotBase:
    def __init__(self, fig: plt.Figure, ax: plt.Axes):
        self.fig = fig
        self.ax = ax

    def plotfig(self) -> plt.Figure:
        # self.fig.tight_layout()
        plt.show()
        return self.fig

    def savefig(
        self,
        path: str,
        dpi: int = 300,
        transparent: bool = False,
        bbox_inches: Optional[str] = "tight",
    ):
        """
        Save the figure to a file.

        Parameters:
        - path: Path to save the figure (e.g. "plot.png", "plot.svg").
        - dpi: Dots per inch (resolution) of the output image. Default is 300.
        - transparent: Whether to make saved figure transparent.
        - bbox_inches: Bounding box option passed to matplotlib. Default is "tight".
        """
        self.fig.savefig(
            path, dpi=dpi, transparent=transparent, bbox_inches=bbox_inches
        )


def aggregate_by_metadata(
    df: pd.DataFrame,
    metadata: pd.DataFrame,
    metadata_group: str,
) -> pd.DataFrame:
    """Merge df with metadata and re-normalise rel_abund_perc per group."""
    if "Sample_id" not in metadata.columns:
        raise ValueError("metadata must contain 'Sample_id' column")
    if metadata_group not in metadata.columns:
        raise ValueError(f"'{metadata_group}' column not found in metadata")
    df = df.merge(
        metadata[["Sample_id", metadata_group]], on="Sample_id", how="left"
    )
    df = (
        df.groupby([metadata_group, "taxon"], as_index=False)["rel_abund_perc"]
        .mean()
        .rename(columns={metadata_group: "Sample_id"})
    )
    df["rel_abund_perc"] = df.groupby("Sample_id")["rel_abund_perc"].transform(
        lambda x: (x / x.sum()) * 100
    )
    return df
