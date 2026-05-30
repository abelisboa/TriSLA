/**
 * Sprint 5M2 — lifecycle runtime snapshot mapping tests (node, no deps).
 * Run: node apps/portal-frontend/scripts/test-lifecycle-runtime-snapshot.mjs
 */

function pick(obj, keys) {
  if (!obj || typeof obj !== "object") return undefined;
  for (const key of keys) {
    const v = obj[key];
    if (v !== null && v !== undefined && v !== "") return v;
  }
  return undefined;
}

function ranRows(ran) {
  if (!ran) return [];
  const rows = [];
  const prb = pick(ran, ["prb_utilization"]);
  const load = pick(ran, ["latency_ms", "latency", "radio_load"]);
  if (prb !== undefined) rows.push(["PRB Utilization", prb]);
  if (load !== undefined) rows.push(["Radio Load", load]);
  return rows;
}

function transportRows(transport) {
  if (!transport) return [];
  const rows = [];
  const latency = pick(transport, ["latency_ms", "rtt_ms", "rtt", "latency"]);
  const jitter = pick(transport, ["jitter_ms", "jitter"]);
  const throughput = pick(transport, ["throughput_mbps", "throughput"]);
  if (latency !== undefined) rows.push(["Latency", latency]);
  if (jitter !== undefined) rows.push(["Jitter", jitter]);
  if (throughput !== undefined) rows.push(["Throughput", throughput]);
  return rows;
}

function coreRows(core) {
  if (!core) return [];
  const rows = [];
  const cpu = pick(core, ["cpu_utilization", "cpu"]);
  const memory = pick(core, ["memory_bytes", "memory", "memory_utilization"]);
  if (cpu !== undefined) rows.push(["CPU", cpu]);
  if (memory !== undefined) rows.push(["Memory", memory]);
  return rows;
}

function isPopulated(snap) {
  return (
    ranRows(snap.ran).length > 0 ||
    transportRows(snap.transport).length > 0 ||
    coreRows(snap.core).length > 0
  );
}

const FIXTURES = {
  urllc: {
    ran: { prb_utilization: 0.0, latency_ms: 10 },
    transport: { rtt_ms: 5.0, jitter_ms: 1.1 },
    core: { cpu_utilization: 0.001, memory_bytes: 0.008 },
  },
  embb: {
    ran: { prb_utilization: 0.1, latency_ms: 50 },
    transport: { rtt_ms: 4.5, jitter_ms: 0.9 },
    core: { cpu_utilization: 0.002, memory_bytes: 0.009 },
  },
  mmtc: {
    ran: { prb_utilization: 0.05, latency_ms: 1000 },
    transport: { rtt_ms: 6.0 },
    core: { cpu_utilization: 0.003, memory_bytes: 0.01 },
  },
  smartcity: {
    ran: { prb_utilization: 0.02, latency_ms: 50 },
    transport: { rtt_ms: 5.2, jitter_ms: 1.0 },
    core: { cpu_utilization: 0.0015, memory_bytes: 0.007 },
  },
};

let failed = 0;
for (const [name, snap] of Object.entries(FIXTURES)) {
  if (!isPopulated(snap)) {
    console.error(`FAIL ${name}: snapshot not populated`);
    failed += 1;
    continue;
  }
  if (ranRows(snap.ran).length === 0) {
    console.error(`FAIL ${name}: RAN empty`);
    failed += 1;
  }
  if (transportRows(snap.transport).length === 0) {
    console.error(`FAIL ${name}: Transport empty`);
    failed += 1;
  }
  if (coreRows(snap.core).length === 0) {
    console.error(`FAIL ${name}: Core empty`);
    failed += 1;
  }
  if (failed === 0) console.log(`PASS ${name}`);
}

if (failed > 0) {
  process.exit(1);
}
console.log("All lifecycle runtime snapshot mapping tests passed.");
