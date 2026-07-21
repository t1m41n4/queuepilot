"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { ErrorState, LoadingState, PageHeader, Shell } from "../../../../components/ui";
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
    <PageHeader eyebrow="Customer · Branches" title="Choose a branch" description="Select the branch where you would like service." />
    {loading && <LoadingState label="Loading branches..." />}
    {error && <ErrorState message={error} />}
    {!loading && !error && <div className="card-grid">{branches.map((branch) => <Link className="selection-card" href={`/queue?branchId=${branch.id}&branchName=${encodeURIComponent(branch.name)}`} key={branch.id}>
      <span><strong>{branch.name}</strong><small>{branch.queue_status === "OPEN" ? `${branch.estimated_wait} minute${branch.estimated_wait === 1 ? "" : "s"} estimated wait` : branch.queue_status === "PAUSED" ? "Queue Paused" : "Unavailable"}</small>{branch.recommended && <small className="recommendation-badge">Recommended</small>}</span><span aria-hidden="true">-&gt;</span>
    </Link>)}</div>}
  </Shell>;
}
