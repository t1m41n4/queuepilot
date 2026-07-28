"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { EmptyState, ErrorState, LoadingState, PageHeader, Shell } from "../../components/ui";
import { get, userFacingError } from "../../lib/api";
import type { Bank } from "../../lib/types";

export default function BanksPage() {
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  useEffect(() => {
    get<Bank[]>("/banks").then(setBanks).catch((reason: unknown) => setError(userFacingError(reason))).finally(() => setLoading(false));
  }, []);

  return <Shell>
    <PageHeader eyebrow="Customer" title="Choose your bank" description="Select a participating bank to find a branch." />
    {loading && <LoadingState label="Loading banks…" />}
    {error && <ErrorState message={error} />}
    {!loading && !error && banks.length === 0 && <EmptyState title="No participating banks" message="There are no banks available right now. Please try again later." />}
    {!loading && !error && banks.length > 0 && <div className="card-grid">{banks.map((bank) => <Link className="selection-card" href={`/banks/${bank.id}/branches`} key={bank.id}><span>{bank.name}</span><span aria-hidden="true">→</span></Link>)}</div>}
  </Shell>;
}
