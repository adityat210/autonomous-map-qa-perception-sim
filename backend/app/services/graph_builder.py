from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

try:
    import networkx as nx
except Exception:  # pragma: no cover
    nx = None


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def edge_geometry(node_a: dict[str, Any], node_b: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "LineString",
        "coordinates": [[node_a["lon"], node_a["lat"]], [node_b["lon"], node_b["lat"]]],
    }


def build_graph(payload: dict[str, Any]):
    if nx is None:
        raise RuntimeError("networkx is required to build graph objects")
    graph = nx.MultiDiGraph()
    for node in payload["nodes"]:
        graph.add_node(str(node["id"]), **node)
    for edge in payload["edges"]:
        graph.add_edge(str(edge["u"]), str(edge["v"]), key=str(edge.get("key", 0)), **edge)
    return graph


def graph_stats(payload: dict[str, Any]) -> dict[str, Any]:
    node_ids = {str(node["id"]) for node in payload["nodes"]}
    degree = {node_id: 0 for node_id in node_ids}
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    for edge in payload["edges"]:
        u = str(edge["u"])
        v = str(edge["v"])
        if u in degree:
            degree[u] += 1
            adjacency[u].add(v)
        if v in degree:
            degree[v] += 1
            adjacency[v].add(u)
    seen: set[str] = set()
    components = 0
    for node_id in node_ids:
        if node_id in seen:
            continue
        components += 1
        stack = [node_id]
        seen.add(node_id)
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    avg_degree = sum(degree.values()) / max(len(degree), 1)
    return {
        "node_count": len(payload["nodes"]),
        "edge_count": len(payload["edges"]),
        "connected_components": components,
        "dead_end_count": sum(1 for value in degree.values() if value <= 1),
        "average_degree": round(avg_degree, 3),
    }


def save_graph_payload(payload: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "road_graph.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_graph_payload(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
