"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiRequest, apiRequestOptional, formatApiError } from "../lib/api";
import { StatusCard } from "../components/common/StatusCard";
import { DataState } from "../components/common/DataState";
import { fallback } from "../lib/format";
import { AWAITING_DATA } from "../lib/operatorLabels";
import {
  formatModuleOperationalState,
  moduleOperationalLabel,
  normalizeModuleProbe,
} from "../lib/operatorDiagnostics";
import {
  isV2FlatSummary,
  legacySummaryDisplayRows,
  type PrometheusSummaryPayload,
  v2SummaryDisplayRows,
} from "../lib/prometheusSummary";
import {
  aggregateFromDiagnostics,
  formatPlatformReachability,
  parseReachabilityAggregate,
} from "../lib/platformReachability";

type HealthV1 = {
  status?: string;
  version?: string;
  nasp_reachable?: boolean | null;
  nasp_details_url?: string | null;
  reachable_modules?: number;
  total_modules?: number;
  reachability_percent?: number;
};

export default function HomePage() {
  const [data, setData] = useState<HealthV1 | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [error, setError] = useState<string | undefined>(undefined);

  const [summary, setSummary] = useState<PrometheusSummaryPayload | null>(null);
  const [summaryStatus, setSummaryStatus] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [summaryError, setSummaryError] = useState<string | undefined>(undefined);

  const [naspDiagnostics, setNaspDiagnostics] = useState<Record<string, unknown> | null>(null);
  const [naspStatus, setNaspStatus] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [naspError, setNaspError] = useState<string | undefined>(undefined);

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    setSummaryStatus("loading");
    setNaspStatus("loading");

    apiRequest<HealthV1>("GLOBAL_HEALTH")
      .then((response) => {
        if (cancelled) return;
        setData(response);
        setStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setStatus("error");
        setError(formatApiError(err));
      });

    apiRequestOptional<PrometheusSummaryPayload>("PROMETHEUS_SUMMARY").then(({ data, error }) => {
      if (cancelled) return;
      setSummary(data);
      setSummaryStatus("ready");
      setSummaryError(error ? formatApiError(error) : undefined);
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
        setNaspError(formatApiError(err));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const reachabilityAggregate =
    parseReachabilityAggregate(data) ?? aggregateFromDiagnostics(naspDiagnostics);
  const reachabilityLoadState =
    status === "loading" || naspStatus === "loading"
      ? "loading"
      : status === "error" && naspStatus === "error"
        ? "error"
        : "ready";

  const healthItems = [
    { label: "Status", value: String(fallback(data?.status)) },
    { label: "Version", value: String(fallback(data?.version)) },
    {
      label: "Platform Reachability",
      value: formatPlatformReachability(reachabilityAggregate, reachabilityLoadState),
    },
  ];

  const summaryItems =
    summary && !summaryError
      ? isV2FlatSummary(summary)
        ? [
            {
              label: "Prometheus Up",
              value: summary.cpu != null || summary.ran_load != null ? "Operational" : "Not available",
            },
            ...v2SummaryDisplayRows(summary),
          ]
        : legacySummaryDisplayRows(summary)
      : summaryError
        ? [
            { label: "Status", value: "Unavailable" },
            { label: "Detail", value: summaryError },
          ]
        : [{ label: "Status", value: AWAITING_DATA }];

  function moduleItems(key: string) {
    const probe = normalizeModuleProbe(naspDiagnostics?.[key]);
    const opState = formatModuleOperationalState(probe, naspStatus);
    return [
      { label: "Status", value: moduleOperationalLabel(opState) },
      {
        label: "Health check",
        value:
          probe.status_code != null
            ? `HTTP ${String(probe.status_code)}`
            : naspStatus === "error"
              ? "Unavailable"
              : "Not available",
      },
    ];
  }

  return (
    <section>
      <h1>Platform Overview</h1>
      <p className="trisla-subtitle">
        Platform health, NASP modules, and reachability.{" "}
        <Link href="/administration">Administration</Link>.
      </p>
      <div className="trisla-cards-grid">
        <DataState status={status} errorMessage={error}>
          <StatusCard title="Backend Health" items={healthItems} />
        </DataState>
        <DataState status={summaryStatus} errorMessage={summaryError}>
          <StatusCard title="Prometheus Summary" items={summaryItems} />
        </DataState>
        <StatusCard title="Semantic Engine" items={moduleItems("sem_csmf")} />
        <StatusCard title="ML Engine" items={moduleItems("ml_nsmf")} />
        <StatusCard title="BC-NSSMF service health" items={moduleItems("bc_nssmf")} />
      </div>
    </section>
  );
}
