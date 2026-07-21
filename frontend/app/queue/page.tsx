"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AssistantPanel, ErrorState, PageHeader, Shell } from "../../components/ui";
import { get, post } from "../../lib/api";
import type { AssistantResponse, QueueJoinResponse, QueueStatusResponse } from "../../lib/types";

export default function QueuePage() {
  const [branchId, setBranchId] = useState<number>();
  const [branchName, setBranchName] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [queueEntryId, setQueueEntryId] = useState<number>();
  const [status, setStatus] = useState<QueueStatusResponse | QueueJoinResponse>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string>();
  const [assistantError, setAssistantError] = useState<string>();
  const [assistantLoading, setAssistantLoading] = useState(false);

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    const parsedBranchId = Number(query.get("branchId"));
    if (Number.isFinite(parsedBranchId) && parsedBranchId > 0) setBranchId(parsedBranchId);
    setBranchName(query.get("branchName") ?? "");
  }, []);

  useEffect(() => {
    if (!queueEntryId) return;
    get<QueueStatusResponse>(`/queue/${queueEntryId}`).then(setStatus).catch((reason: Error) => setError(reason.message));
  }, [queueEntryId]);

  function joinQueue() {
    if (!branchId || !customerName.trim()) return;
    setLoading(true); setError(undefined);
    post<QueueJoinResponse>("/queue/join", { branch_id: branchId, customer_name: customerName.trim() })
      .then((response) => { setQueueEntryId(response.queue_entry_id); setStatus(response); })
      .catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false));
  }

  function cancelQueue() {
    if (!queueEntryId) return;
    setLoading(true); setError(undefined);
    post<{ message: string }>(`/queue/${queueEntryId}/cancel`, {})
      .then(() => setStatus((current) => current && { ...current, status: "CANCELLED" }))
      .catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false));
  }

  function askAssistant() {
    if (!queueEntryId || !question.trim()) return;
    setAssistantLoading(true); setAssistantError(undefined);
    post<AssistantResponse>("/assistant/chat", { queue_entry_id: queueEntryId, question: question.trim() })
      .then((response) => setAnswer(response.answer)).catch((reason: Error) => setAssistantError(reason.message)).finally(() => setAssistantLoading(false));
  }

  const joinedStatus = status && "queue_number" in status ? status : undefined;
  return <Shell>
    <Link className="back-link" href="/banks">← Change branch</Link>
    <PageHeader eyebrow="Customer · Queue" title={joinedStatus ? "Your queue status" : "Join a queue"} description={branchName ? `Selected branch: ${branchName}` : "Select a branch before joining."} />
    {error && <ErrorState message={error} />}
    {!joinedStatus ? <section className="panel form-panel"><label htmlFor="customer-name">Customer name</label><input id="customer-name" value={customerName} onChange={(event) => setCustomerName(event.target.value)} placeholder="Enter your name" /><button type="button" onClick={joinQueue} disabled={loading || !branchId || !customerName.trim()}>{loading ? "Joining…" : "Join Queue"}</button></section> : <><section className="status-grid">{[[("Queue number"), joinedStatus.queue_number], [("Branch"), "branch_name" in joinedStatus ? joinedStatus.branch_name : branchName], [("Position"), "position" in joinedStatus ? joinedStatus.position : "—"], [("Estimated wait"), "estimated_wait" in joinedStatus ? `${joinedStatus.estimated_wait} minutes` : "—"], [("Status"), joinedStatus.status]].map(([label, value]) => <div className="metric-card" key={label as string}><span>{label}</span><strong>{value}</strong></div>)}</section><button className="danger-button" type="button" onClick={cancelQueue} disabled={loading || joinedStatus.status === "CANCELLED"}>{loading ? "Updating…" : "Cancel Queue"}</button><AssistantPanel question={question} setQuestion={setQuestion} onSend={askAssistant} answer={answer} loading={assistantLoading} error={assistantError} /></>}
  </Shell>;
}
