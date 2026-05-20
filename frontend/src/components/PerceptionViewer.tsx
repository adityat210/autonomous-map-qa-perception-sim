import { Camera, Waypoints } from "lucide-react";
import { useState } from "react";
import { api, Issue } from "../lib/api";

export function PerceptionViewer() {
  const [frameCount, setFrameCount] = useState<number | null>(null);
  const [issueCount, setIssueCount] = useState<number | null>(null);
  const [motionCount, setMotionCount] = useState<number | null>(null);
  async function load() {
    const [perception, odometry] = await Promise.all([api.perception(), api.visualOdometry()]);
    setFrameCount(perception.frame_count);
    setIssueCount((perception.issues as Issue[]).length);
    setMotionCount(odometry.estimates.length);
  }
  return (
    <section className="mini-panel">
      <div className="panel-title">
        <Camera size={18} />
        <span>perception</span>
      </div>
      <button onClick={load} title="load sample perception data">
        <Waypoints size={18} />
        inspect sample
      </button>
      {frameCount === null ? (
        <p className="empty">sample frames and odometry status appear here</p>
      ) : (
        <div className="stats-list">
          <span>frames {frameCount}</span>
          <span>issues {issueCount}</span>
          <span>motion estimates {motionCount}</span>
        </div>
      )}
    </section>
  );
}
