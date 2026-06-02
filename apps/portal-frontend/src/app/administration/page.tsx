"use client";

import { useEffect, useState } from "react";
import { apiRequest, formatApiError } from "../../lib/api";
import {
  formatNaspModuleStatus,
  formatNaspModuleTechnical,
  healthFieldDisplay,
  inferNaspReachability,
} from "../../lib/administrationDisplay";
import {
  formatNaspModuleLabel,
  PLATFORM_SERVICE_LABELS,
} from "../../lib/operatorLabels";
import { StatusCard } from "../../components/common/StatusCard";

type GlobalHealth = {
  status?: string;
  reachable_modules?: number;
  total_modules?: number;
  reachability_percent?: number;
};

type PlatformHealth = {
  version?: string;
};

type NaspDiagnostics = Record<string, unknown>;

function normalizeError(err: unknown): string {
  return formatApiError(err);
}

const PLATFORM_SERVICE_ENDPOINTS = [
  { key: "GLOBAL_HEALTH", path: "/api/v1/health/global" },
  { key: "NASP_DIAGNOSTICS", path: "/nasp/diagnostics" },
  { key: "PROMETHEUS_SUMMARY", path: "/api/v1/prometheus/summary" },
  { key: "SLA_SUBMIT", path: "/api/v1/sla/submit" },
  { key: "SLA_INTERPRET", path: "/api/v1/sla/interpret" },
] as const;

export default function AdministrationPage() {
  const [globalHealth, setGlobalHealth] = useState<GlobalHealth | null>(null);
  const [platformHealth, setPlatformHealth] = useState<PlatformHealth | null>(null);
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

    Promise.all([
      apiRequest<GlobalHealth>("GLOBAL_HEALTH"),
      apiRequest<PlatformHealth>("PLATFORM_HEALTH"),
    ])
      .then(([global, platform]) => {
        if (cancelled) return;
        setGlobalHealth(global);
        setPlatformHealth(platform);
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

  const naspReachabilityDisplay = inferNaspReachability(nasp);

  const backendDiagnosticItems = [
    {
      label: "Status",
      value:
        globalHealth?.status != null
          ? healthFieldDisplay(globalHealth.status)
          : "Not available",
    },
    {
      label: "Version",
      value: healthFieldDisplay(platformHealth?.version),
    },
    {
      label: "NASP connectivity",
      value: naspReachabilityDisplay,
    },
  ];

  const naspModuleKeys = ["sem_csmf", "ml_nsmf", "decision", "bc_nssmf", "sla_agent"];

  const naspConnectivityItems =
    naspStatus === "ready" && nasp
      ? naspModuleKeys.map((key) => ({
          label: formatNaspModuleLabel(key),
          value: formatNaspModuleStatus(nasp[key]),
        }))
      : [
          {
            label: "Status",
            value:
              naspStatus === "error"
                ? (naspError ?? "Service unavailable")
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
    { label: "Health monitoring", value: "Platform health service" },
  ];

  const platformServiceItems = PLATFORM_SERVICE_ENDPOINTS.map(({ key }) => ({
    label: PLATFORM_SERVICE_LABELS[key] ?? key,
    value: "Operational endpoint",
  }));

  const platformServiceTechnical = PLATFORM_SERVICE_ENDPOINTS.map(({ key, path }) => ({
    label: PLATFORM_SERVICE_LABELS[key] ?? key,
    value: path,
  }));

  const naspTechnicalItems =
    naspStatus === "ready" && nasp
      ? naspModuleKeys.map((key) => ({
          label: `${formatNaspModuleLabel(key)} (probe)`,
          value: formatNaspModuleTechnical(nasp[key]),
        }))
      : [];

  return (
    <section>
      <h1>Administration</h1>
      <p className="trisla-subtitle">Platform health, NASP connectivity, and operational services.</p>
      {(status === "error" || naspStatus === "error") && (
        <p>
          Service unavailable:{" "}
          <span>{error ?? naspError ?? "Unable to reach backend"}</span>
        </p>
      )}
      <div className="trisla-cards-grid">
        <StatusCard title="Backend Diagnostic" items={backendDiagnosticItems} />
        <StatusCard title="NASP Connectivity" items={naspConnectivityItems} />
        <StatusCard title="Runtime Environment" items={runtimeEnvironmentItems} />
        <StatusCard title="Platform Services" items={platformServiceItems} />
      </div>
      <details className="trisla-details" style={{ marginTop: "1.5rem" }}>
        <summary>Technical Details — service endpoints and probe payloads</summary>
        <div className="trisla-cards-grid" style={{ marginTop: "1rem" }}>
          <StatusCard title="Service endpoints" items={platformServiceTechnical} />
          {naspTechnicalItems.length > 0 ? (
            <StatusCard title="NASP probe details" items={naspTechnicalItems} />
          ) : null}
        </div>
      </details>
    </section>
  );
}
