"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { ErrorState, PageHeader, Shell } from "../../../components/ui";
import { post, saveAccessToken, userFacingError } from "../../../lib/api";
import type { StaffLoginResponse } from "../../../lib/types";

export default function StaffLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);

  function login() {
    setLoading(true); setError(undefined);
    post<StaffLoginResponse>("/staff/login", { email, password })
      .then((response) => { saveAccessToken(response.access_token); router.push("/staff/dashboard"); })
      .catch((reason: unknown) => setError(userFacingError(reason)))
      .finally(() => setLoading(false));
  }

  return <Shell><PageHeader eyebrow="Staff" title="Staff login" description="Sign in to access branch queue operations." /><section className="panel form-panel"><label htmlFor="staff-email">Email</label><input id="staff-email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} /><label htmlFor="staff-password">Password</label><input id="staff-password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} /><button type="button" onClick={login} disabled={loading || !email || !password}>{loading ? "Signing in…" : "Sign in"}</button>{error && <ErrorState message={error} />}<Link className="back-link" href="/">Return to customer home</Link></section></Shell>;
}
