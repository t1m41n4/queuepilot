"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { ErrorState, LoadingState, PageHeader, Shell } from "../../../../components/ui";
import { get } from "../../../../lib/api";
import type { Branch } from "../../../../lib/types";

export default function BranchesPage() {
  const params = useParams<{ bankId: string }>();
  const [branches, setBranches] = useState<Branch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  useEffect(() => {
    get<Branch[]>(`/banks/${params.bankId}/branches`).then(setBranches).catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false));
  }, [params.bankId]);

  return <Shell>
    <PageHeader eyebrow="Customer · Branches" title="Choose a branch" description="Select the branch where you would like service." />
    {loading && <LoadingState label="Loading branches…" />}
    {error && <ErrorState message={error} />}
    {!loading && !error && <div className="card-grid">{branches.map((branch) => <Link className="selection-card" href={`/queue?branchId=${branch.id}&branchName=${encodeURIComponent(branch.name)}`} key={branch.id}><span>{branch.name}</span><span aria-hidden="true">→</span></Link>)}</div>}
  </Shell>;
}
