/**
 * Lightweight assertions — run: npx tsx src/lib/phaseNextConsistency.test.ts
 */

import {
  fidelityStatusLabel,
  formatComplianceDisplay,
  formatDelta,
  operationalStatusFromAssurance,
  parseDecisionEvidence,
} from "./phaseNextConsistency";
import type { RuntimeAssurancePayload } from "./runtimeAssurance";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

const evidence = parseDecisionEvidence([
  {
    metric: "prb_utilization",
    observed: 27.65,
    threshold: 25,
    delta: 2.65,
    rule: "PRB_HARD_RENEGOTIATE_THRESHOLD",
  },
]);
assert(evidence.length === 1, "evidence row");
assert(formatDelta(2.65) === "+2.65", "delta format");

const ra: RuntimeAssurancePayload = { operational_status: "PENDING_RENEGOTIATION" };
assert(operationalStatusFromAssurance(ra) === "PENDING_RENEGOTIATION", "operational_status");

assert(formatComplianceDisplay(39, { alreadyPercent: true }) === "39%", "admission %");
assert(formatComplianceDisplay(0.72) === "72%", "runtime fraction");

assert(fidelityStatusLabel(true) === "CONSISTENT", "consistent");
assert(fidelityStatusLabel(false) === "UPDATED SNAPSHOT", "updated");

console.log("phaseNextConsistency.test.ts: OK");
