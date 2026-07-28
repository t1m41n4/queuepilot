"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { ConnectionIndicator, EmptyState, ErrorState, LoadingState, PageHeader, Shell, StatusBadge } from "../../../components/ui";
import { clearAccessToken, get, hasAccessToken, post, userFacingError, websocketUrl } from "../../../lib/api";
import type { StaffDashboardResponse, StaffQueueItem } from "../../../lib/types";

const summaryFields: Array<[keyof StaffDashboardResponse, string]> = [
  ["queue_status", "Queue Status"],
  ["waiting", "Waiting"],
  ["ready", "Ready"],
  ["checked_in", "Checked In"],
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
  const [notice, setNotice] = useState<string>();
  const [connectionState, setConnectionState] = useState<"connecting" | "connected" | "disconnected">("disconnected");

  const load = useCallback(() => {
    setLoading(true);
    setError(undefined);
    return Promise.all([get<StaffDashboardResponse>("/staff/dashboard"), get<StaffQueueItem[]>("/staff/queue")])
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
      setConnectionState("connecting");
      socket = new WebSocket(websocketUrl(`/ws/queue/${branchId}`));
      socket.onopen = () => setConnectionState("connected");
      socket.onmessage = (message) => {
        try {
          const update = JSON.parse(message.data) as { event?: string };
          if (["QUEUE_UPDATED", "READY", "CALLED", "QUEUE_PAUSED", "QUEUE_RESUMED"].includes(update.event ?? "")) void load();
        } catch {
          setConnectionState("disconnected");
        }
      };
      socket.onerror = () => setConnectionState("disconnected");
      socket.onclose = () => {
        setConnectionState("disconnected");
        if (!stopped) timer = setTimeout(connect, 3000);
      };
    };
    connect();
    return () => { stopped = true; if (timer) clearTimeout(timer); socket?.close(); };
  }, [dashboard?.branch_id, load]);

  function runOperation(path: string, body: unknown = {}, label: string) {
    setOperation(true);
    setError(undefined);
    setNotice(undefined);
    post(path, body)
      .then(() => { setNotice(`${label} completed successfully.`); return load(); })
      .catch((reason: unknown) => setError(userFacingError(reason)))
      .finally(() => setOperation(false));
  }

  function runEntryAction(entry: StaffQueueItem) {
    if (!entry.action || !entry.queue_entry_id) return;
    const path = actionPaths[entry.action];
    if (path) runOperation(path, entry.action === "Call Next" ? {} : { queue_entry_id: entry.queue_entry_id }, entry.action);
  }

  function logout() {
    clearAccessToken();
    router.push("/staff/login");
  }

  return <Shell>
    <div className="staff-context">
      <PageHeader eyebrow="Staff" title="Queue dashboard" description="Monitor your branch queue and serve customers efficiently." />
      <div className="button-row"><button className="secondary-link" type="button" onClick={logout}>Sign out</button></div>
    </div>
    {loading && <LoadingState label="Loading dashboard…" />}
    {error && <ErrorState message={error} />}
    {notice && <p className="state-message operation-notice" role="status">{notice}</p>}
    {dashboard && <>
      <section className="panel staff-context"><div><p className="eyebrow">Assigned branch</p><h2>Branch #{dashboard.branch_id ?? "—"}</h2></div><ConnectionIndicator state={connectionState} /></section>
      <section className="status-grid">{summaryFields.map(([key, label]) => <div className="metric-card" key={key}><span>{label}</span>{key === "queue_status" ? <StatusBadge value={String(dashboard[key] ?? "UNKNOWN")} /> : <strong>{String(dashboard[key] ?? "—")}</strong>}</div>)}</section>
      <section className="panel current-service"><p className="eyebrow">Current service</p><h2>{dashboard.current_customer ?? "No customer currently being served"}</h2><p className="muted">This value is provided by the backend queue summary.</p></section>
      <section className="panel">
        <div className="section-heading"><div><p className="eyebrow">Live queue</p><h2>Customers</h2></div><div className="button-row"><button type="button" onClick={() => runOperation("/staff/pause", {}, "Pause queue")} disabled={operation}>Pause Queue</button><button type="button" onClick={() => runOperation("/staff/resume", {}, "Resume queue")} disabled={operation}>Resume Queue</button></div></div>
        {queue.length === 0 ? <EmptyState title="No customers in the queue" message="New customer entries will appear here when they join this branch queue." /> : <div className="table-wrap"><table><caption className="sr-only">Customers in the branch queue</caption><thead><tr><th>Queue Number</th><th>Customer</th><th>Status</th><th>ETA</th><th>Action</th></tr></thead><tbody>{queue.map((entry, index) => <tr key={`${entry.queue_entry_id ?? entry.queue_number ?? "entry"}-${index}`}><td>{entry.queue_number ?? "—"}</td><td>{entry.customer_name ?? "—"}</td><td>{entry.status ? <StatusBadge value={entry.status} /> : "—"}</td><td>{entry.estimated_wait ?? "—"}</td><td>{entry.action && entry.queue_entry_id ? <button type="button" onClick={() => runEntryAction(entry)} disabled={operation}>{entry.action}</button> : "—"}</td></tr>)}</tbody></table></div>}
      </section>
    </>}
  </Shell>;
}
