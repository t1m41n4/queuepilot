"use client";

import { useEffect, useState } from "react";

import { ErrorState, LoadingState, PageHeader, Shell } from "../../../components/ui";
import { get, post } from "../../../lib/api";
import type { StaffDashboardResponse, StaffQueueItem } from "../../../lib/types";

const summaryFields: Array<[keyof StaffDashboardResponse, string]> = [["queue_status", "Queue Status"], ["waiting", "Waiting"], ["ready", "Ready"], ["checked_in", "Checked In"], ["current_customer", "Current Customer"]];

export default function StaffDashboardPage() {
  const [dashboard, setDashboard] = useState<StaffDashboardResponse>();
  const [queue, setQueue] = useState<StaffQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  function load() {
    setLoading(true); setError(undefined);
    Promise.all([get<StaffDashboardResponse>("/staff/dashboard"), get<StaffQueueItem[]>("/staff/queue")])
      .then(([summary, entries]) => { setDashboard(summary); setQueue(entries); })
      .catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false));
  }
  useEffect(() => { load(); }, []);

  function changeQueue(path: "/staff/pause" | "/staff/resume") {
    post(path, {}).then(load).catch((reason: Error) => setError(reason.message));
  }

  return <Shell><PageHeader eyebrow="Staff" title="Queue dashboard" description="Monitor the branch queue and use backend-provided actions." />{loading && <LoadingState label="Loading dashboard…" />}{error && <ErrorState message={error} />}{dashboard && <><section className="status-grid">{summaryFields.map(([key, label]) => <div className="metric-card" key={key}><span>{label}</span><strong>{String(dashboard[key] ?? "—")}</strong></div>)}</section><section className="panel"><div className="section-heading"><h2>Queue</h2><div className="button-row"><button type="button" onClick={() => changeQueue("/staff/pause")}>Pause Queue</button><button type="button" onClick={() => changeQueue("/staff/resume")}>Resume Queue</button></div></div><div className="table-wrap"><table><thead><tr><th>Queue Number</th><th>Customer</th><th>Status</th><th>ETA</th><th>Action</th></tr></thead><tbody>{queue.map((entry, index) => <tr key={`${entry.queue_number ?? "entry"}-${index}`}><td>{entry.queue_number ?? "—"}</td><td>{entry.customer_name ?? "—"}</td><td>{entry.status ?? "—"}</td><td>{entry.estimated_wait ?? "—"}</td><td>{entry.action ? <button type="button">{entry.action}</button> : "—"}</td></tr>)}</tbody></table></div></section></>}</Shell>;
}
