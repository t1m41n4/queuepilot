"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { EmptyState, ErrorState, LoadingState, PageHeader, Shell } from "../../../../components/ui";
import { get, userFacingError } from "../../../../lib/api";
import type { Branch } from "../../../../lib/types";

export default function BranchesPage() {
  const params = useParams<{ bankId: string }>();
  const [branches, setBranches] = useState<Branch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  useEffect(() => {
    get<Branch[]>(`/banks/${params.bankId}/branches`)
      .then(setBranches)
      .catch((reason: unknown) => setError(userFacingError(reason)))
      .finally(() => setLoading(false));
  }, [params.bankId]);

  return <Shell>
    <Link className="back-link" href="/banks">← Change bank</Link>
    <PageHeader eyebrow="Customer · Branches" title="Choose a branch" description="Select the branch where you would like service." />
    {loading && <LoadingState label="Loading branches…" />}
    {error && <ErrorState message={error} />}
    {!loading && !error && branches.length === 0 && <EmptyState title="No branches available" message="This bank has no participating branches right now. Please choose another bank." />}
    {!loading && !error && branches.length > 0 && <div className="card-grid">{branches.map((branch) => {
      const available = branch.queue_status === "OPEN";
      const content = <><span><strong>{branch.name}</strong><small>{available ? `${branch.estimated_wait} minute${branch.estimated_wait === 1 ? "" : "s"} estimated wait` : branch.queue_status === "PAUSED" ? "Queue Paused — unavailable for joining" : "Unavailable for joining"}</small>{branch.recommended && available && <small className="recommendation-badge">Recommended</small>}</span><span aria-hidden="true">{available ? "→" : "—"}</span></>;
      return available ? <Link className="selection-card" href={`/queue?branchId=${branch.id}&branchName=${encodeURIComponent(branch.name)}`} key={branch.id}>{content}</Link> : <div className="selection-card unavailable-card" aria-disabled="true" key={branch.id}>{content}</div>;
    })}</div>}
  </Shell>;
}
