from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.graph_builder import edge_geometry, haversine_meters, save_graph_payload


def _sample_nodes() -> list[dict[str, Any]]:
    base_lat = 34.412
    base_lon = -119.86
    return [
        {"id": "n1", "lat": base_lat, "lon": base_lon, "highway": "traffic_signals"},
        {"id": "n2", "lat": base_lat, "lon": base_lon + 0.004},
        {"id": "n3", "lat": base_lat + 0.003, "lon": base_lon + 0.004},
        {"id": "n4", "lat": base_lat + 0.003, "lon": base_lon},
        {"id": "n5", "lat": base_lat + 0.0015, "lon": base_lon + 0.002},
        {"id": "n6", "lat": base_lat + 0.02, "lon": base_lon + 0.02},
        {"id": "n7", "lat": base_lat + 0.0204, "lon": base_lon + 0.0204},
        {"id": "n8", "lat": base_lat + 0.00302, "lon": base_lon + 0.00002},
    ]


def _make_edge(nodes: dict[str, dict[str, Any]], u: str, v: str, key: int, **tags: Any) -> dict[str, Any]:
    length = haversine_meters(nodes[u]["lat"], nodes[u]["lon"], nodes[v]["lat"], nodes[v]["lon"])
    return {
        "u": u,
        "v": v,
        "key": key,
        "length": round(length, 2),
        "geometry": edge_geometry(nodes[u], nodes[v]),
        **tags,
    }


def generate_sample_map(place_name: str = "Isla Vista, California") -> dict[str, Any]:
    nodes = _sample_nodes()
    node_lookup = {node["id"]: node for node in nodes}
    edges = [
        _make_edge(node_lookup, "n1", "n2", 0, name="pardall road", highway="residential", maxspeed="25 mph", oneway=False),
        _make_edge(node_lookup, "n2", "n3", 0, name="camino corto", highway="residential", maxspeed="25 mph", oneway=False),
        _make_edge(node_lookup, "n3", "n4", 0, name="del playa drive", highway="residential", oneway=True),
        _make_edge(node_lookup, "n4", "n1", 0, name="el colegio road", highway="secondary", maxspeed="35 mph", oneway=False),
        _make_edge(node_lookup, "n1", "n2", 1, name="pardall road duplicate", highway="residential", maxspeed="25 mph", oneway=False),
        _make_edge(node_lookup, "n5", "n5", 0, name="", highway="", maxspeed="", oneway=False),
        _make_edge(node_lookup, "n6", "n7", 0, name="remote service road", highway="service", oneway=False),
        _make_edge(node_lookup, "n4", "n8", 0, name="short connector", highway="service", maxspeed="10 mph", oneway=False),
    ]
    return {"place_name": place_name, "source": "generated-sample", "nodes": nodes, "edges": edges}


def ingest_map(place_name: str, network_type: str = "drive", use_sample: bool = False) -> tuple[dict[str, Any], Path]:
    if not use_sample:
        try:
            import osmnx as ox

            graph = ox.graph_from_place(place_name, network_type=network_type, simplify=True)
            nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)
            nodes = [
                {"id": str(index), "lat": float(row.geometry.y), "lon": float(row.geometry.x)}
                for index, row in nodes_gdf.iterrows()
            ]
            edges: list[dict[str, Any]] = []
            for (u, v, key), row in edges_gdf.iterrows():
                geometry = row.geometry.__geo_interface__ if row.geometry is not None else None
                edges.append(
                    {
                        "u": str(u),
                        "v": str(v),
                        "key": str(key),
                        "name": str(row.get("name", "")),
                        "highway": str(row.get("highway", "")),
                        "maxspeed": str(row.get("maxspeed", "")),
                        "oneway": bool(row.get("oneway", False)),
                        "length": float(row.get("length", 0.0)),
                        "geometry": geometry,
                    }
                )
            payload = {"place_name": place_name, "source": "openstreetmap-osmnx", "nodes": nodes, "edges": edges}
        except Exception:
            payload = generate_sample_map(place_name)
    else:
        payload = generate_sample_map(place_name)
    output_dir = settings.data_dir / "generated_map"
    return payload, save_graph_payload(payload, output_dir)
