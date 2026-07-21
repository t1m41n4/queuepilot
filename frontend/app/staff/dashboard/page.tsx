"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { ErrorState, LoadingState, PageHeader, Shell } from "../../../components/ui";
import { get, hasAccessToken, post, userFacingError, websocketUrl } from "../../../lib/api";
import type { StaffDashboardResponse, StaffQueueItem } from "../../../lib/types";

const summaryFields: Array<[keyof StaffDashboardResponse, string]> = [
  ["queue_status", "Queue Status"],
  ["waiting", "Waiting"],
  ["ready", "Ready"],
  ["checked_in", "Checked In"],
  ["current_customer", "Current Customer"],
];

const actionPaths: Record<string, string> = {
  "Check In": "/staff/check-in",
  "Call Next": "/staff/call-next",
  "Start Service": "/staff/start-service",
  "Complete Service": "/staff/complete-service",
};

export default function StaffDashboardPage() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState<StaffDashboardResponse>();
  const [queue, setQueue] = useState<StaffQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [operation, setOperation] = useState(false);
  const [error, setError] = useState<string>();

  const load = useCallback(() => {
    setLoading(true);
    setError(undefined);
    return Promise.all([
      get<StaffDashboardResponse>("/staff/dashboard"),
      get<StaffQueueItem[]>("/staff/queue"),
    ])
      .then(([summary, entries]) => { setDashboard(summary); setQueue(entries); })
      .catch((reason: unknown) => {
        const message = userFacingError(reason);
        setError(message);
        if (message.includes("session has expired")) router.push("/staff/login");
      })
      .finally(() => setLoading(false));
  }, [router]);

  useEffect(() => {
    if (!hasAccessToken()) {
      setError("Please sign in to access the staff dashboard.");
      setLoading(false);
      router.push("/staff/login");
      return;
    }
    void load();
  }, [load, router]);

  useEffect(() => {
    const branchId = dashboard?.branch_id;
    if (!branchId) return;
    let stopped = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let socket: WebSocket | undefined;
    const connect = () => {
      if (stopped) return;
      socket = new WebSocket(websocketUrl(`/ws/queue/${branchId}`));
      socket.onopen = () => setError(undefined);
      socket.onmessage = (message) => {
        try {
          const update = JSON.parse(message.data) as { event?: string };
          if (["QUEUE_UPDATED", "READY", "CALLED", "QUEUE_PAUSED", "QUEUE_RESUMED"].includes(update.event ?? "")) {
            void load();
          }
        } catch {
          setError("Live queue updates are unavailable.");
        }
      };
      socket.onerror = () => setError("Live queue updates are unavailable.");
      socket.onclose = () => { if (!stopped) timer = setTimeout(connect, 3000); };
    };
    connect();
    return () => { stopped = true; if (timer) clearTimeout(timer); socket?.close(); };
  }, [dashboard?.branch_id, load]);

  function runOperation(path: string, body: unknown = {}) {
    setOperation(true);
    setError(undefined);
    post(path, body)
      .then(() => load())
      .catch((reason: unknown) => setError(userFacingError(reason)))
      .finally(() => setOperation(false));
  }

  function runEntryAction(entry: StaffQueueItem) {
    if (!entry.action || !entry.queue_entry_id) return;
    const path = actionPaths[entry.action];
    if (path) runOperation(path, { queue_entry_id: entry.queue_entry_id });
  }

  return <Shell>
    <PageHeader eyebrow="Staff" title="Queue dashboard" description="Monitor the branch queue and use backend-provided actions." />
    {loading && <LoadingState label="Loading dashboard…" />}
    {error && <ErrorState message={error} />}
    {dashboard && <>
      <section className="status-grid">
        {summaryFields.map(([key, label]) => <div className="metric-card" key={key}><span>{label}</span><strong>{String(dashboard[key] ?? "—")}</strong></div>)}
      </section>
      <section className="panel">
        <div className="section-heading"><h2>Queue</h2><div className="button-row">
          <button type="button" onClick={() => runOperation("/staff/pause")} disabled={operation}>Pause Queue</button>
          <button type="button" onClick={() => runOperation("/staff/resume")} disabled={operation}>Resume Queue</button>
        </div></div>
        <div className="table-wrap"><table><thead><tr><th>Queue Number</th><th>Customer</th><th>Status</th><th>ETA</th><th>Action</th></tr></thead><tbody>
          {queue.map((entry, index) => <tr key={`${entry.queue_entry_id ?? entry.queue_number ?? "entry"}-${index}`}>
            <td>{entry.queue_number ?? "—"}</td><td>{entry.customer_name ?? "—"}</td><td>{entry.status ?? "—"}</td><td>{entry.estimated_wait ?? "—"}</td>
            <td>{entry.action && entry.queue_entry_id ? <button type="button" onClick={() => runEntryAction(entry)} disabled={operation}>{entry.action}</button> : "—"}</td>
          </tr>)}
        </tbody></table></div>
      </section>
    </>}
  </Shell>;
}
