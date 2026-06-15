import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import { writeFile } from "node:fs/promises";

const BASE = process.env.TRISLA_FRONTEND_URL || "http://127.0.0.1:32001";
const OUT = process.argv[2];
const SLICE = process.argv[3] || "embb";
const INTENT = process.argv[4];

const views = [
  { name: "01_admission_analysis", view: "admission", label: "Admission Analysis" },
  { name: "02_service_profile", view: "serviceProfile", label: "Service Profile" },
  { name: "03_observed_telemetry", view: "telemetry", label: "Observed Telemetry" },
  { name: "04_compliance_evaluation", view: "runtimeCompliance", label: "Compliance Evaluation" },
  { name: "05_decision_evidence", view: "decisionEvidence", label: "Decision Evidence" },
  { name: "06_runtime_assurance", view: "assurance", label: "Runtime Assurance" },
  { name: "07_domain_explainability", view: "runtimeCompliance", label: "Domain Explainability" },
  { name: "08_governance", view: "governance", label: "Governance" },
];

await mkdir(`${OUT}/${SLICE}`, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });

const checks = {};
for (const v of views) {
  const url = `${BASE}/sla-lifecycle?intent_id=${INTENT}&view=${v.view}`;
  await page.goto(url, { waitUntil: "networkidle", timeout: 120000 });
  await page.waitForTimeout(3000);
  const text = await page.locator("body").innerText();
  checks[v.name] = {
    url,
    hasContent: text.length > 200,
    packetLoss: /packet loss|packet_loss/i.test(text),
    reliability: /reliability/i.test(text),
    availability: /availability/i.test(text),
    prb: /PRB Utilization|prb/i.test(text),
    compliance: /Compliance Evaluation|Compliance Score/i.test(text),
  };
  await page.screenshot({ path: `${OUT}/${SLICE}/${v.name}.png`, fullPage: true });
}

await writeFile(`${OUT}/${SLICE}/ui_checks.json`, JSON.stringify({ slice: SLICE, intent: INTENT, checks }, null, 2));
await browser.close();
console.log(`screenshots OK ${SLICE}`);
