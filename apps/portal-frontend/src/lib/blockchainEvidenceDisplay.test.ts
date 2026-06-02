/**
 * Sprint 10G.8 — run: npx tsx src/lib/blockchainEvidenceDisplay.test.ts
 */
import {
  formatBlockNumberDisplay,
  formatShortTxHash,
  hasOnChainEvidence,
  isBcStatusCommitted,
} from "./blockchainEvidenceDisplay";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

const full = "0x41bed3b3c8f2a1e09d4f5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6";
assert(formatShortTxHash(full) === "0x41bed3b3…", "short hash prefix");
assert(formatShortTxHash("0xabc") === "0xabc", "short hash no truncate");
assert(isBcStatusCommitted("COMMITTED"), "committed");
assert(!isBcStatusCommitted("REGISTERED"), "registered not committed");
assert(formatBlockNumberDisplay(5139272) === "5139272", "block number");
assert(hasOnChainEvidence({ tx_hash: full }), "has evidence tx");
assert(!hasOnChainEvidence({}), "empty evidence");

console.log("blockchainEvidenceDisplay.test.ts: OK");
