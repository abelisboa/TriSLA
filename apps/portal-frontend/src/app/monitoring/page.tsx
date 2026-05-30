"use client";

import { useEffect, useState } from "react";
import { apiRequest, apiRequestOptional, formatApiError } from "../../lib/api";
import {
  formatDomainMetricsState,
  isV2FlatSummary,
  legacySummaryDisplayRows,
  type PrometheusSummaryPayload,
  v2SummaryDisplayRows,
} from "../../lib/prometheusSummary";

function normalizeError(err: unknown): string {
  return formatApiError(err);
}

export default function MonitoringPage() {
  const [summary, setSummary] = useState<PrometheusSummaryPayload | null>(null);
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

    apiRequestOptional<PrometheusSummaryPayload>("PROMETHEUS_SUMMARY")
      .then(({ data, error }) => {
        if (cancelled) return;
        setSummary(data);
        setSummaryStatus("ready");
        setSummaryError(error ? normalizeError(error) : undefined);
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

  const summaryRows = summary
    ? isV2FlatSummary(summary)
      ? v2SummaryDisplayRows(summary)
      : legacySummaryDisplayRows(summary)
    : [];

  const summaryCardTitle = summary && isV2FlatSummary(summary)
    ? "Telemetry Summary (v2)"
    : "Prometheus Runtime";

  const transportStatusText =
    transportStatus === "ready"
      ? "ok"
      : transportStatus === "error"
        ? "erro ao consultar fonte real"
        : transportStatus === "loading"
          ? "Loading…"
          : "Not available";

  const transportEndpointState = formatDomainMetricsState(
    transport,
    transportStatus,
    transportError,
  );

  const ranStatusText =
    ranStatus === "ready"
      ? "ok"
      : ranStatus === "error"
        ? "erro ao consultar fonte real"
        : ranStatus === "loading"
          ? "Loading…"
          : "Not available";

  const ranEndpointState = formatDomainMetricsState(ran, ranStatus, ranError);

  return (
    <section>
      <h1>Monitoring</h1>
      <p className="trisla-subtitle">Multi-domain observability using real backend feed.</p>
      <div className="trisla-cards-grid">
        <section className="trisla-status-card">
          <h2>{summaryCardTitle}</h2>
          {summaryError ? (
            <p className="trisla-muted">Monitoring summary unavailable: {summaryError}</p>
          ) : null}
          {summaryStatus === "loading" ? (
            <p className="trisla-muted">Loading…</p>
          ) : summaryStatus === "ready" && summaryRows.length > 0 ? (
            <dl>
              {summaryRows.map((row) => (
                <div key={row.label} className="trisla-status-row">
                  <dt>{row.label}</dt>
                  <dd>{row.value}</dd>
                </div>
              ))}
              {summary?.metadata?.telemetry_version ? (
                <div className="trisla-status-row">
                  <dt>Telemetry version</dt>
                  <dd>{summary.metadata.telemetry_version}</dd>
                </div>
              ) : null}
            </dl>
          ) : summaryStatus === "ready" ? (
            <p className="trisla-muted">Not available</p>
          ) : null}
        </section>
        <section className="trisla-status-card" aria-label="Core Domain">
          <h2>Core Domain</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>Not available</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Service</dt>
              <dd>Core domain metrics not configured on this platform</dd>
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
