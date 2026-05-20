import { RefreshCw, Route, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { api, Issue, Severity } from "../lib/api";
import { BenchmarkPanel } from "./BenchmarkPanel";
import { IssueTable } from "./IssueTable";
import { PerceptionViewer } from "./PerceptionViewer";
import { ValidationPanel } from "./ValidationPanel";

type Stats = {
  node_count: number;
  edge_count: number;
  connected_components: number;
  dead_end_count: number;
  average_degree: number;
};

export function MapDashboard() {
  const [place, setPlace] = useState("Isla Vista, California");
  const [issues, setIssues] = useState<Issue[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [summary, setSummary] = useState("");
  const [severity, setSeverity] = useState<Severity | "all">("all");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const filtered = useMemo(() => issues.filter((issue) => severity === "all" || issue.severity === severity), [issues, severity]);

  async function runPipeline() {
    setBusy(true);
    setError("");
    try {
      await api.ingest(place, true);
      const [validation, graphStats, qaSummary] = await Promise.all([api.validate(), api.graphStats(), api.summary()]);
      setIssues(validation.issues);
      setStats(graphStats);
      setSummary(qaSummary.text);
    } catch (err) {
      setError(err instanceof Error ? err.message : "pipeline failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="topbar">
        <div>
          <h1>autonomous map qa</h1>
          <p>road-network validation, perception checks, and gpu-aware preprocessing benchmarks</p>
        </div>
        <div className="controls">
          <label className="search-box">
            <Search size={18} />
            <input value={place} onChange={(event) => setPlace(event.target.value)} />
          </label>
          <button onClick={runPipeline} disabled={busy} title="run ingestion and validation">
            <RefreshCw size={18} />
            {busy ? "running" : "run"}
          </button>
        </div>
      </section>

      {error && <div className="error-state">{error}</div>}

      <section className="dashboard-grid">
        <div className="network-panel">
          <div className="panel-title">
            <Route size={18} />
            <span>road network qa view</span>
          </div>
          <div className="map-canvas">
            <svg viewBox="0 0 640 420" role="img" aria-label="road network issue overlay">
              <path d="M80 300 L430 300 L430 110 L90 110 L80 300" className="road major" />
              <path d="M80 300 L430 300" className="road duplicate" />
              <path d="M255 205 L255 205" className="road invalid" />
              <path d="M500 85 L560 45" className="road remote" />
              {filtered.slice(0, 30).map((issue, index) => (
                <circle
                  key={issue.issue_id}
                  cx={90 + (index % 8) * 62}
                  cy={92 + Math.floor(index / 8) * 72}
                  r={issue.severity === "high" ? 8 : 6}
                  className={`issue-dot ${issue.severity}`}
                />
              ))}
            </svg>
          </div>
        </div>

        <ValidationPanel stats={stats} issues={issues} severity={severity} onSeverityChange={setSeverity} summary={summary} />
        <IssueTable issues={filtered} />
        <BenchmarkPanel />
        <PerceptionViewer />
      </section>
    </main>
  );
}
