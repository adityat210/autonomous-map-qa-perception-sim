import { Cpu, Gauge } from "lucide-react";
import { useState } from "react";
import { api } from "../lib/api";

type Benchmark = { device: string; cpu_ms: number; gpu_ms?: number; speedup?: number; workload: string };

export function BenchmarkPanel() {
  const [benchmark, setBenchmark] = useState<Benchmark | null>(null);
  const [busy, setBusy] = useState(false);
  async function run() {
    setBusy(true);
    try {
      setBenchmark(await api.benchmark());
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="mini-panel">
      <div className="panel-title">
        <Gauge size={18} />
        <span>benchmark</span>
      </div>
      <button onClick={run} disabled={busy} title="run gpu benchmark">
        <Cpu size={18} />
        {busy ? "running" : "run benchmark"}
      </button>
      {benchmark ? (
        <div className="stats-list">
          <span>device {benchmark.device}</span>
          <span>cpu {benchmark.cpu_ms} ms</span>
          <span>gpu {benchmark.gpu_ms ?? "not available"}</span>
          <span>speedup {benchmark.speedup ?? "cpu only"}</span>
        </div>
      ) : (
        <p className="empty">cpu fallback runs even without cuda</p>
      )}
    </section>
  );
}
