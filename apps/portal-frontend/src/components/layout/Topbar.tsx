"use client";

import { useEffect, useState } from "react";

export function Topbar() {
  const [runtimeTimestamp, setRuntimeTimestamp] = useState<string>(
    () => new Date().toISOString(),
  );

  useEffect(() => {
    const id = setInterval(() => {
      setRuntimeTimestamp(new Date().toISOString());
    }, 60_000);
    return () => clearInterval(id);
  }, []);

  const envLabel =
    process.env.NEXT_PUBLIC_TRISLA_ENV ||
    process.env.NEXT_PUBLIC_ENV ||
    "local";

  return (
    <header className="trisla-topbar">
      <div className="trisla-topbar-title">
        <span>TriSLA Scientific Portal</span>
        <span className="trisla-topbar-subtitle">
          SLA-Centric Scientific Interface
        </span>
      </div>
      <div className="trisla-topbar-right">
        <span className="trisla-topbar-env" aria-label="Environment label">
          {envLabel}
        </span>
        <span className="trisla-topbar-badge trisla-topbar-badge-nasp">
          NASP
        </span>
        <span
          className="trisla-topbar-runtime"
          aria-label="Frontend runtime timestamp (ISO8601)"
        >
          {runtimeTimestamp}
        </span>
      </div>
    </header>
  );
}
