"use client";

import { useEffect, useState } from "react";
import { apiRequest } from "../../lib/api";
import { DataState } from "../../components/common/DataState";
import { fallback, formatBytesToMB, formatValue, prometheusFirstValue } from "../../lib/format";

type DomainMetrics = unknown;

type Status = "idle" | "loading" | "ready" | "error";

type PrometheusSummaryReal = {
  up?: { status?: string; data?: { result?: Array<{ value?: [number, string] }> } };
  cpu?: { status?: string; data?: { result?: Array<{ value?: [number, string] }> } };
  memory?: { status?: string; data?: { result?: Array<{ value?: [number, string] }> } };
};

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

function MetricDl({ value }: { value: unknown }) {
  if (value === null || value === undefined) return <p>—</p>;
  if (typeof value !== "object") {
    return (
      <dl className="trisla-status-row">
        <dt>value</dt>
        <dd>{formatValue(value)}</dd>
      </dl>
    );
  }
  if (Array.isArray(value)) {
    if (value.length === 0) return <p>—</p>;
    return (
      <dl>
        {value.map((item, i) => (
          <div key={i} className="trisla-status-row">
            <dt>[{i}]</dt>
            <dd>{typeof item === "object" && item !== null ? formatValue(item) : formatValue(item)}</dd>
          </div>
        ))}
      </dl>
    );
  }
  const entries = Object.entries(value as Record<string, unknown>);
  if (entries.length === 0) return <p>—</p>;
  return (
    <dl>
      {entries.map(([k, v]) => (
        <div key={k} className="trisla-status-row">
          <dt>{k}</dt>
          <dd>{formatValue(v)}</dd>
        </div>
      ))}
    </dl>
  );
}

export default function MetricsPage() {
  const [summary, setSummary] = useState<PrometheusSummaryReal | null>(null);
  const [summaryStatus, setSummaryStatus] = useState<Status>("idle");
  const [summaryError, setSummaryError] = useState<string | undefined>(undefined);
  const [transportMetrics, setTransportMetrics] = useState<Record<string, unknown> | null>(
    null,
  );
  const [transportStatus, setTransportStatus] = useState<Status>("idle");
  const [transportError, setTransportError] = useState<string | undefined>(undefined);

  useEffect(() => {
    let cancelled = false;

    setSummaryStatus("loading");
    setSummaryError(undefined);
    setTransportStatus("loading");
    setTransportError(undefined);

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
        setTransportMetrics(response);
        setTransportStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setTransportStatus("error");
        setTransportError(normalizeError(err));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const awaiting = "Awaiting validated runtime feed";
  const cpuVal = prometheusFirstValue(summary?.cpu?.data?.result);
  const memoryVal = prometheusFirstValue(summary?.memory?.data?.result);
  const cpuDisplay = cpuVal !== null ? String(cpuVal) : awaiting;
  const memoryDisplay = memoryVal !== null ? formatBytesToMB(memoryVal) : awaiting;

  return (
    <section>
      <h1>Metrics</h1>
      <p className="trisla-subtitle">Quantitative scientific metrics using only real backend feed.</p>
      <div className="trisla-cards-grid">
        <section className="trisla-status-card">
          <h2>CPU Metrics</h2>
          <DataState status={summaryStatus} errorMessage={summaryError}>
            <dl>
              <div className="trisla-status-row">
                <dt>CPU current value</dt>
                <dd>{cpuDisplay}</dd>
              </div>
            </dl>
          </DataState>
        </section>
        <section className="trisla-status-card">
          <h2>Memory Metrics</h2>
          <DataState status={summaryStatus} errorMessage={summaryError}>
            <dl>
              <div className="trisla-status-row">
                <dt>Memory current value</dt>
                <dd>{memoryDisplay}</dd>
              </div>
            </dl>
          </DataState>
        </section>
        <section className="trisla-status-card">
          <h2>Runtime Throughput</h2>
          <DataState status={transportStatus} errorMessage={transportError}>
            <dl>
              <div className="trisla-status-row">
                <dt>Status</dt>
                <dd>
                  {transportStatus === "ready"
                    ? "no throughput metric exposed (showing transport payload)"
                    : awaiting}
                </dd>
              </div>
              <div className="trisla-status-row">
                <dt>Observed value</dt>
                <dd>
                  {transportStatus === "ready"
                    ? formatValue(transportMetrics)
                    : awaiting}
                </dd>
              </div>
            </dl>
          </DataState>
        </section>
        <section className="trisla-status-card" aria-label="SLA Evidence Feed">
          <h2>SLA Evidence Feed</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>No SLA evidence feed endpoint in current API</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Observed source</dt>
              <dd>SLA evidence feed not exposed by backend</dd>
            </div>
          </dl>
        </section>
      </div>
    </section>
  );
}
