"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { apiRequest } from "../../lib/api";
import { DataState } from "../../components/common/DataState";
import { formatValue } from "../../lib/format";

type InterpretResponse = {
  intent_id?: string | null;
  nest_id?: string | null;
  service_type?: string | null;
  slice_type?: string | null;
  tenant_id?: string | null;
  status?: string | null;
  created_at?: string | null;
  message?: string | null;
  sla_requirements?: unknown;
  technical_parameters?: unknown;
  sla_id?: string | null;
};

type Status = "idle" | "loading" | "ready" | "error";

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

/** Render payload real como tabela/lista legível. */
function StructuredPayload({ value }: { value: unknown }) {
  if (value === null || value === undefined) {
    return <span className="trisla-muted">unavailable</span>;
  }
  if (typeof value !== "object") {
    return <span>{formatValue(value)}</span>;
  }
  if (Array.isArray(value)) {
    if (value.length === 0) return <span className="trisla-muted">[]</span>;
    const allPlain = value.every(
      (v) => v === null || typeof v !== "object" || Array.isArray(v),
    );
    if (allPlain) {
      return (
        <details className="trisla-details">
          <summary>Raw JSON ({value.length} items)</summary>
          <pre className="trisla-pre-secondary">{JSON.stringify(value, null, 2)}</pre>
        </details>
      );
    }
    return (
      <dl className="trisla-constraint-list">
        {value.map((item, i) => (
          <div key={i} className="trisla-status-row">
            <dt>[{i}]</dt>
            <dd>
              {typeof item === "object" && item !== null && !Array.isArray(item) ? (
                <StructuredPayload value={item} />
              ) : (
                formatValue(item)
              )}
            </dd>
          </div>
        ))}
      </dl>
    );
  }
  const entries = Object.entries(value as Record<string, unknown>);
  if (entries.length === 0) return <span className="trisla-muted">{"{}"}</span>;
  return (
    <dl className="trisla-constraint-list">
      {entries.map(([k, v]) => (
        <div key={k} className="trisla-status-row">
          <dt>{k}</dt>
          <dd>
            {typeof v === "object" && v !== null ? (
              <StructuredPayload value={v} />
            ) : (
              formatValue(v)
            )}
          </dd>
        </div>
      ))}
    </dl>
  );
}

/** Recommended template ID from service_type (e.g. urllc-basic). */
function recommendedTemplateId(serviceType: string | null | undefined): string {
  if (!serviceType || !serviceType.trim()) return "—";
  const s = serviceType.trim().toLowerCase();
  if (s === "urllc") return "urllc-basic";
  if (s === "embb") return "embb-basic";
  if (s === "mmtc") return "mmtc-basic";
  return `${s}-basic`;
}

export default function CreateSlaPnlPage() {
  const [intentText, setIntentText] = useState("");
  const [tenantId, setTenantId] = useState("");
  const [result, setResult] = useState<InterpretResponse | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | undefined>(undefined);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!tenantId.trim()) {
      setError("Tenant ID não pode ser vazio");
      setStatus("error");
      return;
    }
    setStatus("loading");
    setError(undefined);
    setResult(null);

    try {
      const response = await apiRequest<InterpretResponse>("SLA_INTERPRET", {
        method: "POST",
        body: {
          intent_text: intentText,
          tenant_id: tenantId,
        },
      });
      setResult(response);
      setStatus("ready");
    } catch (err) {
      setStatus("error");
      setError(normalizeError(err));
    }
  }

  return (
    <section>
      <h1>PNL</h1>
      <p className="trisla-subtitle">Natural language semantic interpretation pipeline.</p>

      <form onSubmit={handleSubmit} className="trisla-form">
        <div className="trisla-form-row">
          <label htmlFor="intent_text">Intent text (linguagem natural)</label>
          <textarea
            id="intent_text"
            value={intentText}
            onChange={(e) => setIntentText(e.target.value)}
            rows={4}
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

        <button type="submit" disabled={status === "loading"}>
          Interpretar SLA
        </button>
      </form>

      <DataState status={status} errorMessage={error}>
        {result && (
          <>
            {/* A. Semantic Interpretation — campos entregues por /interpret */}
            <section className="trisla-status-card" aria-label="Semantic Interpretation">
              <h2>A. Semantic Interpretation</h2>
              <dl>
                <div className="trisla-status-row">
                  <dt>Intent</dt>
                  <dd>{intentText || "—"}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>Recommended template</dt>
                  <dd>{recommendedTemplateId(result.service_type ?? result.slice_type)}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>slice_type</dt>
                  <dd>{formatValue(result.slice_type ?? result.service_type)}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>technical_parameters</dt>
                  <dd>
                    {result.technical_parameters ? (
                      <StructuredPayload value={result.technical_parameters} />
                    ) : (
                      <span className="trisla-muted">unavailable</span>
                    )}
                  </dd>
                </div>
                <div className="trisla-status-row">
                  <dt>intent_id</dt>
                  <dd>{formatValue(result.intent_id)}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>nest_id</dt>
                  <dd>{formatValue(result.nest_id)}</dd>
                </div>
              </dl>
            </section>

            {/* B. Semantic Mapping — explanation e classification do /interpret */}
            <section className="trisla-status-card" aria-label="Semantic Mapping">
              <h2>B. Semantic Mapping</h2>
              <dl>
                <div className="trisla-status-row">
                  <dt>Semantic explanation</dt>
                  <dd>{result.message ? formatValue(result.message) : "—"}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>Semantic classification</dt>
                  <dd>{formatValue(result.service_type ?? result.slice_type)}</dd>
                </div>
              </dl>
            </section>

            {/* C. Recommendation — texto científico */}
            <section className="trisla-status-card" aria-label="Recommendation">
              <h2>C. Recommendation</h2>
              <p className="trisla-xai-message">
                Complete admission decision, XAI evidence, domain viability and blockchain governance are available after SLA submission in Template Workflow.
              </p>
            </section>

            {/* D. CTA — Continue to Template Submission */}
            <section className="trisla-status-card" aria-label="Next step">
              <h2>D. Next step</h2>
              <p className="trisla-muted">Submit the interpreted SLA in the Template workflow to obtain decision, reasoning, confidence, domains and blockchain evidence.</p>
              <Link href="/template" className="trisla-cta-button">
                Continue to Template Submission
              </Link>
            </section>

            {/* SLA Requirements — payload real do /interpret */}
            <section className="trisla-status-card" aria-label="SLA Requirements">
              <h2>SLA Requirements</h2>
              {result.sla_requirements ? (
                <StructuredPayload value={result.sla_requirements} />
              ) : (
                <p className="trisla-muted">unavailable</p>
              )}
            </section>
          </>
        )}
      </DataState>
    </section>
  );
}
