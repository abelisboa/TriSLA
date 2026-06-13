/**
 * RC-P20-03 compliance separation tests.
 * Run: npx tsx src/lib/complianceSeparation.test.ts
 */

import {
  observedCoreRows,
  observedRanRows,
  observedTransportRows,
  filterObservedDomainObject,
  OBSERVED_TRANSPORT_FIELDS,
} from "./observedTelemetry";
import { hasDomainExplainability, parseDomainExplainability } from "./domainExplainability";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

const snapshot = {
  ran: { prb_utilization: 0.1, latency_ms: 5.2, reliability_pct: null },
  transport: {
    rtt_ms: 4.9,
    jitter_ms: 1.2,
    bandwidth_mbps: 0,
    packet_loss_pct: null,
    throughput_mbps: undefined,
  },
  core: { cpu_utilization: 0.02, memory_bytes: 1e6, availability_pct: null },
};

const transportRows = observedTransportRows(snapshot.transport);
assert(transportRows.some((r) => r.label === "Bandwidth"), "bandwidth_mbps shown as Bandwidth");
assert(!transportRows.some((r) => r.label === "Compliance Score"), "no compliance in telemetry");

const filtered = filterObservedDomainObject(snapshot.transport, OBSERVED_TRANSPORT_FIELDS);
assert(filtered?.bandwidth_mbps === 0, "canonical bandwidth key in filtered object");
assert(filtered?.throughput_mbps === undefined, "no duplicate throughput key");

const assurance = {
  domain_explainability: {
    transport: [
      {
        metric: "bandwidth",
        observed: 0,
        threshold: 100,
        compliance_score: 0.5,
        status: "N/A",
        source: "telemetry_snapshot.transport",
      },
    ],
  },
};
const de = parseDomainExplainability(assurance.domain_explainability);
assert(hasDomainExplainability(de), "compliance payload parseable");
assert(de?.transport?.[0]?.compliance_score === 0.5, "compliance score in explainability only");

assert(!observedRanRows({ rsrp: -80 }).some((r) => r.label.includes("RSRP")), "RSRP not shown");

console.log("complianceSeparation.test.ts: OK");
