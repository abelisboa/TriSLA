#!/usr/bin/env node
/** Sprint 5N5_1 — Administration cleanup unit checks (source assertions). */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const adminSrc = fs.readFileSync(
  path.join(__dirname, "../src/app/administration/page.tsx"),
  "utf8",
);
const endpointsSrc = fs.readFileSync(
  path.join(__dirname, "../src/lib/endpoints.ts"),
  "utf8",
);

let failed = 0;

function pass(name) {
  console.log(`PASS ${name}`);
}

function fail(name, detail) {
  failed += 1;
  console.log(`FAIL ${name}: ${detail}`);
}

if (!adminSrc.includes("NASP details URL")) {
  pass("NASP details URL row removed");
} else {
  fail("NASP details URL row removed", "still referenced");
}

if (!adminSrc.includes("nasp_details_url")) {
  pass("nasp_details_url binding removed");
} else {
  fail("nasp_details_url binding removed", "still in source");
}

if (adminSrc.includes('apiRequest<PlatformHealth>("PLATFORM_HEALTH")')) {
  pass("Version sourced from PLATFORM_HEALTH");
} else {
  fail("Version sourced from PLATFORM_HEALTH", "missing fetch");
}

if (endpointsSrc.includes('PLATFORM_HEALTH: "/health"')) {
  pass("PLATFORM_HEALTH endpoint registered");
} else {
  fail("PLATFORM_HEALTH endpoint registered", "missing in endpoints.ts");
}

if (adminSrc.includes("inferNaspReachability(nasp)")) {
  pass("NASP connectivity uses diagnostics inference");
} else {
  fail("NASP connectivity uses diagnostics inference", "missing");
}

if (adminSrc.includes("NASP probe details")) {
  pass("NASP probe details card retained");
} else {
  fail("NASP probe details card retained", "missing");
}

if (adminSrc.includes("Service endpoints")) {
  pass("Service endpoints card retained");
} else {
  fail("Service endpoints card retained", "missing");
}

if (failed) process.exit(1);
console.log("All administration cleanup tests passed.");
