/**
 * RC-P20-04A explainability recovery tests.
 * Run: npx tsx src/lib/explainabilityRecovery.test.ts
 */

import { formatMetricValue, metricDisplayName } from "./domainExplainability";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

assert(
  formatMetricValue(0.001199, "cpu") === "0.12 %",
  "cpu fractional display scaled to percent",
);
assert(formatMetricValue(0, "cpu") === "0 %", "cpu zero unchanged");
assert(formatMetricValue(5.2, "latency_ms") === "5.20 ms", "latency not scaled");
assert(formatMetricValue(0.05, "packet_loss") === "0.05 %", "packet_loss not scaled");

assert(
  metricDisplayName("cpu_utilization", {
    measurement_note: "RAN cpu_utilization observed via PRB/prb_utilization alias (Sprint 9D).",
  }) === "PRB Utilization",
  "PRB alias label",
);

console.log("explainabilityRecovery.test.ts: OK");
