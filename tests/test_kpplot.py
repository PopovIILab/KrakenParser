"""kpplot smoke, parameter-validation, and output-contract tests.

Sections
--------
1. Smoke tests          — each plot function returns a KpPlotBase without error.
2. sample_order         — ValueError when requested samples are missing from the data.
3. cmap validation      — ValueError on too-short or wrong-type colour maps.
4. aggregate_by_metadata— aggregation logic and missing-column validation.
5. Base class methods   — plotfig() return value and savefig() filesystem contract.
6. Full-parameter smoke — metadata, sample_order, cmap, title all wired together.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from krakenparser.kpplot.base import KpPlotBase, aggregate_by_metadata
from krakenparser.kpplot.clustermap import clustermap
from krakenparser.kpplot.stackedbar import stacked_barplot
from krakenparser.kpplot.streamgraph import streamgraph

# ---------------------------------------------------------------------------
# Module-local fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def cohort_metadata():
    """Metadata DataFrame mapping S1→CohortA and S2→CohortB."""
    return pd.DataFrame({"Sample_id": ["S1", "S2"], "Group": ["CohortA", "CohortB"]})


# ---------------------------------------------------------------------------
# 1. Smoke tests — happy-path return type
# ---------------------------------------------------------------------------


def test_stackedbar_returns_kpplotbase(relabund_df):
    assert isinstance(stacked_barplot(relabund_df), KpPlotBase)


def test_streamgraph_returns_kpplotbase(relabund_df):
    assert isinstance(streamgraph(relabund_df), KpPlotBase)


def test_clustermap_returns_kpplotbase(relabund_df):
    assert isinstance(clustermap(relabund_df), KpPlotBase)


# ---------------------------------------------------------------------------
# 2. sample_order validation
# ---------------------------------------------------------------------------


def test_stackedbar_unknown_sample_in_order_raises(relabund_df):
    with pytest.raises(ValueError, match="Samples missing"):
        stacked_barplot(relabund_df, sample_order=["S1", "S2", "GHOST"])


def test_streamgraph_unknown_sample_in_order_raises(relabund_df):
    with pytest.raises(ValueError, match="Samples missing"):
        streamgraph(relabund_df, sample_order=["S1", "GHOST"])


def test_clustermap_unknown_sample_in_order_raises(relabund_df):
    with pytest.raises(ValueError, match="Samples missing"):
        clustermap(relabund_df, sample_order=["S1", "GHOST"])


# ---------------------------------------------------------------------------
# 3. cmap validation (stackedbar / streamgraph)
# ---------------------------------------------------------------------------


def test_stackedbar_cmap_too_short_raises(relabund_df):
    with pytest.raises(ValueError, match="cmap"):
        stacked_barplot(relabund_df, cmap=["red"])


def test_streamgraph_cmap_too_short_raises(relabund_df):
    with pytest.raises(ValueError, match="cmap"):
        streamgraph(relabund_df, cmap=["red"])


def test_stackedbar_cmap_wrong_type_raises(relabund_df):
    with pytest.raises(ValueError, match="cmap"):
        stacked_barplot(relabund_df, cmap=123)  # ty:ignore[invalid-argument-type]


def test_streamgraph_cmap_wrong_type_raises(relabund_df):
    with pytest.raises(ValueError, match="cmap"):
        streamgraph(relabund_df, cmap=123)  # ty:ignore[invalid-argument-type]


# ---------------------------------------------------------------------------
# 4. aggregate_by_metadata
# ---------------------------------------------------------------------------


def test_aggregate_by_metadata_groups_samples_correctly(relabund_df):
    metadata = pd.DataFrame({"Sample_id": ["S1", "S2"], "Group": ["A", "A"]})
    result = aggregate_by_metadata(relabund_df, metadata, "Group")

    assert "Sample_id" in result.columns
    assert set(result["Sample_id"]) == {"A"}


def test_aggregate_by_metadata_relative_abundance_sums_to_100(relabund_df):
    metadata = pd.DataFrame({"Sample_id": ["S1", "S2"], "Group": ["A", "A"]})
    result = aggregate_by_metadata(relabund_df, metadata, "Group")
    assert result["rel_abund_perc"].sum() == pytest.approx(100.0, abs=1e-6)


def test_aggregate_by_metadata_missing_sample_id_column_raises(relabund_df):
    bad_meta = pd.DataFrame({"Group": ["A", "B"], "X": [1, 2]})
    with pytest.raises(ValueError, match="Sample_id"):
        aggregate_by_metadata(relabund_df, bad_meta, "Group")


def test_aggregate_by_metadata_missing_group_column_raises(relabund_df):
    meta = pd.DataFrame({"Sample_id": ["S1", "S2"]})
    with pytest.raises(ValueError, match="Group"):
        aggregate_by_metadata(relabund_df, meta, "Group")


# ---------------------------------------------------------------------------
# 5. KpPlotBase methods — plotfig() and savefig()
# ---------------------------------------------------------------------------


def test_kpplotbase_plotfig_returns_figure(relabund_df):
    ctx = stacked_barplot(df=relabund_df)
    assert ctx.plotfig() is not None


def test_kpplotbase_savefig_writes_file(relabund_df, tmp_path):
    ctx = stacked_barplot(df=relabund_df)
    img_path = tmp_path / "output.png"
    ctx.savefig(img_path)
    assert os.path.exists(img_path)


# ---------------------------------------------------------------------------
# 6. Full-parameter smoke — metadata, sample_order, cmap, title
# ---------------------------------------------------------------------------


def test_stackedbar_with_all_parameters(relabund_df, two_sample_metadata, tmp_path):
    custom_colors = ["#ff0000", "#00ff00", "#0000ff"]
    ctx = stacked_barplot(
        df=relabund_df,
        metadata=two_sample_metadata,
        metadata_group="Group",
        sample_order=["TypeA", "TypeB"],
        cmap=custom_colors,
        title="Full-Parameter Barplot",
    )
    assert ctx.fig is not None

    out = tmp_path / "barplot.png"
    ctx.fig.savefig(out, dpi=150, bbox_inches="tight")
    assert out.exists()

    plt.close(ctx.fig)


def test_streamgraph_with_all_parameters(relabund_df, two_sample_metadata):
    ctx = streamgraph(
        df=relabund_df,
        metadata=two_sample_metadata,
        metadata_group="Group",
        sample_order=["TypeA", "TypeB"],
        cmap=["#ff0000", "#00ff00", "#0000ff"],
        title="Full-Parameter Streamgraph",
    )
    assert ctx.fig is not None
    plt.close(ctx.fig)


def test_clustermap_with_all_parameters(relabund_df, cohort_metadata):
    ctx = clustermap(
        df=relabund_df,
        metadata=cohort_metadata,
        metadata_group="Group",
        sample_order=["CohortA", "CohortB"],
        title="Full-Parameter Clustermap",
        xlabel="X Label",
        ylabel="Y Label",
    )
    assert ctx.grid is not None


def test_clustermap_unknown_sample_in_order_raises_with_message(relabund_df):
    with pytest.raises(ValueError, match="Samples missing from the clustermap matrix"):
        clustermap(df=relabund_df, sample_order=["GHOST_SAMPLE"])
