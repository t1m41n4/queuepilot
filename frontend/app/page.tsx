import Link from "next/link";

import { PageHeader, Shell } from "../components/ui";

export default function Home() {
  return <Shell><PageHeader eyebrow="QueuePilot" title="A calmer way to visit your bank" description="Find a branch, join its queue, and keep track of your place." /><div className="hero-actions"><Link className="primary-link" href="/banks">Find a branch</Link><Link className="secondary-link" href="/staff/login">Staff portal</Link></div></Shell>;
}
