#!/usr/bin/env node
/** Sprint 5N operator UX unit tests (node, no deps). */

function formatModuleOperationalState(probe, loadState = "ready") {
  if (loadState === "loading" || loadState === "idle") return "Loading";
  if (loadState === "error") return "Unavailable";
  if (!probe || typeof probe !== "object") return "Unavailable";
  if (probe.reachable === true) {
    if (probe.status_code === 200 || probe.detail === "ok") return "Operational";
    return "Operational";
  }
  if (probe.reachable === false) return "Unavailable";
  return "Unavailable";
}

let failed = 0;
const cases = [
  { name: "operational_probe", probe: { reachable: true, status_code: 200, detail: "ok" }, expect: "Operational" },
  { name: "unavailable_probe", probe: { reachable: false }, expect: "Unavailable" },
  { name: "loading", probe: {}, load: "loading", expect: "Loading" },
];

for (const c of cases) {
  const got = formatModuleOperationalState(c.probe, c.load ?? "ready");
  if (got === c.expect) console.log(`PASS ${c.name}`);
  else {
    failed += 1;
    console.log(`FAIL ${c.name} got=${got}`);
  }
}

if (failed) process.exit(1);
console.log("All operator UX mapping tests passed.");
