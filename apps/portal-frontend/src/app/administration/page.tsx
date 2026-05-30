"use client";

import { useEffect, useState } from "react";
import { apiRequest, formatApiError } from "../../lib/api";
import {
  formatNaspModuleStatus,
  healthFieldDisplay,
  inferNaspReachability,
} from "../../lib/administrationDisplay";
import { StatusCard } from "../../components/common/StatusCard";

type HealthV1 = {
  status?: string;
  version?: string;
  nasp_reachable?: boolean | null;
  nasp_details_url?: string | null;
};

type NaspDiagnostics = Record<string, unknown>;

function normalizeError(err: unknown): string {
  return formatApiError(err);
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

  const naspReachabilityDisplay =
    data?.nasp_reachable != null
      ? healthFieldDisplay(data.nasp_reachable)
      : inferNaspReachability(nasp);

  const backendDiagnosticItems = [
    {
      label: "Status",
      value: data?.status != null ? healthFieldDisplay(data.status) : "Not available",
    },
    {
      label: "Version",
      value: healthFieldDisplay(data?.version),
    },
    {
      label: "NASP reachable",
      value: naspReachabilityDisplay,
    },
    {
      label: "NASP details URL",
      value: healthFieldDisplay(data?.nasp_details_url),
    },
  ];

  const naspModuleKeys = ["sem_csmf", "ml_nsmf", "decision", "bc_nssmf", "sla_agent"];

  const naspConnectivityItems =
    naspStatus === "ready" && nasp
      ? naspModuleKeys.map((key) => ({
          label: key,
          value: formatNaspModuleStatus(nasp[key]),
        }))
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
    { label: "Environment", value: envLabel },
    { label: "Health source", value: "Provided by health endpoint" },
  ];

  const apiSurfaceItems = [
    { label: "GLOBAL_HEALTH", value: "/api/v1/health/global" },
    { label: "NASP_DIAGNOSTICS", value: "/nasp/diagnostics" },
    { label: "PROMETHEUS_SUMMARY", value: "/api/v1/prometheus/summary (optional)" },
    { label: "SLA_SUBMIT", value: "/api/v1/sla/submit" },
    { label: "SLA_INTERPRET", value: "/api/v1/sla/interpret" },
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
