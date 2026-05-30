"use client";

import { FormEvent, useMemo, useRef, useState } from "react";
import { apiRequest, formatApiError } from "../../lib/api";
import { DataState } from "../../components/common/DataState";
import { InterpretPreviewPanel } from "../../components/pnl/InterpretPreviewPanel";
import {
  buildSubmitPayloadFromInterpret,
  type InterpretResponse,
} from "../../lib/pnlSubmit";
import type { SubmitResponse } from "../../lib/submitResponse";
import { generateTrislaTenantId } from "../../lib/tenantAutogen";
import { WorkflowSteps, PNL_WORKFLOW_STEPS } from "../../components/workflow/WorkflowSteps";
import { TEMPLATE_ID_HELP } from "../../lib/operatorLabels";
import { SubmitResultPanels } from "../../components/submit-payload/SubmitResultPanels";

type FlowStatus = "idle" | "loading" | "ready" | "error";

export default function CreateSlaPnlPage() {
  const [intentText, setIntentText] = useState("");
  const [templateId, setTemplateId] = useState("");
  const sessionTenantIdRef = useRef<string | null>(null);

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
    if (!intentText.trim()) {
      setInterpretError("Natural Language Request não pode ser vazio");
      setInterpretStatus("error");
      return;
    }

    const tenantId = generateTrislaTenantId();
    sessionTenantIdRef.current = tenantId;

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
      setSubmitError("Submission incomplete — confirm Template ID and interpret fields.");
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

  const workflowSteps = PNL_WORKFLOW_STEPS.map((step) => ({
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
        Natural language SLA creation — interpret intent, confirm template, and submit for admission.
      </p>

      <WorkflowSteps title="SLA workflow — natural language" steps={workflowSteps} />

      <form onSubmit={handleInterpret} className="trisla-form">
        <div className="trisla-form-row">
          <label htmlFor="intent_text">Natural Language Request</label>
          <textarea
            id="intent_text"
            value={intentText}
            onChange={(e) => setIntentText(e.target.value)}
            rows={4}
            placeholder="Describe the required network service in natural language"
          />
        </div>

        <button type="submit" disabled={interpretStatus === "loading"}>
          Interpret SLA
        </button>
      </form>

      <DataState status={interpretStatus} errorMessage={interpretError}>
        {interpretResult && (
          <>
            <InterpretPreviewPanel
              interpret={interpretResult}
              inputText={intentText}
              sessionTenantId={sessionTenantIdRef.current}
            />

            <section className="trisla-status-card" aria-label="Submit confirmation">
              <h2>Confirm and Submit</h2>
              <p className="trisla-muted">
                Template ID is required for submission and must be confirmed before submit.
              </p>
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

              {submitPayload ? (
                <details className="trisla-details">
                  <summary>Technical details — submission payload</summary>
                  <pre className="trisla-pre-secondary">
                    {JSON.stringify(submitPayload, null, 2)}
                  </pre>
                </details>
              ) : (
                <p className="trisla-muted">Submission preview available after Template ID is set.</p>
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
