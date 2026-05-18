from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any

from app.models.schemas import MapIssue
from app.services.graph_builder import graph_stats


def _issue(issue_type: str, severity: str, explanation: str, recommended_action: str, **extra: Any) -> MapIssue:
    seed = "|".join(str(value) for value in [issue_type, explanation, extra.get("node_id"), extra.get("edge_id")])
    return MapIssue(
        issue_id=hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12],
        issue_type=issue_type,
        severity=severity,
        explanation=explanation,
        recommended_action=recommended_action,
        **extra,
    )


def _geometry_key(geometry: dict[str, Any] | None) -> tuple[tuple[float, float], ...] | None:
    if not geometry or geometry.get("type") != "LineString":
        return None
    coords = geometry.get("coordinates") or []
    rounded = tuple((round(float(x), 6), round(float(y), 6)) for x, y in coords)
    return tuple(sorted(rounded))


def validate_map_payload(payload: dict[str, Any]) -> list[MapIssue]:
    issues: list[MapIssue] = []
    nodes = {str(node["id"]): node for node in payload.get("nodes", [])}
    edges = payload.get("edges", [])
    stats = graph_stats(payload)
    if stats["connected_components"] > 1:
        issues.append(
            _issue(
                "disconnected_components",
                "high",
                f"road graph has {stats['connected_components']} disconnected components",
                "inspect component boundaries and confirm whether ferry, private, or missing connector roads explain the split",
            )
        )
    degree = defaultdict(int)
    for edge in edges:
        degree[str(edge.get("u"))] += 1
        degree[str(edge.get("v"))] += 1
    for node_id in nodes:
        if degree[node_id] == 0:
            issues.append(
                _issue(
                    "isolated_node",
                    "high",
                    f"node {node_id} has no incident road segments",
                    "remove stale node data or add the missing connecting road geometry",
                    node_id=node_id,
                )
            )
        elif degree[node_id] == 1:
            issues.append(
                _issue(
                    "dead_end",
                    "low",
                    f"node {node_id} is a dead end",
                    "confirm this is a legitimate cul-de-sac, driveway, or terminal segment",
                    node_id=node_id,
                )
            )
    seen_edges: dict[tuple[str, str, tuple[tuple[float, float], ...] | None], dict[str, Any]] = {}
    for edge in edges:
        edge_id = f"{edge.get('u')}:{edge.get('v')}:{edge.get('key')}"
        geometry = edge.get("geometry")
        coords = geometry.get("coordinates") if isinstance(geometry, dict) else None
        if not coords or len(coords) < 2:
            issues.append(
                _issue(
                    "invalid_geometry",
                    "high",
                    f"edge {edge_id} has missing or empty geometry",
                    "reload the source feature or reconstruct geometry from endpoint nodes",
                    edge_id=edge_id,
                    geometry=geometry,
                )
            )
        length = float(edge.get("length") or 0.0)
        if length < 5:
            issues.append(
                _issue(
                    "unusually_short_segment",
                    "medium",
                    f"edge {edge_id} is only {length:.1f} meters long",
                    "merge the segment with adjacent geometry or verify a real short connector exists",
                    edge_id=edge_id,
                    geometry=geometry,
                )
            )
        if length > 2000:
            issues.append(
                _issue(
                    "unusually_long_segment",
                    "medium",
                    f"edge {edge_id} is {length:.1f} meters long",
                    "split the road at intersections or confirm the source intentionally models it as one feature",
                    edge_id=edge_id,
                    geometry=geometry,
                )
            )
        if not str(edge.get("highway") or "").strip():
            issues.append(
                _issue(
                    "missing_road_classification",
                    "medium",
                    f"edge {edge_id} has no road classification",
                    "fill the highway or functional class tag before using this map for routing or simulation",
                    edge_id=edge_id,
                    geometry=geometry,
                )
            )
        if not str(edge.get("maxspeed") or "").strip():
            issues.append(
                _issue(
                    "missing_speed_metadata",
                    "low",
                    f"edge {edge_id} has no maxspeed metadata",
                    "enrich speed data from a trusted source or apply a documented class-based default",
                    edge_id=edge_id,
                    geometry=geometry,
                )
            )
        duplicate_key = tuple(sorted([str(edge.get("u")), str(edge.get("v"))])) + (_geometry_key(geometry),)
        if duplicate_key in seen_edges:
            issues.append(
                _issue(
                    "duplicate_edge",
                    "medium",
                    f"edge {edge_id} appears to duplicate another segment between the same nodes",
                    "deduplicate parallel records unless lane-level modeling intentionally requires them",
                    edge_id=edge_id,
                    geometry=geometry,
                )
            )
        else:
            seen_edges[duplicate_key] = edge
        if edge.get("oneway") is True:
            reverse_exists = any(str(other.get("u")) == str(edge.get("v")) and str(other.get("v")) == str(edge.get("u")) for other in edges)
            if reverse_exists:
                issues.append(
                    _issue(
                        "oneway_inconsistency",
                        "medium",
                        f"one-way edge {edge_id} also has a reverse edge",
                        "verify whether the road is bidirectional or represented as lane-level directed edges",
                        edge_id=edge_id,
                        geometry=geometry,
                    )
                )
    if stats["dead_end_count"] >= max(3, stats["node_count"] // 4):
        issues.append(
            _issue(
                "dead_end_cluster",
                "medium",
                f"{stats['dead_end_count']} nodes have dead-end connectivity",
                "review local extraction boundaries and service roads for missing connectors",
            )
        )
    if stats["average_degree"] < 2:
        issues.append(
            _issue(
                "low_connectivity_subgraph",
                "high",
                f"average graph degree is {stats['average_degree']}",
                "audit source coverage and graph simplification settings before simulation use",
            )
        )
    return issues


def summarize_issues(issues: list[MapIssue]) -> dict[str, Any]:
    by_severity = {"high": 0, "medium": 0, "low": 0}
    by_type: dict[str, int] = {}
    for issue in issues:
        by_severity[issue.severity] += 1
        by_type[issue.issue_type] = by_type.get(issue.issue_type, 0) + 1
    return {"by_severity": by_severity, "by_type": by_type}
