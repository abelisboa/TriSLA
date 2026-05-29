"use client";

import { FormEvent, useState } from "react";
import { apiRequest, formatApiError } from "../../lib/api";
import { DataState } from "../../components/common/DataState";
import { SubmitResultPanels } from "../../components/submit-payload/SubmitResultPanels";
import type { SubmitResponse } from "../../lib/submitResponse";

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
      setError(formatApiError(err));
    }
  }

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
        {result && <SubmitResultPanels response={result} />}
      </DataState>
    </section>
  );
}
