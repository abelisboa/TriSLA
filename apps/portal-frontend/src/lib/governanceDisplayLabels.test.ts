/**
 * Sprint 10G.2 — run: npx tsx src/lib/governanceDisplayLabels.test.ts
 */
import {
  displayClarityBlockchainStatus,
  displayClarityReason,
  displayLocalGovernanceRegistration,
  displayOnChainCommitStatus,
} from "./governanceDisplayLabels";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

assert(
  displayClarityBlockchainStatus("Pending or failed", false) === "Not committed on-chain",
  "pending maps",
);
assert(displayClarityReason("ACCEPT without on-chain commit").includes("degraded"), "reason maps");
assert(displayLocalGovernanceRegistration("REGISTERED") === "Lineage ID assigned", "local reg");
assert(displayOnChainCommitStatus("COMMITTED") === "Committed on-chain", "on-chain committed");
assert(
  displayOnChainCommitStatus("REGISTERED") === "REGISTERED",
  "REGISTERED not aliased as on-chain in displayOnChainCommitStatus",
);

console.log("governanceDisplayLabels.test.ts: OK");
