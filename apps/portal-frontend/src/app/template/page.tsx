"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { apiRequest } from "../../lib/api";
import { DataState } from "../../components/common/DataState";
import { formatValue } from "../../lib/format";

function ObjectDl({ value }: { value: unknown }) {
  if (value === null || value === undefined) return <span>—</span>;
  if (typeof value !== "object") return <span>{formatValue(value)}</span>;
  if (Array.isArray(value) && value.length === 0) return <span>—</span>;
  if (Array.isArray(value)) {
    return (
      <dl>
        {value.map((item, i) => (
          <div key={i} className="trisla-status-row">
            <dt>[{i}]</dt>
            <dd>{formatValue(item)}</dd>
          </div>
        ))}
      </dl>
    );
  }
  const entries = Object.entries(value as Record<string, unknown>);
  if (entries.length === 0) return <span>—</span>;
  return (
    <dl>
      {entries.map(([k, v]) => (
        <div key={k} className="trisla-status-row">
          <dt>{k}</dt>
          <dd>{typeof v === "object" && v !== null ? formatValue(v) : formatValue(v)}</dd>
        </div>
      ))}
    </dl>
  );
}

/** Resposta real do POST /api/v1/sla/submit — campos oficiais + XAI profundo */
type SubmitResponse = {
  decision: string;
  status?: string;
  reason?: string | null;
  justification?: string | null;
  sla_id?: string | null;
  intent_id?: string | null;
  nest_id?: string | null;
  service_type?: string | null;
  timestamp?: string | null;
  sla_requirements?: unknown;
  ml_prediction?: Record<string, unknown> | null;
  tx_hash?: string | null;
  block_number?: number | null;
  bc_status?: string | null;
  reasoning?: string;
  confidence?: number;
  domains?: string[];
  metadata?: Record<string, unknown>;
};

type Status = "idle" | "loading" | "ready" | "error";

function buildFormValues(fields: Record<string, string>): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  Object.entries(fields).forEach(([key, value]) => {
    const trimmed = value.trim();
    if (!trimmed) return;
    if (["latency", "throughput"].includes(key)) {
      const num = Number(trimmed);
      result[key] = Number.isFinite(num) ? num : trimmed;
      return;
    }
    if (["availability", "reliability"].includes(key)) {
      const num = Number(trimmed);
      result[key] = Number.isFinite(num) ? num : trimmed;
      return;
    }
    result[key] = trimmed;
  });
  return result;
}

export default function CreateSlaTemplatePage() {
  const [templateId, setTemplateId] = useState("");
  const [tenantId, setTenantId] = useState("");
  const [serviceName, setServiceName] = useState("");
  const [sliceType, setSliceType] = useState("");
  const [latency, setLatency] = useState("");
  const [throughput, setThroughput] = useState("");
  const [availability, setAvailability] = useState("");
  const [reliability, setReliability] = useState("");
  const [priority, setPriority] = useState("");

  const [result, setResult] = useState<SubmitResponse | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | undefined>(undefined);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!templateId.trim()) {
      setError("Template ID não pode ser vazio");
      setStatus("error");
      return;
    }
    if (!tenantId.trim()) {
      setError("Tenant ID não pode ser vazio");
      setStatus("error");
      return;
    }
    setStatus("loading");
    setError(undefined);
    setResult(null);

    const formValues = buildFormValues({
      service_name: serviceName,
      slice_type: sliceType,
      latency,
      throughput,
      availability,
      reliability,
      priority,
    });

    try {
      const response = await apiRequest<SubmitResponse>("SLA_SUBMIT", {
        method: "POST",
        body: {
          template_id: templateId,
          tenant_id: tenantId,
          form_values: formValues,
        },
      });
      setResult(response);
      setStatus("ready");
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "unknown error");
    }
  }

  const ml = result?.ml_prediction ?? null;

  return (
    <section>
      <h1>Template</h1>
      <p className="trisla-subtitle">Structured SLA submission — official pipeline only. Campos conforme matriz.</p>

      <section className="trisla-status-card" aria-label="Template Real Feed">
        <h2>Template Real Feed</h2>
        <dl>
          <div className="trisla-status-row">
            <dt>Template source</dt>
            <dd>No template list endpoint in current API</dd>
          </div>
          <div className="trisla-status-row">
            <dt>Available templates</dt>
            <dd>Template list not exposed by backend</dd>
          </div>
        </dl>
      </section>

      <form onSubmit={handleSubmit} className="trisla-form">
        <div className="trisla-form-row">
          <label htmlFor="template_id">Template ID</label>
          <input
            id="template_id"
            type="text"
            value={templateId}
            onChange={(e) => setTemplateId(e.target.value)}
          />
        </div>
        <div className="trisla-form-row">
          <label htmlFor="tenant_id">Tenant ID</label>
          <input
            id="tenant_id"
            type="text"
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
          />
        </div>
        <div className="trisla-form-row">
          <label htmlFor="service_name">Service name</label>
          <input id="service_name" type="text" value={serviceName} onChange={(e) => setServiceName(e.target.value)} />
        </div>
        <div className="trisla-form-row">
          <label htmlFor="slice_type">Slice type</label>
          <input id="slice_type" type="text" value={sliceType} onChange={(e) => setSliceType(e.target.value)} />
        </div>
        <div className="trisla-form-row">
          <label htmlFor="latency">Latency</label>
          <input id="latency" type="number" value={latency} onChange={(e) => setLatency(e.target.value)} />
        </div>
        <div className="trisla-form-row">
          <label htmlFor="throughput">Throughput</label>
          <input id="throughput" type="number" value={throughput} onChange={(e) => setThroughput(e.target.value)} />
        </div>
        <div className="trisla-form-row">
          <label htmlFor="availability">Availability</label>
          <input id="availability" type="number" value={availability} onChange={(e) => setAvailability(e.target.value)} />
        </div>
        <div className="trisla-form-row">
          <label htmlFor="reliability">Reliability</label>
          <input id="reliability" type="number" value={reliability} onChange={(e) => setReliability(e.target.value)} />
        </div>
        <div className="trisla-form-row">
          <label htmlFor="priority">Priority</label>
          <input id="priority" type="text" value={priority} onChange={(e) => setPriority(e.target.value)} />
        </div>
        <button type="submit" disabled={status === "loading"}>
          Submeter SLA Template
        </button>
      </form>

      <DataState status={status} errorMessage={error}>
        {result && (() => {
          const decisionSnapshot =
            result.metadata &&
            typeof result.metadata === "object" &&
            "decision_snapshot" in result.metadata
              ? (result.metadata.decision_snapshot as Record<string, unknown>)
              : undefined;
          return (
          <>
            {/* A. Semantic Result */}
            <section className="trisla-status-card" aria-label="Semantic Result">
              <h2>A. Semantic Result</h2>
              <dl>
                <div className="trisla-status-row">
                  <dt>sla_id</dt>
                  <dd>{formatValue(result.sla_id)}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>intent_id</dt>
                  <dd>{formatValue(result.intent_id)}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>nest_id</dt>
                  <dd>{formatValue(result.nest_id)}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>service_type</dt>
                  <dd>{formatValue(result.service_type)}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>timestamp</dt>
                  <dd>{formatValue(result.timestamp)}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>sla_requirements</dt>
                  <dd><ObjectDl value={result.sla_requirements} /></dd>
                </div>
              </dl>
            </section>

            {/* B. Admission Decision — result.decision */}
            <section className="trisla-status-card" aria-label="Admission Decision">
              <h2>B. Admission Decision</h2>
              <dl>
                <div className="trisla-status-row">
                  <dt>decision</dt>
                  <dd>{formatValue(result.decision)}</dd>
                </div>
              </dl>
            </section>

            {/* C. XAI Metrics & Reasoning — result.confidence, result.reasoning (fallback reason/justification) */}
            <section className="trisla-status-card" aria-label="XAI Scientific Result">
              <h2>C. XAI Metrics & Reasoning</h2>
              <dl>
                <div className="trisla-status-row">
                  <dt>confidence</dt>
                  <dd>{result.confidence != null ? formatValue(result.confidence) : (ml && "confidence" in ml ? formatValue(ml.confidence) : "—")}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>reasoning</dt>
                  <dd>{formatValue(result.reasoning ?? result.reason ?? result.justification) || "—"}</dd>
                </div>
                {decisionSnapshot && (
                  <>
                    <div className="trisla-status-row">
                      <dt>ml_risk_score</dt>
                      <dd>{formatValue(decisionSnapshot.ml_risk_score) || "—"}</dd>
                    </div>
                    <div className="trisla-status-row">
                      <dt>ml_risk_level</dt>
                      <dd>{formatValue(decisionSnapshot.ml_risk_level) || "—"}</dd>
                    </div>
                  </>
                )}
              </dl>
            </section>

            {/* D. Domain Viability — decisionSnapshot.domains (RAN, Transport, Core) */}
            <section className="trisla-status-card" aria-label="Domain Viability">
              <h2>D. Domain Viability</h2>
              {(() => {
                const domainsSnapshot = decisionSnapshot?.domains as Record<string, Record<string, unknown>> | undefined;
                if (!domainsSnapshot || typeof domainsSnapshot !== "object") {
                  return <p className="trisla-muted">—</p>;
                }
                const domainOrder = ["RAN", "Transport", "Core"];
                return (
                  <dl>
                    {domainOrder.map((name) => {
                      const data = domainsSnapshot[name];
                      if (!data || typeof data !== "object") return null;
                      const entries = Object.entries(data);
                      if (entries.length === 0) return null;
                      return (
                        <div key={name} className="trisla-status-row">
                          <dt>{name}</dt>
                          <dd>
                            <dl className="trisla-nested-dl">
                              {entries.map(([k, v]) => (
                                <div key={k} className="trisla-status-row">
                                  <dt>{k}</dt>
                                  <dd>{formatValue(v)}</dd>
                                </div>
                              ))}
                            </dl>
                          </dd>
                        </div>
                      );
                    })}
                  </dl>
                );
              })()}
            </section>

            {/* E. Blockchain Governance — result.tx_hash, result.block_number, result.bc_status */}
            <section className="trisla-status-card" aria-label="Blockchain Governance">
              <h2>E. Blockchain Governance</h2>
              <dl>
                <div className="trisla-status-row">
                  <dt>tx_hash</dt>
                  <dd>{formatValue(result.tx_hash)}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>block_number</dt>
                  <dd>{formatValue(result.block_number)}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>bc_status</dt>
                  <dd>{formatValue(result.bc_status)}</dd>
                </div>
              </dl>
            </section>

            {/* F. Post-submit CTAs — navegação controlada para Runtime e Monitoring */}
            <section className="trisla-status-card" aria-label="Next steps">
              <h2>F. Next steps</h2>
              <p className="trisla-muted">View runtime orchestration and observability after admission.</p>
              <div className="trisla-cta-row">
                <Link href="/sla-lifecycle" className="trisla-cta-button">View Runtime</Link>
                <Link href="/monitoring" className="trisla-cta-button">View Monitoring</Link>
              </div>
            </section>
          </>
          );
        })()}
      </DataState>
    </section>
  );
}
