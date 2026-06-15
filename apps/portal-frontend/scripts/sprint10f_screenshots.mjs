import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";

const BASE = "http://127.0.0.1:3001";
const OUT = process.argv[2];
const ACCEPT_ID = "cb527ea5-f95b-4814-8312-08ccd6f7b4fe";

const REJECT_STATUS = {
  sla_id: "mock-reject-id",
  intent_id: "mock-reject-id",
  admission_decision: "REJECT",
  runtime_lifecycle_enabled: false,
  admission_reasoning: "PRB threshold exceeded (mock evidence).",
  admission_decision_evidence: [
    { metric: "prb_utilization", observed: 0.45, threshold: 0.4, delta: 0.05, rule: "HARD_PRB_REJECT", unit: "%" },
  ],
  operational_summary: { admission_decision: "REJECT", ml_confidence: 0.72, decision_score: 0.31 },
};

const RENEG_STATUS = {
  sla_id: "mock-reneg-id",
  intent_id: "mock-reneg-id",
  admission_decision: "RENEGOTIATE",
  runtime_lifecycle_enabled: false,
  admission_reasoning: "PRB renegotiation band (mock evidence).",
  admission_decision_evidence: [
    { metric: "prb_utilization", observed: 0.3, threshold: 0.25, delta: 0.05, rule: "HARD_PRB_RENEGOTIATE", unit: "%" },
  ],
  operational_summary: { admission_decision: "RENEGOTIATE", ml_confidence: 0.68, decision_score: 0.55 },
};

await mkdir(OUT, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

async function mockStatus(body) {
  await page.route("**/api/v1/sla/status/**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(body),
    });
  });
}

async function shot(name, path) {
  await page.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/${name}`, fullPage: true });
}

await shot("accept_sidebar_admission.png", `/sla-lifecycle?view=admission&intent_id=${ACCEPT_ID}`);

await page.goto(`${BASE}/sla-lifecycle?view=admission&intent_id=${ACCEPT_ID}`, { waitUntil: "networkidle" });
await page.waitForTimeout(3000);
await page.screenshot({ path: `${OUT}/accept_sidebar_runtime_nav_visible.png`, fullPage: false });

await mockStatus(REJECT_STATUS);
await shot("reject_sidebar_no_runtime_nav.png", "/sla-lifecycle?view=admission&intent_id=mock-reject-id");
await shot("reject_admission_analysis.png", "/sla-lifecycle?view=admission&intent_id=mock-reject-id");

await mockStatus(RENEG_STATUS);
await shot("renegotiate_sidebar_no_runtime_nav.png", "/sla-lifecycle?view=admission&intent_id=mock-reneg-id");
await shot("renegotiate_admission_analysis.png", "/sla-lifecycle?view=admission&intent_id=mock-reneg-id");

await browser.close();
console.log("screenshots OK:", OUT);
