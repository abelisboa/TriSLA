import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import { writeFile } from "node:fs/promises";

const BASE = process.env.TRISLA_FRONTEND_URL || "http://192.168.10.15:32561";
const OUT = process.argv[2];
const INTENT = process.argv[3] || "2dff6e79-fd0c-4ee6-a0f8-2f7a246bb488";

await mkdir(`${OUT}`, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const url = `${BASE}/sla-lifecycle?intent_id=${INTENT}&view=admission`;

await page.goto(url, { waitUntil: "networkidle", timeout: 120000 });
await page.waitForTimeout(5000);

const bodyText = await page.locator("body").innerText();
const checks = {
  onChainCommit: /On-chain commit/i.test(bodyText),
  committed: /✓ Committed|Committed on-chain/.test(bodyText),
  registered: /Registered/.test(bodyText),
  confirmed: /Confirmed/.test(bodyText),
  shortHash: /0x[0-9a-f]{6,10}…/i.test(bodyText),
  blockNumber: /5139272/.test(bodyText),
  blockchainEvidence: /Blockchain evidence|On-chain evidence/i.test(bodyText),
};

await page.screenshot({ path: `${OUT}/01_lifecycle_blockchain_card.png`, fullPage: true });

const evidence = page.locator("details").filter({ hasText: /On-chain evidence|Blockchain evidence/i }).first();
if (await evidence.count()) {
  await evidence.click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${OUT}/02_onchain_evidence_expanded.png`, fullPage: true });
}

await writeFile(`${OUT}/ui_text_checks.json`, JSON.stringify({ url, checks, sample: bodyText.slice(0, 4000) }, null, 2));
await browser.close();

const allPass = Object.values(checks).every(Boolean);
if (!allPass) {
  console.error("UI checks failed:", checks);
  process.exit(1);
}
console.log("UI checks OK:", checks);
