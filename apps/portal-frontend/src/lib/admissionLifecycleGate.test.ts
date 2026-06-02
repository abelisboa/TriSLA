/**
 * Lightweight gate matrix tests — run: npx tsx src/lib/admissionLifecycleGate.test.ts
 */
import {
  admissionDecisionFromStatus,
  isRuntimeLifecycleEnabled,
  showLifecycleSection,
} from "./admissionLifecycleGate";
import type { SlaRuntimeStatusResponse } from "./runtimeSupervision";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

const acceptStatus: SlaRuntimeStatusResponse = {
  admission_decision: "ACCEPT",
  runtime_lifecycle_enabled: true,
};

const rejectStatus: SlaRuntimeStatusResponse = {
  admission_decision: "REJECT",
  runtime_lifecycle_enabled: false,
};

assert(admissionDecisionFromStatus(acceptStatus) === "ACCEPT", "accept decision");
assert(isRuntimeLifecycleEnabled(acceptStatus), "accept runtime");
assert(showLifecycleSection("runtimeSnapshot", "ACCEPT"), "accept snapshot");
assert(!showLifecycleSection("runtimeSnapshot", "REJECT"), "reject no snapshot");
assert(showLifecycleSection("whyRejected", "REJECT"), "reject why panel");
assert(!showLifecycleSection("whyRejected", "ACCEPT"), "accept no why rejected");
assert(showLifecycleSection("renegotiationProposal", "RENEGOTIATE"), "reneg proposal");
assert(!showLifecycleSection("viewRuntimeCta", "REJECT"), "reject no cta");
assert(admissionDecisionFromStatus(rejectStatus) === "REJECT", "reject from status");

console.log("admissionLifecycleGate.test.ts: OK");
