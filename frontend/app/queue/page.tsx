"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AssistantPanel, ErrorState, PageHeader, Shell } from "../../components/ui";
import { get, post, userFacingError, websocketUrl } from "../../lib/api";
import type { AssistantResponse, QueueJoinResponse, QueueStatusResponse } from "../../lib/types";

export default function QueuePage() {
  const [branchId, setBranchId] = useState<number>();
  const [branchName, setBranchName] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [queueEntryId, setQueueEntryId] = useState<number>();
  const [status, setStatus] = useState<QueueStatusResponse | QueueJoinResponse>();
  const [loading, setLoading] = useState(false);
  const [statusLoading, setStatusLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string>();
  const [assistantError, setAssistantError] = useState<string>();
  const [assistantLoading, setAssistantLoading] = useState(false);
  const [connectionState, setConnectionState] = useState<"connecting" | "connected" | "disconnected">("disconnected");
  const [connectionError, setConnectionError] = useState<string>();

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    const parsedBranchId = Number(query.get("branchId"));
    if (Number.isFinite(parsedBranchId) && parsedBranchId > 0) setBranchId(parsedBranchId);
    setBranchName(query.get("branchName") ?? "");
  }, []);

  useEffect(() => {
    if (!queueEntryId) return;
    setStatusLoading(true);
    get<QueueStatusResponse>(`/queue/${queueEntryId}`).then(setStatus).catch((reason: unknown) => setError(userFacingError(reason))).finally(() => setStatusLoading(false));
  }, [queueEntryId]);

  useEffect(() => {
    if (!branchId) return;
    let socket: WebSocket | undefined;
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
    let stopped = false;

    const connect = () => {
      if (stopped) return;
      setConnectionState("connecting");
      socket = new WebSocket(websocketUrl(`/ws/queue/${branchId}`));
      socket.onopen = () => { setConnectionState("connected"); setConnectionError(undefined); };
      socket.onmessage = (message) => {
        try {
          const update = JSON.parse(message.data) as { event?: string; state?: { status?: string } };
          if (!["QUEUE_UPDATED", "READY", "CALLED", "QUEUE_PAUSED", "QUEUE_RESUMED"].includes(update.event ?? "")) return;
          if (update.event === "QUEUE_PAUSED" || update.event === "QUEUE_RESUMED") {
            setStatus((current) => current ? { ...current, status: update.state?.status ?? current.status } : current);
          } else if (queueEntryId) {
            setStatusLoading(true);
            get<QueueStatusResponse>(`/queue/${queueEntryId}`).then(setStatus).catch((reason: unknown) => setError(userFacingError(reason))).finally(() => setStatusLoading(false));
          }
        } catch {
          setConnectionError("Received an invalid queue update.");
        }
      };
      socket.onerror = () => { setConnectionState("disconnected"); setConnectionError("Live queue updates are unavailable."); };
      socket.onclose = () => {
        setConnectionState("disconnected");
        if (!stopped) reconnectTimer = setTimeout(connect, 3000);
      };
    };

    connect();
    return () => { stopped = true; if (reconnectTimer) clearTimeout(reconnectTimer); socket?.close(); };
  }, [branchId, queueEntryId]);

  function joinQueue() {
    if (!branchId || !customerName.trim()) return;
    setLoading(true); setError(undefined);
    post<QueueJoinResponse>("/queue/join", { branch_id: branchId, customer_name: customerName.trim() })
      .then((response) => { setQueueEntryId(response.queue_entry_id); setStatus(response); })
      .catch((reason: unknown) => setError(userFacingError(reason))).finally(() => setLoading(false));
  }

  function cancelQueue() {
    if (!queueEntryId) return;
    setLoading(true); setError(undefined);
    post<{ message: string }>(`/queue/${queueEntryId}/cancel`, {})
      .then(() => setStatus((current) => current && { ...current, status: "CANCELLED" }))
      .catch((reason: unknown) => setError(userFacingError(reason))).finally(() => setLoading(false));
  }

  function askAssistant() {
    if (!queueEntryId || !question.trim()) return;
    setAssistantLoading(true); setAssistantError(undefined);
    post<AssistantResponse>("/assistant/chat", { queue_entry_id: queueEntryId, question: question.trim() })
      .then((response) => setAnswer(response.answer)).catch((reason: unknown) => setAssistantError(userFacingError(reason))).finally(() => setAssistantLoading(false));
  }

  const joinedStatus = status && "queue_number" in status ? status : undefined;
  return <Shell>
    <Link className="back-link" href="/banks">← Change branch</Link>
    <PageHeader eyebrow="Customer · Queue" title={joinedStatus ? "Your queue status" : "Join a queue"} description={branchName ? `Selected branch: ${branchName}` : "Select a branch before joining."} />
    {error && <ErrorState message={error} />}
    {statusLoading && <p className="connection-status" role="status">Refreshing queue status…</p>}
    {connectionError && <ErrorState message={connectionError} />}
    {branchId && <p className="connection-status" role="status">Live updates: {connectionState}</p>}
    {!joinedStatus ? <section className="panel form-panel"><label htmlFor="customer-name">Customer name</label><input id="customer-name" value={customerName} onChange={(event) => setCustomerName(event.target.value)} placeholder="Enter your name" /><button type="button" onClick={joinQueue} disabled={loading || !branchId || !customerName.trim()}>{loading ? "Joining…" : "Join Queue"}</button></section> : <><section className="status-grid">{[[("Queue number"), joinedStatus.queue_number], [("Branch"), "branch_name" in joinedStatus ? joinedStatus.branch_name : branchName], [("Position"), "position" in joinedStatus ? joinedStatus.position : "—"], [("Estimated wait"), "estimated_wait" in joinedStatus ? `${joinedStatus.estimated_wait} minutes` : "—"], [("Status"), joinedStatus.status]].map(([label, value]) => <div className="metric-card" key={label as string}><span>{label}</span><strong>{value}</strong></div>)}</section><button className="danger-button" type="button" onClick={cancelQueue} disabled={loading || joinedStatus.status === "CANCELLED"}>{loading ? "Updating…" : "Cancel Queue"}</button><AssistantPanel question={question} setQuestion={setQuestion} onSend={askAssistant} answer={answer} loading={assistantLoading} error={assistantError} /></>}
  </Shell>;
}
