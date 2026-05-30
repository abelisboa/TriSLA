"use client";

import { FormEvent, useState } from "react";
import { apiRequest, formatApiError } from "../../lib/api";
import { DataState } from "../../components/common/DataState";
import { WorkflowSteps, TEMPLATE_WORKFLOW_STEPS } from "../../components/workflow/WorkflowSteps";
import { TEMPLATE_ID_HELP } from "../../lib/operatorLabels";
import { generateTrislaTenantId } from "../../lib/tenantAutogen";
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
    const tenantId = generateTrislaTenantId();

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

  const workflowSteps = TEMPLATE_WORKFLOW_STEPS.map((step) => ({
    ...step,
    active: step.id === (result ? "admission" : "submit"),
    complete:
      (step.id === "submit" && Boolean(result)) ||
      (["governance", "runtime"].includes(step.id) && Boolean(result)),
  }));

  return (
    <section>
      <h1>Template</h1>
      <p className="trisla-subtitle">
        Structured SLA submission — complete the form, then review admission through runtime sections.
      </p>

      <WorkflowSteps title="SLA workflow — template" steps={workflowSteps} />

      <form onSubmit={handleSubmit} className="trisla-form">
        <div className="trisla-form-row">
          <label htmlFor="template_id">Template ID</label>
          <input
            id="template_id"
            type="text"
            value={templateId}
            onChange={(e) => setTemplateId(e.target.value)}
          />
          <p className="trisla-field-help">{TEMPLATE_ID_HELP}</p>
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
          <input
            id="latency"
            type="number"
            step="any"
            value={latency}
            onChange={(e) => setLatency(e.target.value)}
          />
        </div>
        <div className="trisla-form-row">
          <label htmlFor="throughput">Throughput</label>
          <input
            id="throughput"
            type="number"
            step="any"
            value={throughput}
            onChange={(e) => setThroughput(e.target.value)}
          />
        </div>
        <div className="trisla-form-row">
          <label htmlFor="availability">Availability</label>
          <input
            id="availability"
            type="number"
            step="any"
            value={availability}
            onChange={(e) => setAvailability(e.target.value)}
          />
        </div>
        <div className="trisla-form-row">
          <label htmlFor="reliability">Reliability</label>
          <input
            id="reliability"
            type="number"
            step="any"
            value={reliability}
            onChange={(e) => setReliability(e.target.value)}
          />
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
