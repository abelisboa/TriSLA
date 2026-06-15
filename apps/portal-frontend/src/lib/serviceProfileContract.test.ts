/**
 * RC-P20-01 — Service Profile contract fields.
 * Run: npx tsx src/lib/serviceProfileContract.test.ts
 */

import {
  SERVICE_PROFILE_SOURCE,
  serviceProfileContractFields,
} from "./serviceProfileContract";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

const sla = {
  slice_type: "URLLC",
  template_id: "urllc-template-001",
  latency: "10ms",
  throughput: "100Mbps",
  reliability: 0.99999,
  availability: 0.99999,
  jitter: "5ms",
  coverage: "Urban",
  device_density: 1000,
};

const rows = serviceProfileContractFields(sla, "URLLC");
assert(rows.length === 9, "nine contract rows");
assert(rows[0].label === "Slice Type" && rows[0].value === "URLLC", "slice type");
assert(rows[1].value === "urllc-template-001", "template");
assert(rows[8].label === "Device Density Requirement", "device density label");
assert(SERVICE_PROFILE_SOURCE === "SEM-CSMF", "source constant");

console.log("serviceProfileContract.test.ts — PASS");
