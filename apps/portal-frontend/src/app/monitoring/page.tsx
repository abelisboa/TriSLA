"use client";

import { useEffect, useState } from "react";
import { apiRequest } from "../../lib/api";
import { DataState } from "../../components/common/DataState";
import {
  fallback,
  formatValue,
  prometheusFirstValue,
  formatBytesToMB,
} from "../../lib/format";

/** Payload real: GET /api/v1/prometheus/summary — up, cpu, memory. */
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

function normalizeError(err: unknown): string {
  if (err && typeof err === "object") {
    if (
      "message" in err &&
      typeof (err as { message?: unknown }).message === "string"
    ) {
      return (err as { message: string }).message || "erro ao consultar fonte real";
    }
    if ("status" in err && typeof (err as { status?: unknown }).status === "number") {
      return `HTTP ${(err as { status: number }).status} — erro ao consultar fonte real`;
    }
  }
  return "erro ao consultar fonte real";
}

export default function MonitoringPage() {
  const [summary, setSummary] = useState<PrometheusSummaryReal | null>(null);
  const [summaryStatus, setSummaryStatus] = useState<
    "idle" | "loading" | "ready" | "error"
  >("idle");
  const [summaryError, setSummaryError] = useState<string | undefined>(
    undefined,
  );
  const [transport, setTransport] = useState<Record<string, unknown> | null>(
    null,
  );
  const [transportStatus, setTransportStatus] = useState<
    "idle" | "loading" | "ready" | "error"
  >("idle");
  const [transportError, setTransportError] = useState<string | undefined>(
    undefined,
  );

  const [ran, setRan] = useState<Record<string, unknown> | null>(null);
  const [ranStatus, setRanStatus] = useState<"idle" | "loading" | "ready" | "error">(
    "idle",
  );
  const [ranError, setRanError] = useState<string | undefined>(undefined);

  useEffect(() => {
    let cancelled = false;
    setSummaryStatus("loading");
    setSummaryError(undefined);
    setTransportStatus("loading");
    setTransportError(undefined);
    setRanStatus("loading");
    setRanError(undefined);

    apiRequest<PrometheusSummaryReal>("PROMETHEUS_SUMMARY")
      .then((response) => {
        if (cancelled) return;
        setSummary(response);
        setSummaryStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setSummaryStatus("error");
        setSummaryError(normalizeError(err));
      });

    apiRequest<Record<string, unknown>>("TRANSPORT_METRICS")
      .then((response) => {
        if (cancelled) return;
        setTransport(response);
        setTransportStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setTransportStatus("error");
        setTransportError(normalizeError(err));
      });

    apiRequest<Record<string, unknown>>("RAN_METRICS")
      .then((response) => {
        if (cancelled) return;
        setRan(response);
        setRanStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setRanStatus("error");
        setRanError(normalizeError(err));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const upCount = summary?.up?.data?.result?.length ?? null;
  const prometheusUp =
    summary?.up?.status != null
      ? `${String(fallback(summary.up.status))}${upCount != null ? ` (${upCount} series)` : ""}`
      : "N/A";
  const cpuVal = prometheusFirstValue(summary?.cpu?.data?.result);
  const memoryVal = prometheusFirstValue(summary?.memory?.data?.result);

  const awaitingFeed = "Awaiting validated runtime feed";

  const transportStatusText =
    transportStatus === "ready"
      ? "ok"
      : transportStatus === "error"
        ? "erro ao consultar fonte real"
        : awaitingFeed;

  const transportEndpointState =
    transportStatus === "ready"
      ? formatValue(transport)
      : transportStatus === "error"
        ? formatValue(transportError ?? "erro ao consultar fonte real")
        : awaitingFeed;

  const ranStatusText =
    ranStatus === "ready"
      ? "ok"
      : ranStatus === "error"
        ? "erro ao consultar fonte real"
        : awaitingFeed;

  const ranEndpointState =
    ranStatus === "ready"
      ? formatValue(ran)
      : ranStatus === "error"
        ? formatValue(ranError ?? "erro ao consultar fonte real")
        : awaitingFeed;

  return (
    <section>
      <h1>Monitoring</h1>
      <p className="trisla-subtitle">Multi-domain observability using real backend feed.</p>
      <div className="trisla-cards-grid">
        <DataState status={summaryStatus} errorMessage={summaryError}>
          <section className="trisla-status-card">
            <h2>Prometheus Runtime</h2>
            <dl>
              <div className="trisla-status-row">
                <dt>Prometheus Up</dt>
                <dd>{prometheusUp}</dd>
              </div>
              <div className="trisla-status-row">
                <dt>CPU</dt>
                <dd>{cpuVal !== null ? String(cpuVal) : awaitingFeed}</dd>
              </div>
              <div className="trisla-status-row">
                <dt>Memory</dt>
                <dd>{memoryVal !== null ? formatBytesToMB(memoryVal) : awaitingFeed}</dd>
              </div>
            </dl>
          </section>
        </DataState>
        <section className="trisla-status-card" aria-label="Core Domain">
          <h2>Core Domain</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>No Core metrics endpoint in current API</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Endpoint state</dt>
              <dd>Core metrics not exposed by backend</dd>
            </div>
          </dl>
        </section>
        <section className="trisla-status-card">
          <h2>Transport Domain</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>{transportStatusText}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Endpoint state</dt>
              <dd>{transportEndpointState}</dd>
            </div>
          </dl>
        </section>
        <section className="trisla-status-card">
          <h2>RAN Domain</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>{ranStatusText}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Endpoint state</dt>
              <dd>{ranEndpointState}</dd>
            </div>
          </dl>
        </section>
      </div>
    </section>
  );
}












