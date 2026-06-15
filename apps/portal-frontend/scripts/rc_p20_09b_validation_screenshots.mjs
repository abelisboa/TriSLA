import { chromium } from "playwright";
import { mkdir, writeFile } from "node:fs/promises";

const BASE = process.env.TRISLA_FRONTEND_URL || "http://127.0.0.1:32001";
const OUT = process.argv[2];
const SLICE = process.argv[3];
const INTENT = process.argv[4];

const views = [
  { name: "01_admission_analysis", view: "admission" },
  { name: "02_service_profile", view: "serviceProfile" },
  { name: "03_observed_telemetry", view: "telemetry" },
  { name: "04_compliance_evaluation", view: "runtimeCompliance" },
  { name: "05_decision_evidence", view: "decisionEvidence" },
  { name: "06_runtime_assurance", view: "assurance" },
  { name: "07_domain_explainability", view: "runtimeCompliance" },
  { name: "08_governance", view: "governance" },
];

const PT_PATTERNS = [
  /não disponível/i,
  /conformidade/i,
  /decisão/i,
  /governança/i,
  /telemetria/i,
  /requisito/i,
  /violacao/i,
  /violação/i,
  /contínuo/i,
  /métrica/i,
];

await mkdir(`${OUT}/${SLICE}`, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });

const checks = {};
const panelTexts = {};

for (const v of views) {
  const url = `${BASE}/sla-lifecycle?intent_id=${INTENT}&view=${v.view}`;
  await page.goto(url, { waitUntil: "networkidle", timeout: 120000 });
  await page.waitForTimeout(2500);
  const text = await page.locator("body").innerText();
  panelTexts[v.name] = text.slice(0, 5000);
  const ptHits = PT_PATTERNS.filter((p) => p.test(text)).map(String);
  checks[v.name] = {
    url,
    length: text.length,
    portuguese_hits: ptHits,
    serviceProfile: /Service Profile|Slice Type|Latency Requirement/.test(text),
    telemetry: /Multidomain Telemetry|PRB|Bandwidth|Observed/.test(text),
    compliance: /Compliance Evaluation|Compliance Score|Observed Value/.test(text),
    decision: /Decision Evidence|decision_score|prb_utilization|Threshold/.test(text),
    assurance: /Runtime Assurance|recommendation|bottleneck|violations/i.test(text),
    governance: /Governance|tx_hash|block_number|COMMITTED|On-chain/i.test(text),
    packetLoss: /packet loss|Packet Loss|packet_loss/i.test(text),
    reliability: /reliability|Reliability/i.test(text),
    availability: /availability|Availability/i.test(text),
    prbLabel: /PRB Utilization/i.test(text),
  };
  await page.screenshot({ path: `${OUT}/${SLICE}/${v.name}.png`, fullPage: true });
}

// V8 separation: compare panel headings across views
const tel = panelTexts["03_observed_telemetry"] || "";
const comp = panelTexts["04_compliance_evaluation"] || "";
const dec = panelTexts["05_decision_evidence"] || "";
const ass = panelTexts["06_runtime_assurance"] || "";
checks.separation = {
  telemetry_has_compliance_score: /Compliance Score/.test(tel),
  compliance_has_raw_telemetry_heading: /Multidomain Telemetry/.test(comp),
  decision_has_domain_explainability: /Domain Explainability|Compliance Evaluation/.test(dec),
  assurance_has_kpi_cards: /Observed Value[\s\S]*Requirement[\s\S]*Compliance Score/.test(ass),
  assurance_has_compliance_panel: /Compliance Evaluation/.test(ass),
};

await writeFile(`${OUT}/${SLICE}/ui_checks.json`, JSON.stringify({ slice: SLICE, intent: INTENT, checks }, null, 2));
await browser.close();
console.log(`OK ${SLICE}`, checks.separation);
