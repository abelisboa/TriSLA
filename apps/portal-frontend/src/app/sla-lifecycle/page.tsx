 "use client";

 import { useEffect, useState } from "react";
 import { apiRequest } from "../../lib/api";
 import { DataState } from "../../components/common/DataState";
 import { formatValue } from "../../lib/format";

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

 function normalizeModuleProbe(moduleProbe: unknown): {
   reachable: boolean | null;
   status_code: unknown;
   detail: unknown;
 } {
   if (!moduleProbe || typeof moduleProbe !== "object") {
     return { reachable: null, status_code: null, detail: null };
   }
   const obj = moduleProbe as Record<string, unknown>;
   return {
     reachable: typeof obj.reachable === "boolean" ? (obj.reachable as boolean) : null,
     status_code: obj.status_code ?? null,
     detail: obj.detail ?? null,
   };
 }

export default function SlaLifecyclePage() {
  const awaiting = "Awaiting validated runtime feed";
 
   const [naspDiagnostics, setNaspDiagnostics] = useState<Record<string, unknown> | null>(
     null,
   );
   const [naspStatus, setNaspStatus] = useState<Status>("idle");
   const [naspError, setNaspError] = useState<string | undefined>(undefined);
 
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
         setNaspError(normalizeError(err));
       });
 
     return () => {
       cancelled = true;
     };
   }, []);
 
   const semProbe = normalizeModuleProbe(naspDiagnostics?.["sem_csmf"] ?? null);
   const semStatusText =
     naspStatus === "loading"
       ? awaiting
       : naspStatus === "error"
         ? "erro ao consultar fonte real"
         : semProbe.reachable === true
           ? "reachable"
           : semProbe.reachable === false
             ? "unreachable"
             : awaiting;
 
   const semRecommendation =
     naspStatus === "ready"
       ? formatValue({ status_code: semProbe.status_code, detail: semProbe.detail })
       : naspStatus === "error"
         ? formatValue(naspError ?? "erro ao consultar fonte real")
         : awaiting;

  const mlProbe = normalizeModuleProbe(naspDiagnostics?.["ml_nsmf"] ?? null);
  const mlDecisionStatus =
    naspStatus === "loading"
      ? awaiting
      : naspStatus === "error"
        ? "erro ao consultar fonte real"
        : mlProbe.reachable === true
          ? "reachable"
          : mlProbe.reachable === false
            ? "unreachable"
            : awaiting;

  // Não inventar score/confidence: exibir apenas detalhe textual real (status_code + detail)
  const mlDecisionConfidence =
    naspStatus === "ready"
      ? formatValue({ status_code: mlProbe.status_code, detail: mlProbe.detail })
      : naspStatus === "error"
        ? formatValue(naspError ?? "erro ao consultar fonte real")
        : awaiting;

  const bcProbe = normalizeModuleProbe(naspDiagnostics?.["bc_nssmf"] ?? null);
  const bcCommitStatus =
    naspStatus === "loading"
      ? awaiting
      : naspStatus === "error"
        ? "erro ao consultar fonte real"
        : bcProbe.reachable === true
          ? "reachable"
          : bcProbe.reachable === false
            ? "unreachable"
            : awaiting;

  // Não inventar tx hash / blockchain state: apenas evidência textual real (status_code + detail)
  const bcTrustEvidence =
    naspStatus === "ready"
      ? formatValue({ status_code: bcProbe.status_code, detail: bcProbe.detail })
      : naspStatus === "error"
        ? formatValue(naspError ?? "erro ao consultar fonte real")
        : awaiting;

  const orchestrationStatus =
    naspStatus === "loading"
      ? "loading"
      : naspStatus === "error"
        ? "error"
        : "ready";

  const orchestrationRows =
    naspStatus === "ready" && naspDiagnostics && typeof naspDiagnostics === "object"
      ? [
          { label: "sem_csmf", value: formatValue(naspDiagnostics["sem_csmf"]) },
          { label: "ml_nsmf", value: formatValue(naspDiagnostics["ml_nsmf"]) },
          { label: "decision", value: formatValue(naspDiagnostics["decision"]) },
          { label: "bc_nssmf", value: formatValue(naspDiagnostics["bc_nssmf"]) },
          { label: "sla_agent", value: formatValue(naspDiagnostics["sla_agent"]) },
        ]
      : [];

  return (
    <section>
      <h1>SLA Lifecycle</h1>
      <p className="trisla-subtitle">Scientific SLA lifecycle runtime evidence.</p>
      <div className="trisla-cards-grid">
        <section className="trisla-status-card" aria-label="Semantic Admission">
          <h2>Semantic Admission</h2>
          <DataState status={naspStatus} errorMessage={naspError}>
            <dl>
              <div className="trisla-status-row">
                <dt>Status</dt>
                <dd>{semStatusText}</dd>
              </div>
              <div className="trisla-status-row">
                <dt>Recommendation</dt>
                <dd>{semRecommendation}</dd>
              </div>
            </dl>
          </DataState>
        </section>

        <section className="trisla-status-card" aria-label="ML Decision">
          <h2>ML Decision</h2>
          <DataState status={naspStatus} errorMessage={naspError}>
            <dl>
              <div className="trisla-status-row">
                <dt>Decision confidence</dt>
                <dd>{mlDecisionConfidence}</dd>
              </div>
              <div className="trisla-status-row">
                <dt>Decision status</dt>
                <dd>{mlDecisionStatus}</dd>
              </div>
            </dl>
          </DataState>
        </section>

        <section className="trisla-status-card" aria-label="Blockchain Commit">
          <h2>Blockchain Commit</h2>
          <DataState status={naspStatus} errorMessage={naspError}>
            <dl>
              <div className="trisla-status-row">
                <dt>Commit status</dt>
                <dd>{bcCommitStatus}</dd>
              </div>
              <div className="trisla-status-row">
                <dt>Trust evidence</dt>
                <dd>{bcTrustEvidence}</dd>
              </div>
            </dl>
          </DataState>
        </section>

        <section className="trisla-status-card" aria-label="Runtime orchestration">
          <h2>Runtime orchestration</h2>
          <DataState status={orchestrationStatus as Status} errorMessage={naspError}>
            <dl>
              {orchestrationRows.length > 0 ? (
                orchestrationRows.map(({ label, value }) => (
                  <div key={label} className="trisla-status-row">
                    <dt>{label}</dt>
                    <dd>{value}</dd>
                  </div>
                ))
              ) : (
                <div className="trisla-status-row">
                  <dt>Source</dt>
                  <dd>{naspStatus === "error" ? formatValue(naspError) : "NASP diagnostics"}</dd>
                </div>
              )}
            </dl>
          </DataState>
        </section>
      </div>
    </section>
  );
}
