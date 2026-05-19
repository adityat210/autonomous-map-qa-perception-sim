from __future__ import annotations

from app.services.graph_builder import graph_stats
from app.services.map_ingestion import generate_sample_map


def test_graph_stats_counts_components_and_dead_ends():
    stats = graph_stats(generate_sample_map())
    assert stats["node_count"] == 8
    assert stats["edge_count"] == 8
    assert stats["connected_components"] >= 2
    assert stats["dead_end_count"] >= 2
