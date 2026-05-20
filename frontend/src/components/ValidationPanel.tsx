import { AlertTriangle, Network } from "lucide-react";
import { Issue, Severity } from "../lib/api";

type Props = {
  stats: {
    node_count: number;
    edge_count: number;
    connected_components: number;
    dead_end_count: number;
    average_degree: number;
  } | null;
  issues: Issue[];
  severity: Severity | "all";
  summary: string;
  onSeverityChange: (severity: Severity | "all") => void;
};

export function ValidationPanel({ stats, issues, severity, onSeverityChange, summary }: Props) {
  const counts = {
    high: issues.filter((issue) => issue.severity === "high").length,
    medium: issues.filter((issue) => issue.severity === "medium").length,
    low: issues.filter((issue) => issue.severity === "low").length,
  };
  return (
    <aside className="side-panel">
      <div className="panel-title">
        <AlertTriangle size={18} />
        <span>validation</span>
      </div>
      <div className="metric-row">
        <span>issues</span>
        <strong>{issues.length}</strong>
      </div>
      <div className="severity-tabs">
        {(["all", "high", "medium", "low"] as const).map((item) => (
          <button key={item} className={severity === item ? "active" : ""} onClick={() => onSeverityChange(item)}>
            {item}
          </button>
        ))}
      </div>
      <div className="severity-counts">
        <span className="high">high {counts.high}</span>
        <span className="medium">medium {counts.medium}</span>
        <span className="low">low {counts.low}</span>
      </div>
      <div className="panel-title small">
        <Network size={16} />
        <span>graph stats</span>
      </div>
      {stats ? (
        <div className="stats-list">
          <span>nodes {stats.node_count}</span>
          <span>edges {stats.edge_count}</span>
          <span>components {stats.connected_components}</span>
          <span>dead ends {stats.dead_end_count}</span>
          <span>avg degree {stats.average_degree}</span>
        </div>
      ) : (
        <p className="empty">run the pipeline to populate graph stats</p>
      )}
      <p className="summary">{summary || "qa summary appears after validation runs."}</p>
    </aside>
  );
}
