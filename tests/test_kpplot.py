"""kpplot smoke tests and parameter-validation tests."""

import pytest

from krakenparser.kpplot.stackedbar import stacked_barplot
from krakenparser.kpplot.streamgraph import streamgraph
from krakenparser.kpplot.clustermap import clustermap
from krakenparser.kpplot.base import KpPlotBase, aggregate_by_metadata


# ---------------------------------------------------------------------------
# Smoke tests — verify each plot function returns without error
# ---------------------------------------------------------------------------

def test_stackedbar_returns_kpplotbase(relabund_df):
    result = stacked_barplot(relabund_df)
    assert isinstance(result, KpPlotBase)


def test_streamgraph_returns_kpplotbase(relabund_df):
    result = streamgraph(relabund_df)
    assert isinstance(result, KpPlotBase)


def test_clustermap_returns_kpplotbase(relabund_df):
    result = clustermap(relabund_df)
    assert isinstance(result, KpPlotBase)


# ---------------------------------------------------------------------------
# sample_order validation
# ---------------------------------------------------------------------------

def test_stackedbar_sample_order_missing_raises(relabund_df):
    with pytest.raises(ValueError, match="Samples missing"):
        stacked_barplot(relabund_df, sample_order=["S1", "S2", "GHOST"])


def test_streamgraph_sample_order_missing_raises(relabund_df):
    with pytest.raises(ValueError, match="Samples missing"):
        streamgraph(relabund_df, sample_order=["S1", "GHOST"])


def test_clustermap_sample_order_missing_raises(relabund_df):
    with pytest.raises(ValueError, match="Samples missing"):
        clustermap(relabund_df, sample_order=["S1", "GHOST"])


# ---------------------------------------------------------------------------
# cmap validation (stackedbar / streamgraph)
# ---------------------------------------------------------------------------

def test_stackedbar_cmap_too_short_raises(relabund_df):
    with pytest.raises(ValueError, match="cmap"):
        stacked_barplot(relabund_df, cmap=["red"])


def test_streamgraph_cmap_too_short_raises(relabund_df):
    with pytest.raises(ValueError, match="cmap"):
        streamgraph(relabund_df, cmap=["red"])


def test_stackedbar_cmap_invalid_type_raises(relabund_df):
    with pytest.raises(ValueError, match="cmap"):
        stacked_barplot(relabund_df, cmap=123)


def test_streamgraph_cmap_invalid_type_raises(relabund_df):
    with pytest.raises(ValueError, match="cmap"):
        streamgraph(relabund_df, cmap=123)


# ---------------------------------------------------------------------------
# aggregate_by_metadata
# ---------------------------------------------------------------------------

def test_aggregate_by_metadata_basic(relabund_df):
    import pandas as pd

    metadata = pd.DataFrame({
        "Sample_id": ["S1", "S2"],
        "Group": ["A", "A"],
    })
    result = aggregate_by_metadata(relabund_df, metadata, "Group")
    assert "Sample_id" in result.columns
    assert set(result["Sample_id"]) == {"A"}
    # Relative abundance should still sum to 100 per group
    total = result["rel_abund_perc"].sum()
    assert total == pytest.approx(100.0, abs=1e-6)


def test_aggregate_by_metadata_missing_sample_id_column_raises(relabund_df):
    import pandas as pd

    bad_meta = pd.DataFrame({"Group": ["A", "B"], "X": [1, 2]})
    with pytest.raises(ValueError, match="Sample_id"):
        aggregate_by_metadata(relabund_df, bad_meta, "Group")


def test_aggregate_by_metadata_missing_group_column_raises(relabund_df):
    import pandas as pd

    meta = pd.DataFrame({"Sample_id": ["S1", "S2"]})
    with pytest.raises(ValueError, match="Group"):
        aggregate_by_metadata(relabund_df, meta, "Group")
