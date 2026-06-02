"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { apiRequest, formatApiError, portalApi } from "../../lib/api";
import { DataState } from "../../components/common/DataState";
import {
  admissionDecisionFromStatus,
  admissionBannerMessage,
  isRuntimeLifecycleEnabled,
  operationalStatusLabel,
  parseStatusDecisionEvidence,
  showLifecycleSection,
  type LifecycleSection,
} from "../../lib/admissionLifecycleGate";
import {
  lifecycleViewFromParam,
  showLifecycleSectionInView,
} from "../../lib/lifecycleViewFilter";
import { usePortalNavContext } from "../../lib/portalNavContext";
import {
  formatModuleOperationalState,
  moduleOperationalLabel,
  normalizeModuleProbe,
} from "../../lib/operatorDiagnostics";
import { formatDecisionScore } from "../../lib/operatorFormat";
import {
  AWAITING_DATA,
  formatLifecycleStateLabel,
  formatNaspModuleLabel,
  operatorFieldLabel,
} from "../../lib/operatorLabels";
import type { SlaRuntimeStatusResponse } from "../../lib/runtimeSupervision";
import { LifecycleRuntimeSnapshotPanel } from "../../components/lifecycle/LifecycleRuntimeSnapshotPanel";
import { RuntimeAssurancePanel } from "../../components/lifecycle/RuntimeAssurancePanel";
import { parseRuntimeAssurance } from "../../lib/runtimeAssurance";
import { LIFECYCLE_ACTIVE_EXPLANATION } from "../../lib/runtimeAssuranceStateModel";
import { DecisionEvidencePanel } from "../../components/consistency/DecisionEvidencePanel";
import { BlockchainCommitCard } from "../../components/consistency/BlockchainCommitCard";
import { GovernanceClarityPanel } from "../../components/consistency/GovernanceClarityPanel";
import { AdmissionOnlyBanner } from "../../components/gating/AdmissionOnlyBanner";
import { WhyRejectedPanel } from "../../components/gating/WhyRejectedPanel";
import { RenegotiationProposalPanel } from "../../components/gating/RenegotiationProposalPanel";
import { BESU_NETWORK_LABEL } from "../../lib/blockchainEvidenceDisplay";
import { GOVERNANCE_TOOLTIPS } from "../../lib/governanceDisplayLabels";
import { governanceClarityFromAssurance } from "../../lib/phaseNextConsistency";

type Status = "idle" | "loading" | "ready" | "error";

export default function SlaLifecyclePage() {
  return (
    <Suspense fallback={<section><h1>SLA Lifecycle</h1><p className="trisla-muted">Loading…</p></section>}>
      <SlaLifecycleContent />
    </Suspense>
  );
}

function SlaLifecycleContent() {
  const searchParams = useSearchParams();
  const intentFromUrl = searchParams.get("intent_id")?.trim() ?? "";
  const lifecycleView = lifecycleViewFromParam(searchParams.get("view"));
  const { setPortalNavContext } = usePortalNavContext();

  const [intentQuery, setIntentQuery] = useState(intentFromUrl);
  const [statusData, setStatusData] = useState<SlaRuntimeStatusResponse | null>(null);
  const [statusLoad, setStatusLoad] = useState<Status>("idle");
  const [statusError, setStatusError] = useState<string | undefined>();

  const [naspDiagnostics, setNaspDiagnostics] = useState<Record<string, unknown> | null>(null);
  const [naspStatus, setNaspStatus] = useState<Status>("idle");
  const [naspError, setNaspError] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (intentFromUrl) setIntentQuery(intentFromUrl);
  }, [intentFromUrl]);

  useEffect(() => {
    let cancelled = false;
    const intentId = intentQuery.trim();
    if (!intentId) {
      setStatusData(null);
      setStatusLoad("idle");
      setStatusError(undefined);
      return;
    }

    setStatusLoad("loading");
    setStatusError(undefined);

    portalApi
      .getSlaStatus(intentId)
      .then((response) => {
        if (cancelled) return;
        setStatusData(response);
        setStatusLoad("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setStatusLoad("error");
        setStatusError(formatApiError(err));
        setStatusData(null);
      });

    return () => {
      cancelled = true;
    };
  }, [intentQuery]);

  useEffect(() => {
    let cancelled = false;
    setNaspStatus("loading");
    setNaspError(undefined);

    apiRequest<Record<string, unknown>>("NASP_DIAGNOSTICS")
      .then((response) => {
        if (cancelled) return;
        setNaspDiagnostics(response);
        setNaspStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setNaspStatus("error");
        setNaspError(formatApiError(err));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const operational = statusData?.operational_summary;
  const admissionDecision = admissionDecisionFromStatus(statusData);
  const runtimeEnabled = isRuntimeLifecycleEnabled(statusData);
  const decisionEvidence = parseStatusDecisionEvidence(statusData);
  const displayOperationalStatus = operationalStatusLabel(admissionDecision);

  useEffect(() => {
    setPortalNavContext({
      intentId: intentQuery.trim() || null,
      admissionDecision: statusData ? admissionDecision : null,
    });
  }, [intentQuery, statusData, admissionDecision, setPortalNavContext]);

  const semanticValidation = operational?.semantic_validation ?? "Not available";
  const gstGenerated = operational?.gst_generated ?? (statusData?.nest_id ? "Yes" : "Not available");
  const nestGenerated = operational?.nest_generated ?? (statusData?.nest_id ? "Yes" : "Not available");
  const semanticFill = operational?.semantic_fill ?? "Not available";
  const mlConfidenceDisplay =
    operational?.ml_confidence != null
      ? formatDecisionScore(operational.ml_confidence)
      : "Not available";
  const bcStatus = operational?.bc_status;
  const txHash = operational?.tx_hash;
  const blockNumberRaw = operational?.block_number;
  const blockNumber =
    typeof blockNumberRaw === "number" || typeof blockNumberRaw === "string"
      ? blockNumberRaw
      : undefined;

  const orchestrationModules = useMemo(() => {
    const keys = ["sem_csmf", "ml_nsmf", "decision", "bc_nssmf"] as const;
    if (showLifecycleSection("runtimeOrchestration", admissionDecision)) {
      return [...keys, "sla_agent"] as const;
    }
    return keys;
  }, [admissionDecision]);

  const traceability = statusData?.traceability;
  const correlationChain = traceability?.correlation_chain ?? [];
  const parsedAssurance = parseRuntimeAssurance(statusData?.runtime_assurance);
  const governanceClarity =
    governanceClarityFromAssurance(parsedAssurance) ??
    (statusData
      ? {
          governance_event: {
            label: "Governance Event",
            status: "Recorded",
            event_type: "Decision Recorded",
            governance_event_id: operational?.governance_event_id ?? null,
          },
          blockchain_registration: {
            label: "Blockchain Registration",
            status:
              admissionDecision === "ACCEPT" && bcStatus === "COMMITTED" ? "Executed" : "Not executed",
            executed: admissionDecision === "ACCEPT" && bcStatus === "COMMITTED",
            reason:
              admissionDecision !== "ACCEPT"
                ? `Decision ${admissionDecision}`
                : bcStatus !== "COMMITTED"
                  ? "ACCEPT without on-chain commit"
                  : undefined,
          },
        }
      : undefined);
  const onChainEvidence = {
    bc_status: bcStatus,
    tx_hash: txHash,
    block_number: blockNumber,
    network: BESU_NETWORK_LABEL,
  };
  const snapshotForPanel = runtimeEnabled
    ? statusData?.telemetry_snapshot
    : statusData?.admission_telemetry_snapshot ?? statusData?.telemetry_snapshot;

  const show = (section: LifecycleSection) =>
    showLifecycleSectionInView(section, admissionDecision, lifecycleView);

  const pageTitle =
    lifecycleView === "runtime" ? "Runtime Lifecycle" : "Admission Analysis";
  const pageSubtitle =
    lifecycleView === "runtime"
      ? runtimeEnabled
        ? "Runtime supervision, assurance, and closed-loop indicators for accepted SLAs."
        : "Runtime lifecycle is not available for this admission decision."
      : runtimeEnabled
        ? "Admission pipeline evidence — decision, semantics, ML, and decision analysis."
        : "Admission analysis — runtime supervision disabled for this decision.";

  return (
    <section>
      <h1>{pageTitle}</h1>
      <p className="trisla-subtitle">{pageSubtitle}</p>

      {lifecycleView === "runtime" && !runtimeEnabled && statusData ? (
        <AdmissionOnlyBanner decision={admissionDecision} />
      ) : null}

      {lifecycleView === "admission" && admissionBannerMessage(admissionDecision) ? (
        <AdmissionOnlyBanner decision={admissionDecision} />
      ) : null}

      {show("runtimeIdentity") ? (
        <section className="trisla-status-card" aria-label="SLA Runtime Identity">
          <h2>Runtime Identity</h2>
          <p className="trisla-muted">Look up persisted SLA identity via Intent ID.</p>
          <div className="trisla-form-row" style={{ marginBottom: "1rem" }}>
            <label htmlFor="lifecycle-intent-id">Intent ID</label>
            <input
              id="lifecycle-intent-id"
              className="trisla-input"
              value={intentQuery}
              onChange={(e) => setIntentQuery(e.target.value)}
              placeholder="Paste intent UUID from admission result"
            />
          </div>
          <DataState status={statusLoad} errorMessage={statusError}>
            {statusData ? (
              <dl>
                <div className="trisla-status-row">
                  <dt>{operatorFieldLabel("intent_id")}</dt>
                  <dd>{statusData.intent_id ?? statusData.sla_id ?? "Not available"}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>{operatorFieldLabel("nest_id")}</dt>
                  <dd>{statusData.nest_id ?? "Not available"}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>Admission Decision</dt>
                  <dd>{admissionDecision}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>Operational Status</dt>
                  <dd>{formatLifecycleStateLabel(displayOperationalStatus)}</dd>
                </div>
                {displayOperationalStatus === "ACTIVE" ? (
                  <div className="trisla-status-row">
                    <dt>Operational note</dt>
                    <dd>{LIFECYCLE_ACTIVE_EXPLANATION}</dd>
                  </div>
                ) : null}
              </dl>
            ) : intentQuery.trim() ? null : (
              <p className="trisla-muted">Enter an Intent ID to load runtime identity.</p>
            )}
          </DataState>
        </section>
      ) : null}

      <div className="trisla-cards-grid">
        {show("semanticAdmission") ? (
          <section className="trisla-status-card" aria-label="Semantic Admission">
            <h2>Semantic Admission</h2>
            <DataState status={naspStatus} errorMessage={naspError}>
              <dl>
                <div className="trisla-status-row">
                  <dt>Semantic Validation</dt>
                  <dd>{semanticValidation}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>GST Generated</dt>
                  <dd>{gstGenerated}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>NEST Generated</dt>
                  <dd>{nestGenerated}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>Semantic Fill</dt>
                  <dd>{semanticFill}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>SEM Engine</dt>
                  <dd>
                    {moduleOperationalLabel(
                      formatModuleOperationalState(
                        normalizeModuleProbe(naspDiagnostics?.sem_csmf),
                        naspStatus,
                      ),
                    )}
                  </dd>
                </div>
              </dl>
            </DataState>
          </section>
        ) : null}

        {show("mlDecision") ? (
          <section className="trisla-status-card" aria-label="ML Decision">
            <h2>ML Decision</h2>
            <DataState status={naspStatus} errorMessage={naspError}>
              <dl>
                <div className="trisla-status-row">
                  <dt>Model Confidence</dt>
                  <dd>{mlConfidenceDisplay}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>ML Engine</dt>
                  <dd>
                    {moduleOperationalLabel(
                      formatModuleOperationalState(
                        normalizeModuleProbe(naspDiagnostics?.ml_nsmf),
                        naspStatus,
                      ),
                    )}
                  </dd>
                </div>
                {operational?.decision_score != null ? (
                  <div className="trisla-status-row">
                    <dt>Decision Score</dt>
                    <dd>{formatDecisionScore(operational.decision_score)}</dd>
                  </div>
                ) : null}
              </dl>
            </DataState>
          </section>
        ) : null}

        {show("blockchain") ? (
          <section className="trisla-status-card" aria-label="On-chain commit">
            <h2>On-chain commit</h2>
            <p className="trisla-muted" title={GOVERNANCE_TOOLTIPS.onChainCommitCard}>
              Per-SLA transaction commit from the NASP pipeline (not BC-NSSMF service health).
            </p>
            <DataState status={naspStatus} errorMessage={naspError}>
              <BlockchainCommitCard
                bcStatus={bcStatus}
                txHash={txHash}
                blockNumber={blockNumber}
              />
            </DataState>
          </section>
        ) : null}

        {show("runtimeOrchestration") ? (
          <section className="trisla-status-card" aria-label="Runtime orchestration">
            <h2>Runtime orchestration</h2>
            <p className="trisla-muted" title={GOVERNANCE_TOOLTIPS.bcServiceHealth}>
              NASP module probes (BC-NSSMF row = service health only).
            </p>
            <DataState status={naspStatus} errorMessage={naspError}>
              <dl>
                {orchestrationModules.map((key) => {
                  const probe = normalizeModuleProbe(naspDiagnostics?.[key]);
                  const op = formatModuleOperationalState(probe, naspStatus);
                  return (
                    <div key={key} className="trisla-status-row">
                      <dt>{formatNaspModuleLabel(key)}</dt>
                      <dd>{naspStatus === "loading" ? AWAITING_DATA : moduleOperationalLabel(op)}</dd>
                    </div>
                  );
                })}
              </dl>
            </DataState>
          </section>
        ) : null}
      </div>

      {show("decisionEvidence") && decisionEvidence.length > 0 ? (
        <section className="trisla-status-card">
          <DecisionEvidencePanel evidence={decisionEvidence} />
        </section>
      ) : null}

      {show("governance") ? (
        <section className="trisla-status-card">
          <GovernanceClarityPanel clarity={governanceClarity} onChainEvidence={onChainEvidence} />
        </section>
      ) : null}

      {show("whyRejected") ? (
        <WhyRejectedPanel
          decision={admissionDecision}
          evidence={decisionEvidence}
          reasoning={statusData?.admission_reasoning}
        />
      ) : null}

      {show("renegotiationProposal") ? (
        <RenegotiationProposalPanel statusData={statusData} />
      ) : null}

      {show("runtimeSnapshot") ? (
        <LifecycleRuntimeSnapshotPanel
          snapshot={snapshotForPanel}
          loading={statusLoad === "loading" && Boolean(intentQuery.trim())}
          error={statusError}
        />
      ) : null}

      {show("runtimeAssurance") ? (
        <RuntimeAssurancePanel
          assurance={parsedAssurance}
          onChainEvidence={onChainEvidence}
          telemetrySnapshot={snapshotForPanel}
          traceContext={{
            intent_id: statusData?.intent_id ?? (intentQuery.trim() || undefined),
            nest_id: statusData?.nest_id,
            trace_id: statusData?.traceability?.trace_id,
            governance_event_id: operational?.governance_event_id,
          }}
        />
      ) : null}

      {show("distributedTrace") ? (
        <details className="trisla-details" style={{ marginTop: "1.5rem" }}>
          <summary>Technical Details — Distributed Trace</summary>
          <div className="trisla-cards-grid" style={{ marginTop: "1rem" }}>
            <section className="trisla-status-card">
              <h2>Trace Identity</h2>
              <dl>
                <div className="trisla-status-row">
                  <dt>Trace ID</dt>
                  <dd>{traceability?.trace_id ?? "Not available"}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>Span ID</dt>
                  <dd>{traceability?.span_id ?? "Not available"}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>End-to-end</dt>
                  <dd>{traceability?.end_to_end === true ? "Yes" : traceability ? "Partial" : "Not available"}</dd>
                </div>
              </dl>
            </section>
            <section className="trisla-status-card">
              <h2>Correlation Chain</h2>
              {correlationChain.length > 0 ? (
                <dl>
                  {correlationChain.map((hop, index) => {
                    const service =
                      typeof hop.service === "string" ? hop.service : `Hop ${index + 1}`;
                    return (
                      <div key={`${service}-${index}`} className="trisla-status-row">
                        <dt>{service}</dt>
                        <dd>
                          {hop.trace_id
                            ? `${String(hop.trace_id).slice(0, 8)}… / ${String(hop.span_id ?? "").slice(0, 8)}…`
                            : "—"}
                        </dd>
                      </div>
                    );
                  })}
                </dl>
              ) : (
                <p className="trisla-muted">No correlation chain available for this intent.</p>
              )}
            </section>
          </div>
        </details>
      ) : null}
    </section>
  );
}
