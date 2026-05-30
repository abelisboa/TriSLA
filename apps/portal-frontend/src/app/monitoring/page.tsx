"use client";

import { useEffect, useMemo, useState } from "react";
import { apiRequest, apiRequestOptional, formatApiError } from "../../lib/api";
import {
  buildCoreDomainCard,
  buildRanDomainCard,
  buildTransportDomainCard,
  domainCardOnError,
  domainCardWhileLoading,
  type DomainCardModel,
  type I1MetricsResponse,
} from "../../lib/domainMonitoringCards";
import {
  isV2FlatSummary,
  legacySummaryDisplayRows,
  type PrometheusSummaryPayload,
  v2SummaryDisplayRows,
} from "../../lib/prometheusSummary";

type LoadStatus = "idle" | "loading" | "ready" | "error";

function DomainCard({
  title,
  card,
  ariaLabel,
}: {
  title: string;
  card: DomainCardModel;
  ariaLabel?: string;
}) {
  return (
    <section className="trisla-status-card" aria-label={ariaLabel ?? title}>
      <h2>{title}</h2>
      <dl>
        {card.rows.map((row) => (
          <div key={row.label} className="trisla-status-row">
            <dt>{row.label}</dt>
            <dd>{row.value}</dd>
          </div>
        ))}
        <div className="trisla-status-row">
          <dt>Data availability</dt>
          <dd>{card.dataAvailability}</dd>
        </div>
      </dl>
    </section>
  );
}

export default function MonitoringPage() {
  const [summary, setSummary] = useState<PrometheusSummaryPayload | null>(null);
  const [summaryStatus, setSummaryStatus] = useState<LoadStatus>("idle");
  const [summaryError, setSummaryError] = useState<string | undefined>(undefined);

  const [ranI1, setRanI1] = useState<I1MetricsResponse | null>(null);
  const [ranStatus, setRanStatus] = useState<LoadStatus>("idle");
  const [ranError, setRanError] = useState<string | undefined>(undefined);

  const [tnI1, setTnI1] = useState<I1MetricsResponse | null>(null);
  const [transportStatus, setTransportStatus] = useState<LoadStatus>("idle");
  const [transportError, setTransportError] = useState<string | undefined>(undefined);

  const [cnI1, setCnI1] = useState<I1MetricsResponse | null>(null);
  const [coreStatus, setCoreStatus] = useState<LoadStatus>("idle");
  const [coreError, setCoreError] = useState<string | undefined>(undefined);

  useEffect(() => {
    let cancelled = false;

    setSummaryStatus("loading");
    setSummaryError(undefined);
    setRanStatus("loading");
    setRanError(undefined);
    setTransportStatus("loading");
    setTransportError(undefined);
    setCoreStatus("loading");
    setCoreError(undefined);

    apiRequestOptional<PrometheusSummaryPayload>("PROMETHEUS_SUMMARY").then(
      ({ data, error }) => {
        if (cancelled) return;
        setSummary(data);
        setSummaryStatus("ready");
        setSummaryError(error ? formatApiError(error) : undefined);
      },
    );

    apiRequest<I1MetricsResponse>("RAN_I1_METRICS")
      .then((response) => {
        if (cancelled) return;
        setRanI1(response);
        setRanStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setRanStatus("error");
        setRanError(formatApiError(err));
      });

    apiRequest<I1MetricsResponse>("TN_I1_METRICS")
      .then((response) => {
        if (cancelled) return;
        setTnI1(response);
        setTransportStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setTransportStatus("error");
        setTransportError(formatApiError(err));
      });

    apiRequest<I1MetricsResponse>("CN_I1_METRICS")
      .then((response) => {
        if (cancelled) return;
        setCnI1(response);
        setCoreStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setCoreStatus("error");
        setCoreError(formatApiError(err));
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

  const summaryCardTitle =
    summary && isV2FlatSummary(summary) ? "Telemetry Summary" : "Prometheus Runtime";

  const ranCard = useMemo(() => {
    if (ranStatus === "loading") return domainCardWhileLoading();
    if (ranStatus === "error") return domainCardOnError(ranError);
    return buildRanDomainCard(ranI1, summary);
  }, [ranI1, ranStatus, ranError, summary]);

  const transportCard = useMemo(() => {
    if (transportStatus === "loading") return domainCardWhileLoading();
    if (transportStatus === "error") return domainCardOnError(transportError);
    return buildTransportDomainCard(tnI1, summary);
  }, [tnI1, transportStatus, transportError, summary]);

  const coreCard = useMemo(() => {
    if (coreStatus === "loading") return domainCardWhileLoading();
    if (coreStatus === "error") return domainCardOnError(coreError);
    return buildCoreDomainCard(cnI1, summary);
  }, [cnI1, coreStatus, coreError, summary]);

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
            </dl>
          ) : summaryStatus === "ready" ? (
            <p className="trisla-muted">Not available</p>
          ) : null}
        </section>
        <DomainCard title="Core Domain" card={coreCard} ariaLabel="Core Domain" />
        <DomainCard title="Transport Domain" card={transportCard} />
        <DomainCard title="RAN Domain" card={ranCard} />
      </div>
    </section>
  );
}
