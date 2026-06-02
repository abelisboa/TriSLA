/**
 * Lightweight assertions for Sprint 6B explainability helpers (run: npx tsx ... if needed).
 */

import {
  buildWhyExplanations,
  formatCompliancePercent,
  whySectionHeading,
} from "./runtimeAssuranceExplainability";
import type { RuntimeAssurancePayload } from "./runtimeAssurance";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

const warningPayload: RuntimeAssurancePayload = {
  state: "WARNING",
  bottleneck_domain: "transport",
  domain_compliance: { ran: 0.7, transport: 0.0, core: 0.99 },
  sla_compliance: 0.71,
  recommendation: "Monitor review transport domain",
  violations: [],
  warnings: [],
  drift_indicators: [],
};

assert(whySectionHeading("WARNING") === "WHY WARNING?", "warning heading");
assert(formatCompliancePercent(0.706) === "71%", "compliance percent");
const why = buildWhyExplanations(warningPayload, {
  transport: { rtt_ms: 14.2 },
});
assert(why.length >= 1, "bottleneck why when empty violations");
assert(why[0].source.includes("bottleneck"), "bottleneck source");

const driftPayload: RuntimeAssurancePayload = {
  state: "AT_RISK",
  drift_indicators: [{ path: "transport.rtt", reference: 10, current: 14.2, delta: 4.2 }],
  violations: ["service_profile.latency"],
};
const whyDrift = buildWhyExplanations(driftPayload, undefined);
assert(whyDrift.some((w) => w.observed?.includes("14.2")), "drift observed");
assert(whyDrift.some((w) => w.source === "violations"), "violation code");

console.log("runtimeAssuranceExplainability.test.ts: OK");
