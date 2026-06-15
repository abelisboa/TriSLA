"use client";

import { useCallback, useEffect, useState } from "react";
import { formatApiError, portalApi } from "../../lib/api";
import {
  admissionDecisionFromStatus,
  isRuntimeLifecycleEnabled,
  showLifecycleSection,
} from "../../lib/admissionLifecycleGate";
import {
  buildRevalidateRequest,
  intentIdFromSubmit,
  lifecycleStateFromSubmit,
  referenceTelemetryFromSubmit,
  type RevalidateTelemetryResponse,
  type SlaRuntimeStatusResponse,
} from "../../lib/runtimeSupervision";
import { LifecycleRuntimeSnapshotPanel } from "../lifecycle/LifecycleRuntimeSnapshotPanel";
import type { SubmitResponse } from "../../lib/submitResponse";
import {
  DriftAnalysisPanel,
  FreshTelemetryPanel,
  RemediationEvidencePanel,
  RuntimePayloadPanel,
  RuntimeStatusPanel,
} from "./RuntimeSupervisionPanels";
import { ComplianceEvaluationPanel } from "../lifecycle/ComplianceEvaluationPanel";
import { RuntimeAssurancePanel } from "../lifecycle/RuntimeAssurancePanel";
import { parseRuntimeAssurance } from "../../lib/runtimeAssurance";
import { AdmissionOnlyBanner } from "../gating/AdmissionOnlyBanner";

type Props = { response: SubmitResponse; heading?: string };

export function RuntimeSupervisionSection({
  response,
  heading = "6. Runtime Supervision",
}: Props) {
  const intentId = intentIdFromSubmit(response);
  const lifecycleState = lifecycleStateFromSubmit(response);

  const [statusData, setStatusData] = useState<SlaRuntimeStatusResponse | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);
  const [statusError, setStatusError] = useState<string | undefined>();

  const [revalidation, setRevalidation] = useState<RevalidateTelemetryResponse | null>(null);
  const [revalidateLoading, setRevalidateLoading] = useState(false);
  const [revalidateError, setRevalidateError] = useState<string | undefined>();

  const loadStatus = useCallback(async () => {
    if (!intentId) return;
    setStatusLoading(true);
    setStatusError(undefined);
    try {
      const data = await portalApi.getSlaStatus(intentId);
      setStatusData(data);
    } catch (err) {
      setStatusError(formatApiError(err));
      setStatusData(null);
    } finally {
      setStatusLoading(false);
    }
  }, [intentId]);

  useEffect(() => {
    void loadStatus();
  }, [loadStatus]);

  const admissionDecision = admissionDecisionFromStatus(statusData);
  const runtimeEnabled = isRuntimeLifecycleEnabled(statusData);

  if (!runtimeEnabled && statusData) {
    return (
      <section className="trisla-status-card trisla-runtime-supervision" aria-label="Runtime Supervision">
        <h2>{heading}</h2>
        <AdmissionOnlyBanner decision={admissionDecision} />
      </section>
    );
  }

  async function handleRevalidate() {
    const body = buildRevalidateRequest(response);
    if (!body) {
      setRevalidateError("intent_id not available in submit response");
      return;
    }

    setRevalidateLoading(true);
    setRevalidateError(undefined);
    try {
      const data = await portalApi.revalidateTelemetry(body);
      setRevalidation(data);
      await loadStatus();
    } catch (err) {
      setRevalidateError(formatApiError(err));
      setRevalidation(null);
    } finally {
      setRevalidateLoading(false);
    }
  }

  const remediation = revalidation?.metadata?.remediation_evidence;
  const remediationObj =
    remediation && typeof remediation === "object"
      ? (remediation as Record<string, unknown>)
      : undefined;

  const submitTelemetrySnapshot = referenceTelemetryFromSubmit(response);
  const runtimeSnapshot =
    submitTelemetrySnapshot ??
    (statusData?.telemetry_snapshot && typeof statusData.telemetry_snapshot === "object"
      ? statusData.telemetry_snapshot
      : undefined);

  return (
    <section className="trisla-status-card trisla-runtime-supervision" aria-label="Runtime Supervision">
      <h2>{heading}</h2>
      <p className="trisla-muted">
        Manual runtime revalidation workflow — user-triggered only. No automatic closed-loop.
      </p>

      {!intentId && (
        <p className="trisla-error">intent_id not available — revalidation cannot proceed.</p>
      )}

      <RuntimeStatusPanel
        statusData={statusData}
        lifecycleState={lifecycleState}
        loading={statusLoading}
        error={statusError}
        assurance={parseRuntimeAssurance(statusData?.runtime_assurance)}
      />

      {showLifecycleSection("runtimeAssurance", admissionDecision) ? (
        <RuntimeAssurancePanel assurance={parseRuntimeAssurance(statusData?.runtime_assurance)} />
      ) : null}

      {showLifecycleSection("runtimeCompliance", admissionDecision) ? (
        <ComplianceEvaluationPanel assurance={parseRuntimeAssurance(statusData?.runtime_assurance)} />
      ) : null}

      {showLifecycleSection("runtimeSnapshot", admissionDecision) ? (
        <LifecycleRuntimeSnapshotPanel snapshot={runtimeSnapshot} />
      ) : null}

      {showLifecycleSection("revalidation", admissionDecision) ? (
        <section className="trisla-runtime-subsection" aria-label="Revalidate Telemetry">
          <h3>Revalidate Telemetry</h3>
          <button
            type="button"
            className="trisla-cta-button"
            onClick={() => void handleRevalidate()}
            disabled={!intentId || revalidateLoading}
          >
            {revalidateLoading ? "Revalidating…" : "Revalidate Telemetry"}
          </button>
          {revalidateError && <p className="trisla-error">{revalidateError}</p>}
          {revalidation?.revalidation_status && (
            <p>
              revalidation_status: <strong>{revalidation.revalidation_status}</strong>
            </p>
          )}
        </section>
      ) : null}

      {revalidation && showLifecycleSection("driftAnalysis", admissionDecision) ? (
        <>
          <FreshTelemetryPanel
            snapshot={
              revalidation.telemetry_snapshot_atual &&
              typeof revalidation.telemetry_snapshot_atual === "object"
                ? revalidation.telemetry_snapshot_atual
                : undefined
            }
            revalidationStatus={revalidation.revalidation_status}
          />
          <DriftAnalysisPanel driftSummary={revalidation.drift_summary} />
          {showLifecycleSection("remediation", admissionDecision) ? (
            <RemediationEvidencePanel evidence={remediationObj} />
          ) : null}
          <RuntimePayloadPanel payload={revalidation} />
        </>
      ) : null}
    </section>
  );
}
