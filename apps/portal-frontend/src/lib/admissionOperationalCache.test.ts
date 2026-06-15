/**
 * P5 — admission operational cache payload-driven rendering.
 * Run: npx tsx src/lib/admissionOperationalCache.test.ts
 */

import { buildAdmissionOperationalSnapshot } from "./admissionOperationalCache";
import { displayField } from "./submitResponse";
import type { SubmitResponse } from "./submitResponse";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

const INFERRED_LABELS = ["Passed", "Review required", "Review", "Approved", "Failed"];

function displaySemantic(value: string | undefined): string {
  return value !== undefined && value.trim() ? value : "Not available";
}

// T1 — field present in payload
{
  const response = {
    intent_id: "intent-t1",
    decision: "ACCEPT",
    nest_id: "nest-1",
    metadata: {
      semantic_validation: "Validated by SEM",
      gst_generated: "Yes",
      nest_generated: "Yes",
      semantic_fill: "Applied",
    },
  } satisfies SubmitResponse;
  const snap = buildAdmissionOperationalSnapshot(response);
  assert(snap !== null, "T1 snapshot");
  assert(snap!.semantic_validation === "Validated by SEM", "T1 semantic_validation");
  assert(displaySemantic(snap!.semantic_validation) === "Validated by SEM", "T1 display");
}

// T2 — field absent → Not available
{
  const response = {
    intent_id: "intent-t2",
    decision: "ACCEPT",
    metadata: {},
  } satisfies SubmitResponse;
  const snap = buildAdmissionOperationalSnapshot(response)!;
  assert(displaySemantic(snap.semantic_validation) === "Not available", "T2 semantic");
  assert(displaySemantic(snap.gst_generated) === "Not available", "T2 gst");
  assert(displaySemantic(snap.nest_generated) === "Not available", "T2 nest");
  assert(displaySemantic(snap.semantic_fill) === "Not available", "T2 fill");
}

// T3 — no semantic_validation; must not infer Passed/Review from decision
{
  const forAccept = buildAdmissionOperationalSnapshot({
    intent_id: "intent-t3a",
    decision: "ACCEPT",
    nest_id: "nest-x",
    metadata: { telemetry_snapshot: { ran: {} } },
  })!;
  const forReject = buildAdmissionOperationalSnapshot({
    intent_id: "intent-t3b",
    decision: "REJECT",
    metadata: {},
  })!;
  for (const snap of [forAccept, forReject]) {
    assert(snap.semantic_validation === undefined, "T3 no semantic_validation cached");
    assert(
      !INFERRED_LABELS.includes(snap.semantic_validation ?? ""),
      "T3 no Passed/Review inference",
    );
    assert(snap.gst_generated === undefined, "T3 no gst inference from nest_id");
    assert(snap.semantic_fill === undefined, "T3 no semantic_fill inference from telemetry");
  }
}

// T4 — URLLC / eMBB / mMTC payload equivalence
for (const slice of ["URLLC", "eMBB", "mMTC"] as const) {
  const payload = {
    semantic_validation: `${slice} backend label`,
    gst_generated: "Yes",
    nest_generated: "Yes",
    semantic_fill: "Applied",
  };
  const response = {
    intent_id: `intent-${slice.toLowerCase()}`,
    decision: "ACCEPT",
    metadata: { operational_summary: payload },
  } satisfies SubmitResponse;
  const snap = buildAdmissionOperationalSnapshot(response)!;
  assert(snap.semantic_validation === payload.semantic_validation, `T4 ${slice} semantic`);
  assert(displayField(snap.gst_generated) === payload.gst_generated, `T4 ${slice} gst`);
}

console.log("admissionOperationalCache.test.ts: OK (T1–T4)");
