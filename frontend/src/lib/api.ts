export type Severity = "low" | "medium" | "high";

export type Issue = {
  issue_id: string;
  issue_type: string;
  severity: Severity;
  explanation: string;
  recommended_action: string;
  geometry?: { type: string; coordinates: number[][] };
};

const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    headers: { "content-type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

export const api = {
  ingest: (placeName: string, useSample = true) =>
    request<{ node_count: number; edge_count: number; output_path: string; source: string }>("/maps/ingest", {
      method: "POST",
      body: JSON.stringify({ place_name: placeName, use_sample: useSample }),
    }),
  validate: () =>
    request<{ issue_count: number; issues: Issue[]; summary: Record<string, unknown> }>("/maps/validate", {
      method: "POST",
      body: JSON.stringify({}),
    }),
  graphStats: () =>
    request<{ node_count: number; edge_count: number; connected_components: number; dead_end_count: number; average_degree: number }>(
      "/maps/graph-stats",
    ),
  summary: () => request<{ text: string; issue_count: number; high_severity_count: number }>("/maps/summary"),
  perception: () =>
    request<{ frame_count: number; issues: Issue[] }>("/perception/load-sample", {
      method: "POST",
      body: JSON.stringify({ dataset_path: "data/sample/perception" }),
    }),
  visualOdometry: () =>
    request<{ frame_count: number; estimates: Array<{ from_frame: string; to_frame: string; match_count: number; inlier_count: number }> }>(
      "/perception/visual-odometry",
      { method: "POST", body: JSON.stringify({ dataset_path: "data/sample/perception" }) },
    ),
  benchmark: () =>
    request<{ device: string; cpu_ms: number; gpu_ms?: number; speedup?: number; workload: string }>("/benchmarks/gpu", {
      method: "POST",
      body: JSON.stringify({ size: 256, iterations: 5 }),
    }),
};
