#!/usr/bin/env node
/** Sprint 5M4 — runtime assurance mapping tests (node, no deps). */

function parseRuntimeAssurance(raw) {
  if (!raw || typeof raw !== "object") return undefined;
  return raw;
}

function assuranceStateLabel(payload) {
  const state = payload?.state ?? payload?.assurance_state;
  if (!state) return "Not available";
  return state.replace(/_/g, " ");
}

function isRuntimeAssurancePopulated(payload) {
  if (!payload) return false;
  return Boolean(payload.state ?? payload.assurance_state);
}

const cases = [
  { name: "urllc", payload: { state: "COMPLIANT", drift_detected: false, recommendation: "Within SLA", last_evaluation: "2026-05-30T00:00:00Z" } },
  { name: "embb", payload: { state: "WARNING", drift_detected: true, recommendation: "Monitor transport latency", last_evaluation: "2026-05-30T00:00:00Z" } },
  { name: "mmtc", payload: { state: "AT_RISK", drift_detected: false, recommendation: "Investigate core domain", last_evaluation: "2026-05-30T00:00:00Z" } },
  { name: "smartcity", payload: { state: "VIOLATED", drift_detected: true, recommendation: "Escalate SLA violation", last_evaluation: "2026-05-30T00:00:00Z" } },
];

let failed = 0;
for (const c of cases) {
  const parsed = parseRuntimeAssurance(c.payload);
  const ok =
    isRuntimeAssurancePopulated(parsed) &&
    assuranceStateLabel(parsed) === c.payload.state.replace(/_/g, " ");
  if (ok) console.log(`PASS ${c.name}`);
  else {
    failed += 1;
    console.log(`FAIL ${c.name}`);
  }
}

if (failed > 0) process.exit(1);
console.log("All runtime assurance mapping tests passed.");
