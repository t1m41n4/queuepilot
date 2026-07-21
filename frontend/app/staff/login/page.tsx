"use client";

import Link from "next/link";
import { useState } from "react";

import { ErrorState, PageHeader, Shell } from "../../../components/ui";
import { post } from "../../../lib/api";

export default function StaffLoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);

  function login() {
    setLoading(true); setError(undefined);
    post("/staff/login", { email, password }).catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false));
  }

  return <Shell><PageHeader eyebrow="Staff" title="Staff login" description="Sign in to access branch queue operations." /><section className="panel form-panel"><label htmlFor="staff-email">Email</label><input id="staff-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} /><label htmlFor="staff-password">Password</label><input id="staff-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} /><button type="button" onClick={login} disabled={loading || !email || !password}>{loading ? "Signing in…" : "Sign in"}</button>{error && <ErrorState message={error} />}<Link className="back-link" href="/staff/dashboard">Continue to dashboard</Link></section></Shell>;
}
