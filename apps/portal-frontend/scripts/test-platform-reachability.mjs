#!/usr/bin/env node
/** Sprint 5N2 platform reachability unit tests (node, no deps). */

const NASP_MODULE_KEYS = [
  "sem_csmf",
  "ml_nsmf",
  "decision",
  "bc_nssmf",
  "sla_agent",
];

function moduleReachable(mod) {
  if (!mod || typeof mod !== "object") return false;
  if (mod.reachable === true) return true;
  if (mod.status_code === 200 || mod.status_code === "200") return true;
  return false;
}

function aggregateFromDiagnostics(diagnostics) {
  if (!diagnostics) return null;
  const total = NASP_MODULE_KEYS.length;
  const reachable = NASP_MODULE_KEYS.filter((key) =>
    moduleReachable(diagnostics[key]),
  ).length;
  return {
    reachable_modules: reachable,
    total_modules: total,
    reachability_percent: total ? Math.round((100 * reachable) / total) : 0,
  };
}

function formatPlatformReachability(aggregate, loadState = "ready") {
  if (loadState === "loading" || loadState === "idle") return "Loading…";
  if (loadState === "error" || !aggregate) return "Unavailable";
  const { reachable_modules, total_modules, reachability_percent } = aggregate;
  if (total_modules === 0) return "Unavailable";
  if (reachable_modules === total_modules) {
    return `${reachable_modules}/${total_modules} Operational`;
  }
  if (reachable_modules === 0) {
    return `0/${total_modules} Unavailable`;
  }
  return `${reachable_modules}/${total_modules} Operational (${reachability_percent}%)`;
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

const allUp = {
  sem_csmf: { reachable: true, status_code: 200 },
  ml_nsmf: { reachable: true, status_code: 200 },
  decision: { reachable: true, status_code: 200 },
  bc_nssmf: { reachable: true, status_code: 200 },
  sla_agent: { reachable: true, status_code: 200 },
};

const agg = aggregateFromDiagnostics(allUp);
assert(agg.reachable_modules === 5, "reachable_modules");
assert(formatPlatformReachability(agg) === "5/5 Operational", "all operational");

const partial = aggregateFromDiagnostics({ ...allUp, sla_agent: { reachable: false } });
assert(
  formatPlatformReachability(partial) === "4/5 Operational (80%)",
  "partial format",
);

console.log("PASS platformReachability tests");
