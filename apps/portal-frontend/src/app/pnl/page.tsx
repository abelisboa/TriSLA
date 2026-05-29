"use client";

import { FormEvent, useMemo, useState } from "react";
import { apiRequest, formatApiError } from "../../lib/api";
import { DataState } from "../../components/common/DataState";
import { InterpretPreviewPanel } from "../../components/pnl/InterpretPreviewPanel";
import {
  buildSubmitPayloadFromInterpret,
  type InterpretResponse,
} from "../../lib/pnlSubmit";
import type { SubmitResponse } from "../../lib/submitResponse";
import { DemoFlowSteps, PNL_DEMO_STEPS } from "../../components/demo/DemoFlowSteps";
import { SubmitResultPanels } from "../../components/submit-payload/SubmitResultPanels";

type FlowStatus = "idle" | "loading" | "ready" | "error";

export default function CreateSlaPnlPage() {
  const [intentText, setIntentText] = useState("");
  const [tenantId, setTenantId] = useState("");
  const [templateId, setTemplateId] = useState("");

  const [interpretResult, setInterpretResult] = useState<InterpretResponse | null>(null);
  const [interpretStatus, setInterpretStatus] = useState<FlowStatus>("idle");
  const [interpretError, setInterpretError] = useState<string | undefined>(undefined);

  const [submitResult, setSubmitResult] = useState<SubmitResponse | null>(null);
  const [submitStatus, setSubmitStatus] = useState<FlowStatus>("idle");
  const [submitError, setSubmitError] = useState<string | undefined>(undefined);

  const submitPayload = useMemo(() => {
    if (!interpretResult) return null;
    return buildSubmitPayloadFromInterpret(interpretResult, templateId);
  }, [interpretResult, templateId]);

  async function handleInterpret(e: FormEvent) {
    e.preventDefault();
    if (!tenantId.trim()) {
      setInterpretError("Tenant ID não pode ser vazio");
      setInterpretStatus("error");
      return;
    }
    if (!intentText.trim()) {
      setInterpretError("Natural Language Request não pode ser vazio");
      setInterpretStatus("error");
      return;
    }

    setInterpretStatus("loading");
    setInterpretError(undefined);
    setInterpretResult(null);
    setSubmitResult(null);
    setSubmitStatus("idle");
    setSubmitError(undefined);
    setTemplateId("");

    try {
      const response = await apiRequest<InterpretResponse>("SLA_INTERPRET", {
        method: "POST",
        body: {
          intent_text: intentText,
          tenant_id: tenantId,
        },
      });
      setInterpretResult(response);
      setInterpretStatus("ready");
    } catch (err) {
      setInterpretStatus("error");
      setInterpretError(formatApiError(err));
    }
  }

  async function handleConfirmSubmit() {
    if (!interpretResult || !submitPayload) {
      setSubmitError("Submit payload incomplete — confirm template_id and interpret fields.");
      setSubmitStatus("error");
      return;
    }

    setSubmitStatus("loading");
    setSubmitError(undefined);
    setSubmitResult(null);

    try {
      const response = await apiRequest<SubmitResponse>("SLA_SUBMIT", {
        method: "POST",
        body: submitPayload,
      });
      setSubmitResult(response);
      setSubmitStatus("ready");
    } catch (err) {
      setSubmitStatus("error");
      setSubmitError(formatApiError(err));
    }
  }

  const activeStepId = submitResult
    ? "admission"
    : submitStatus === "loading" || submitPayload
      ? "submit"
      : interpretResult
        ? "interpret"
        : "pnl";

  const demoSteps = PNL_DEMO_STEPS.map((step) => ({
    ...step,
    active: step.id === activeStepId,
    complete:
      (step.id === "pnl" && Boolean(intentText.trim())) ||
      (step.id === "interpret" && Boolean(interpretResult)) ||
      (step.id === "submit" && Boolean(submitResult)) ||
      (["admission", "governance", "runtime"].includes(step.id) && Boolean(submitResult)),
  }));

  return (
    <section>
      <h1>PNL</h1>
      <p className="trisla-subtitle">
        Natural language pipeline — Steps 1–3 on this page; admission through runtime appear after
        submit.
      </p>

      <DemoFlowSteps title="Demo flow — PNL path" steps={demoSteps} />

      <form onSubmit={handleInterpret} className="trisla-form">
        <div className="trisla-form-row">
          <label htmlFor="intent_text">Natural Language Request</label>
          <textarea
            id="intent_text"
            value={intentText}
            onChange={(e) => setIntentText(e.target.value)}
            rows={4}
            placeholder='e.g. "I need a remote surgery service"'
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

        <button type="submit" disabled={interpretStatus === "loading"}>
          Interpret SLA
        </button>
      </form>

      <DataState status={interpretStatus} errorMessage={interpretError}>
        {interpretResult && (
          <>
            <InterpretPreviewPanel interpret={interpretResult} inputText={intentText} />

            <section className="trisla-status-card" aria-label="Submit confirmation">
              <h2>Confirm and Submit</h2>
              <p className="trisla-muted">
                Submit requires template_id (not returned by interpret). Enter the template ID to
                confirm, then submit mapped fields only.
              </p>
              <div className="trisla-form-row">
                <label htmlFor="template_id">template_id (user confirmation)</label>
                <input
                  id="template_id"
                  type="text"
                  value={templateId}
                  onChange={(e) => setTemplateId(e.target.value)}
                />
              </div>

              {submitPayload ? (
                <details className="trisla-details" open>
                  <summary>Submit payload preview</summary>
                  <pre className="trisla-pre-secondary">
                    {JSON.stringify(submitPayload, null, 2)}
                  </pre>
                </details>
              ) : (
                <p className="trisla-muted">Submit payload preview unavailable until template_id is set.</p>
              )}

              <button
                type="button"
                className="trisla-confirm-submit"
                disabled={submitStatus === "loading" || !submitPayload}
                onClick={handleConfirmSubmit}
              >
                Confirm and Submit
              </button>
            </section>
          </>
        )}
      </DataState>

      <DataState status={submitStatus} errorMessage={submitError}>
        {submitResult && <SubmitResultPanels response={submitResult} />}
      </DataState>
    </section>
  );
}
