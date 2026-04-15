"use client";

import { useEffect, useState } from "react";
import { apiRequest } from "../lib/api";
import { StatusCard } from "../components/common/StatusCard";
import { DataState } from "../components/common/DataState";
import {
  formatValue,
  fallback,
  prometheusFirstValue,
  formatBytesToMB,
} from "../lib/format";

/** Payload real: GET /api/v1/health */
type HealthV1 = {
  status?: string;
  version?: string;
  nasp_reachable?: boolean | null;
  nasp_details_url?: string | null;
};

/** Payload real: GET /api/v1/prometheus/summary — up, cpu, memory (Prometheus query result). */
type PrometheusSummaryReal = {
  up?: {
    status?: string;
    data?: { result?: Array<{ value?: [number, string] }> };
  };
  cpu?: {
    status?: string;
    data?: { result?: Array<{ value?: [number, string] }> };
  };
  memory?: {
    status?: string;
    data?: { result?: Array<{ value?: [number, string] }> };
  };
};

export default function HomePage() {
  const [data, setData] = useState<HealthV1 | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "ready" | "error">(
    "idle",
  );
  const [error, setError] = useState<string | undefined>(undefined);

  const [summary, setSummary] = useState<PrometheusSummaryReal | null>(null);
  const [summaryStatus, setSummaryStatus] = useState<
    "idle" | "loading" | "ready" | "error"
  >("idle");
  const [summaryError, setSummaryError] = useState<string | undefined>(
    undefined,
  );

  const [naspDiagnostics, setNaspDiagnostics] = useState<Record<string, unknown> | null>(
    null,
  );
  const [naspStatus, setNaspStatus] = useState<
    "idle" | "loading" | "ready" | "error"
  >("idle");
  const [naspError, setNaspError] = useState<string | undefined>(undefined);

  function normalizeModuleProbe(moduleProbe: unknown): {
    reachable: boolean | null;
    status_code: unknown;
    detail: unknown;
  } {
    if (!moduleProbe || typeof moduleProbe !== "object") {
      return { reachable: null, status_code: null, detail: null };
    }
    const obj = moduleProbe as Record<string, unknown>;
    return {
      reachable: typeof obj.reachable === "boolean" ? (obj.reachable as boolean) : null,
      status_code: obj.status_code ?? null,
      detail: obj.detail ?? null,
    };
  }

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    setError(undefined);
    setSummaryStatus("loading");
    setSummaryError(undefined);
    setNaspStatus("loading");
    setNaspError(undefined);

    apiRequest<HealthV1>("GLOBAL_HEALTH")
      .then((response) => {
        if (cancelled) return;
        setData(response);
        setStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setStatus("error");
        setError(err instanceof Error ? err.message : "unknown error");
      });

    apiRequest<PrometheusSummaryReal>("PROMETHEUS_SUMMARY")
      .then((response) => {
        if (cancelled) return;
        setSummary(response);
        setSummaryStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setSummaryStatus("error");
        setSummaryError(err instanceof Error ? err.message : "unknown error");
      });

    apiRequest<Record<string, unknown>>("NASP_DIAGNOSTICS")
      .then((response) => {
        if (cancelled) return;
        setNaspDiagnostics(response);
        setNaspStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setNaspStatus("error");
        setNaspError(err instanceof Error ? err.message : "erro ao consultar fonte real");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const healthItems = [
    { label: "Status", value: String(fallback(data?.status)) },
    { label: "Versão", value: String(fallback(data?.version)) },
    {
      label: "NASP reachable",
      value: formatValue(data?.nasp_reachable ?? "N/A"),
    },
    {
      label: "NASP details URL",
      value: String(fallback(data?.nasp_details_url)),
    },
  ];

  const upCount =
    summary?.up?.data?.result?.length ?? null;
  const prometheusUpDisplay =
    summary?.up?.status != null
      ? `${String(fallback(summary.up.status))}${upCount != null ? ` (${upCount} series)` : ""}`
      : "N/A";
  const cpuVal = prometheusFirstValue(summary?.cpu?.data?.result);
  const memoryVal = prometheusFirstValue(summary?.memory?.data?.result);

  const summaryItems = [
    { label: "Prometheus Up", value: prometheusUpDisplay },
    {
      label: "CPU",
      value: cpuVal !== null ? String(cpuVal) : "N/A",
    },
    {
      label: "Memory",
      value: formatBytesToMB(memoryVal),
    },
  ];

  const semanticEngineItems = [
    {
      label: "Status",
      value: "Awaiting runtime feed",
    },
  ];

  const mlEngineItems = [
    {
      label: "Status",
      value: "Awaiting runtime feed",
    },
  ];

  const bcProbe = normalizeModuleProbe(naspDiagnostics?.["bc_nssmf"] ?? null);
  const bcStatusText =
    naspStatus === "loading"
      ? "Awaiting validated runtime feed"
      : naspStatus === "error"
        ? "erro ao consultar fonte real"
        : bcProbe.reachable === true
          ? "reachable"
          : bcProbe.reachable === false
            ? "unreachable"
            : "Awaiting validated runtime feed";

  const bcEndpointState =
    naspStatus === "ready"
      ? formatValue({ status_code: bcProbe.status_code, detail: bcProbe.detail })
      : naspStatus === "error"
        ? formatValue(naspError ?? "erro ao consultar fonte real")
        : "Awaiting validated runtime feed";

  const blockchainItemsControlled = [
    { label: "Status", value: bcStatusText },
    { label: "Endpoint state", value: bcEndpointState },
  ];

  const semCsmf = (naspDiagnostics?.["sem_csmf"] ?? null) as
    | Record<string, unknown>
    | null;
  const semReachable =
    semCsmf && typeof semCsmf === "object" ? semCsmf["reachable"] : null;
  const semStatusText =
    naspStatus === "loading"
      ? "Awaiting validated runtime feed"
      : naspStatus === "error"
        ? "erro ao consultar fonte real"
        : semReachable === true
          ? "reachable"
          : semReachable === false
            ? "unreachable"
            : "Awaiting validated runtime feed";

  const semEndpointState =
    naspStatus === "ready" && semCsmf
      ? formatValue({
          status_code: (semCsmf as Record<string, unknown>)["status_code"],
          detail: (semCsmf as Record<string, unknown>)["detail"],
        })
      : naspStatus === "error"
        ? formatValue(naspError ?? "erro ao consultar fonte real")
        : "Awaiting validated runtime feed";

  const semanticEngineItemsControlled = [
    { label: "Status", value: semStatusText },
    { label: "Endpoint state", value: semEndpointState },
  ];

  const mlProbe = normalizeModuleProbe(naspDiagnostics?.["ml_nsmf"] ?? null);
  const mlStatusText =
    naspStatus === "loading"
      ? "Awaiting validated runtime feed"
      : naspStatus === "error"
        ? "erro ao consultar fonte real"
        : mlProbe.reachable === true
          ? "reachable"
          : mlProbe.reachable === false
            ? "unreachable"
            : "Awaiting validated runtime feed";

  const mlEndpointState =
    naspStatus === "ready"
      ? formatValue({ status_code: mlProbe.status_code, detail: mlProbe.detail })
      : naspStatus === "error"
        ? formatValue(naspError ?? "erro ao consultar fonte real")
        : "Awaiting validated runtime feed";

  const mlEngineItemsControlled = [
    { label: "Status", value: mlStatusText },
    { label: "Endpoint state", value: mlEndpointState },
  ];

  return (
    <section>
      <h1>Home</h1>
      <p className="trisla-subtitle">Scientific executive backend overview.</p>
      <div className="trisla-cards-grid">
        <DataState status={status} errorMessage={error}>
          <StatusCard title="Backend Health" items={healthItems} />
        </DataState>
        <DataState status={summaryStatus} errorMessage={summaryError}>
          <StatusCard
            title="Prometheus Summary"
            items={summaryItems}
          />
        </DataState>
        <StatusCard
          title="Semantic Engine"
          items={semanticEngineItemsControlled}
        />
        <StatusCard title="ML Engine" items={mlEngineItemsControlled} />
        <StatusCard
          title="Blockchain Governance"
          items={blockchainItemsControlled}
        />
      </div>
    </section>
  );
}
