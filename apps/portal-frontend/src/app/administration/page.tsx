"use client";

import { useEffect, useState } from "react";
import { apiRequest } from "../../lib/api";
import { StatusCard } from "../../components/common/StatusCard";
import { formatValue } from "../../lib/format";

type HealthV1 = {
  status?: string;
  version?: string;
  nasp_reachable?: boolean | null;
  nasp_details_url?: string | null;
};

type NaspDiagnostics = Record<string, unknown>;

function normalizeError(err: unknown): string {
  if (err && typeof err === "object") {
    if ("message" in err && typeof (err as { message?: unknown }).message === "string") {
      return (err as { message: string }).message || "erro ao consultar fonte real";
    }
    if ("status" in err && typeof (err as { status?: unknown }).status === "number") {
      return `HTTP ${(err as { status: number }).status} — erro ao consultar fonte real`;
    }
  }
  return "erro ao consultar fonte real";
}

export default function AdministrationPage() {
  const [data, setData] = useState<HealthV1 | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "ready" | "error">(
    "idle",
  );
  const [error, setError] = useState<string | undefined>(undefined);

  const [nasp, setNasp] = useState<NaspDiagnostics | null>(null);
  const [naspStatus, setNaspStatus] = useState<
    "idle" | "loading" | "ready" | "error"
  >("idle");
  const [naspError, setNaspError] = useState<string | undefined>(undefined);

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    setError(undefined);

    apiRequest<HealthV1>("GLOBAL_HEALTH")
      .then((response) => {
        if (cancelled) return;
        setData(response);
        setStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setStatus("error");
        setError(normalizeError(err));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setNaspStatus("loading");
    setNaspError(undefined);

    apiRequest<NaspDiagnostics>("NASP_DIAGNOSTICS")
      .then((response) => {
        if (cancelled) return;
        setNasp(response);
        setNaspStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setNaspStatus("error");
        setNaspError(normalizeError(err));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const backendDiagnosticItems = [
    { label: "Status", value: formatValue(data?.status) },
    { label: "Version", value: formatValue(data?.version) },
    { label: "NASP reachable", value: formatValue(data?.nasp_reachable) },
    { label: "NASP details URL", value: formatValue(data?.nasp_details_url) },
  ];

  const naspConnectivityItems =
    naspStatus === "ready" && nasp
      ? [
          { label: "sem_csmf", value: formatValue(nasp["sem_csmf"]) },
          { label: "ml_nsmf", value: formatValue(nasp["ml_nsmf"]) },
          { label: "decision", value: formatValue(nasp["decision"]) },
          { label: "bc_nssmf", value: formatValue(nasp["bc_nssmf"]) },
          { label: "sla_agent", value: formatValue(nasp["sla_agent"]) },
        ]
      : [
          {
            label: "Status",
            value:
              naspStatus === "error"
                ? (naspError ?? "erro ao consultar fonte real")
                : naspStatus === "loading"
                  ? "Loading…"
                  : "No NASP data",
          },
        ];

  const envLabel =
    process.env.NEXT_PUBLIC_TRISLA_ENV ||
    process.env.NEXT_PUBLIC_ENV ||
    "local";

  const runtimeEnvironmentItems = [
    { label: "Environment", value: formatValue(envLabel) },
  ];

  const apiSurfaceItems = [
    { label: "GLOBAL_HEALTH", value: "/api/v1/health/global" },
    { label: "PROMETHEUS_SUMMARY", value: "/api/v1/prometheus/summary" },
  ];

  return (
    <section>
      <h1>Administration</h1>
      <p className="trisla-subtitle">Executive backend and NASP diagnostics.</p>
      {(status === "error" || naspStatus === "error") && (
        <p>
          Fonte indisponível:{" "}
          <span>{error ?? naspError ?? "erro ao consultar fonte real"}</span>
        </p>
      )}
      <div className="trisla-cards-grid">
        <StatusCard title="Backend Diagnostic" items={backendDiagnosticItems} />
        <StatusCard title="NASP Connectivity" items={naspConnectivityItems} />
        <StatusCard title="Runtime Environment" items={runtimeEnvironmentItems} />
        <StatusCard title="API Surface" items={apiSurfaceItems} />
      </div>
    </section>
  );
}
