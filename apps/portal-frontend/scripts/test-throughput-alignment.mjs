#!/usr/bin/env node
/** Sprint 5N4_2 — throughput formatting + card placement (mirrors operatorFormat / domainMonitoringCards). */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, "..");

function formatThroughputMbps(value) {
  if (value === null || value === undefined || value === "") return "Not available";
  const n = typeof value === "number" ? value : Number(String(value).trim());
  if (!Number.isFinite(n)) return "Not available";
  return `${n.toFixed(2)} Mbps`;
}

function bpsToMbps(bps) {
  return bps / 1_000_000;
}

let failed = 0;

function assertEq(name, got, expect) {
  if (got === expect) console.log(`PASS ${name}`);
  else {
    failed += 1;
    console.log(`FAIL ${name} got=${JSON.stringify(got)} expect=${JSON.stringify(expect)}`);
  }
}

assertEq("0 bps → 0 Mbps", bpsToMbps(0), 0);
assertEq("10 Mbps display", formatThroughputMbps(10), "10.00 Mbps");
assertEq("100 Mbps display", formatThroughputMbps(100), "100.00 Mbps");
assertEq("0 Mbps display", formatThroughputMbps(0), "0.00 Mbps");
assertEq("10M bps → 10 Mbps", bpsToMbps(10_000_000), 10);
assertEq("100M bps → 100 Mbps", bpsToMbps(100_000_000), 100);

const cardsSrc = fs.readFileSync(path.join(root, "src/lib/domainMonitoringCards.ts"), "utf8");
const summarySrc = fs.readFileSync(path.join(root, "src/lib/prometheusSummary.ts"), "utf8");

if (cardsSrc.includes('row("Dataplane Throughput (N6)"')) {
  console.log("PASS ran card has Dataplane Throughput (N6)");
} else {
  failed += 1;
  console.log("FAIL ran card missing Dataplane Throughput (N6)");
}

if (!cardsSrc.includes('row("Throughput (Mbps)"')) {
  console.log("PASS transport card has no Throughput row");
} else {
  failed += 1;
  console.log("FAIL transport card still has Throughput row");
}

if (summarySrc.includes('label: "Observed Throughput"')) {
  console.log("PASS summary Observed Throughput label");
} else {
  failed += 1;
  console.log("FAIL summary missing Observed Throughput label");
}

if (summarySrc.includes("RAN dataplane throughput proxy (N6 peer ingress)")) {
  console.log("PASS summary throughput tooltip");
} else {
  failed += 1;
  console.log("FAIL summary missing throughput tooltip");
}

if (failed) process.exit(1);
console.log("All throughput alignment tests passed.");
