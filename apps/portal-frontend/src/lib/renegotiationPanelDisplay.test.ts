/**
 * P6 — Renegotiation panel payload-driven rendering.
 * Run: npx tsx src/lib/renegotiationPanelDisplay.test.ts
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { extractRenegotiationFields } from "./renegotiationPanelDisplay";
import { displayField } from "./submitResponse";
import type { SubmitResponse } from "./submitResponse";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

const FORBIDDEN_FALLBACKS = [
  '"eMBB"',
  '"5 ms"',
  '"10 ms"',
  '"100 Mbps"',
  '"1 Gbps"',
  "relax URLLC latency target",
  "migrate to eMBB profile",
];

function slicePayload(slice: "URLLC" | "eMBB" | "mMTC") {
  const profiles = {
    URLLC: { slice_type: "URLLC", latency_ms: 5 },
    eMBB: { slice_type: "eMBB", latency_ms: 50 },
    mMTC: { slice_type: "mMTC", latency_ms: 100 },
  } as const;
  const suggested = {
    URLLC: { slice_type: "URLLC", latency_ms: 10 },
    eMBB: { slice_type: "eMBB", latency_ms: 80 },
    mMTC: { slice_type: "mMTC", latency_ms: 200 },
  } as const;

  return {
    decision: "RENEGOTIATE",
    sla_requirements: profiles[slice],
    metadata: {
      canonical_sla: suggested[slice],
      decision_explanation_plain: `${slice} renegotiation from payload`,
    },
  } satisfies SubmitResponse;
}

// T1 — URLLC payload
{
  const fields = extractRenegotiationFields(undefined, slicePayload("URLLC"));
  assert(displayField(fields.requestedType) === "URLLC", "T1 requested profile");
  assert(displayField(fields.requestedLatency) === "5", "T1 requested latency");
  assert(displayField(fields.suggestedType) === "URLLC", "T1 suggested profile");
  assert(displayField(fields.suggestedLatency) === "10", "T1 suggested latency");
  assert(
    displayField(fields.explanation) === "URLLC renegotiation from payload",
    "T1 explanation",
  );
}

// T2 — eMBB payload
{
  const fields = extractRenegotiationFields(undefined, slicePayload("eMBB"));
  assert(displayField(fields.requestedType) === "eMBB", "T2 requested profile");
  assert(displayField(fields.suggestedType) === "eMBB", "T2 suggested profile");
  assert(displayField(fields.suggestedLatency) === "80", "T2 suggested latency");
}

// T3 — mMTC payload
{
  const fields = extractRenegotiationFields(undefined, slicePayload("mMTC"));
  assert(displayField(fields.requestedType) === "mMTC", "T3 requested profile");
  assert(displayField(fields.suggestedType) === "mMTC", "T3 suggested profile");
  assert(displayField(fields.suggestedLatency) === "200", "T3 suggested latency");
}

// T4 — payload without proposal fields
{
  const response = {
    decision: "RENEGOTIATE",
    metadata: {},
  } satisfies SubmitResponse;
  const fields = extractRenegotiationFields(undefined, response);
  assert(displayField(fields.requestedType) === "Not available", "T4 requested profile");
  assert(displayField(fields.requestedLatency) === "Not available", "T4 requested latency");
  assert(displayField(fields.suggestedType) === "Not available", "T4 suggested profile");
  assert(displayField(fields.suggestedLatency) === "Not available", "T4 suggested latency");
  assert(displayField(fields.explanation) === "Not available", "T4 explanation");
}

// T5 — no hardcoded SLA fallbacks in panel source
{
  const panelPath = resolve(
    fileURLToPath(new URL(".", import.meta.url)),
    "../components/gating/RenegotiationProposalPanel.tsx",
  );
  const source = readFileSync(panelPath, "utf8");
  for (const forbidden of FORBIDDEN_FALLBACKS) {
    assert(!source.includes(forbidden), `T5 forbidden hardcode present: ${forbidden}`);
  }
  assert(!source.includes("?? requestedType"), "T5 no requestedType fallback for suggested");
}

console.log("renegotiationPanelDisplay.test.ts: all tests passed");
