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
import { cacheAdmissionOperationalSnapshot } from "../../lib/admissionOperationalCache";
import { generateTrislaTenantId } from "../../lib/tenantAutogen";
import {
  resolveTemplateId,
  slaProfileLabel,
  UnknownSliceTypeError,
} from "../../lib/templateAutogen";
import { WorkflowSteps, PNL_WORKFLOW_STEPS } from "../../components/workflow/WorkflowSteps";
import { SubmitResultPanels } from "../../components/submit-payload/SubmitResultPanels";

type FlowStatus = "idle" | "loading" | "ready" | "error";

export default function CreateSlaPnlPage() {
  const [intentText, setIntentText] = useState("");
  const sessionTenantIdRef = useRef<string | null>(null);

  const [interpretResult, setInterpretResult] = useState<InterpretResponse | null>(null);
  const [interpretStatus, setInterpretStatus] = useState<FlowStatus>("idle");
  const [interpretError, setInterpretError] = useState<string | undefined>(undefined);

  const [submitResult, setSubmitResult] = useState<SubmitResponse | null>(null);
  const [submitStatus, setSubmitStatus] = useState<FlowStatus>("idle");
  const [submitError, setSubmitError] = useState<string | undefined>(undefined);

  const sliceType = interpretResult?.slice_type ?? interpretResult?.service_type ?? null;

  const resolvedTemplateId = useMemo(() => {
    if (!interpretResult) return null;
    try {
      return resolveTemplateId(sliceType);
    } catch {
      return null;
    }
  }, [interpretResult, sliceType]);

  const profileLabel = useMemo(() => slaProfileLabel(sliceType), [sliceType]);

  const submitPayload = useMemo(() => {
    if (!interpretResult || !resolvedTemplateId) return null;
    return buildSubmitPayloadFromInterpret(interpretResult, resolvedTemplateId);
  }, [interpretResult, resolvedTemplateId]);

  async function handleInterpret(e: FormEvent) {
    e.preventDefault();
    if (!intentText.trim()) {
      setInterpretError("Natural language request cannot be empty");
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

    try {
      const response = await apiRequest<InterpretResponse>("SLA_INTERPRET", {
        method: "POST",
        body: {
          intent_text: intentText,
          tenant_id: tenantId,
        },
      });
      try {
        resolveTemplateId(response.slice_type ?? response.service_type);
      } catch (err) {
        if (err instanceof UnknownSliceTypeError) {
          setInterpretError(err.message);
          setInterpretStatus("error");
          return;
        }
        throw err;
      }
      setInterpretResult(response);
      setInterpretStatus("ready");
    } catch (err) {
      setInterpretStatus("error");
      setInterpretError(formatApiError(err));
    }
  }

  async function handleConfirmSubmit() {
    if (!interpretResult || !submitPayload) {
      setSubmitError("Submission incomplete — interpret result unavailable.");
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
      cacheAdmissionOperationalSnapshot(response);
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
        Natural language SLA creation — interpret intent and submit for admission.
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
              resolvedTemplateId={resolvedTemplateId}
              profileLabel={profileLabel}
            />

            <section className="trisla-status-card" aria-label="Submit confirmation">
              <h2>Submit SLA</h2>
              <dl>
                <div className="trisla-status-row">
                  <dt>Selected SLA Profile</dt>
                  <dd>{profileLabel}</dd>
                </div>
              </dl>

              {submitPayload ? (
                <details className="trisla-details">
                  <summary>Advanced details — submission payload</summary>
                  <pre className="trisla-pre-secondary">
                    {JSON.stringify(submitPayload, null, 2)}
                  </pre>
                </details>
              ) : null}

              <button
                type="button"
                className="trisla-confirm-submit"
                disabled={submitStatus === "loading" || !submitPayload}
                onClick={handleConfirmSubmit}
              >
                Submit SLA
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
