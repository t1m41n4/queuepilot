"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ErrorState, LoadingState, PageHeader, Shell } from "../../components/ui";
import { get } from "../../lib/api";
import type { Bank } from "../../lib/types";

export default function BanksPage() {
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  useEffect(() => {
    get<Bank[]>("/banks").then(setBanks).catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false));
  }, []);

  return <Shell>
    <PageHeader eyebrow="Customer" title="Choose your bank" description="Select a participating bank to find a branch." />
    {loading && <LoadingState label="Loading banks…" />}
    {error && <ErrorState message={error} />}
    {!loading && !error && <div className="card-grid">{banks.map((bank) => <Link className="selection-card" href={`/banks/${bank.id}/branches`} key={bank.id}><span>{bank.name}</span><span aria-hidden="true">→</span></Link>)}</div>}
  </Shell>;
}
