/** ACTIVE vs WARNING operational model (Sprint 5N). */

export const LIFECYCLE_ACTIVE_EXPLANATION =
  "The service is in operation — the SLA intent is registered and active in the runtime catalog.";

export const RUNTIME_ASSURANCE_WARNING_EXPLANATION =
  "Runtime metrics show elevated risk in one or more domains. This is observational guidance only — no SLA violation is registered and no automatic remediation is triggered.";

export const RUNTIME_ASSURANCE_COMPLIANT_EXPLANATION =
  "Runtime metrics are within configured SLA observation bands.";

export const ACTIVE_VS_WARNING_SUMMARY =
  "ACTIVE means the service is operating. WARNING means elevated runtime risk was detected without automatic remediation.";

export function assuranceExplanationForState(state: string | undefined): string | undefined {
  switch (state) {
    case "COMPLIANT":
      return RUNTIME_ASSURANCE_COMPLIANT_EXPLANATION;
    case "WARNING":
      return RUNTIME_ASSURANCE_WARNING_EXPLANATION;
    case "AT_RISK":
      return "Runtime risk indicators require operator review. The service remains active.";
    case "VIOLATED":
      return "SLA observation bands report a violation indicator. Escalation is recommended — no automatic network change is performed.";
    case "INCOMPLETE":
      return "Telemetry was incomplete during the last evaluation; assurance state cannot be fully determined until revalidation succeeds.";
    default:
      return undefined;
  }
}
