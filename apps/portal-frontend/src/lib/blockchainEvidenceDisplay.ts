/**
 * Sprint 10G.8 — Blockchain evidence display helpers (frontend only).
 */

export const BESU_NETWORK_LABEL = "Hyperledger Besu";

export type OnChainEvidenceFields = {
  bc_status?: string | null;
  tx_hash?: string | null;
  block_number?: number | string | null;
  network?: string | null;
};

export function formatShortTxHash(hash: string | null | undefined, visibleChars = 10): string {
  if (!hash) return "";
  const h = String(hash).trim();
  if (!h) return "";
  if (h.length <= visibleChars + 1) return h;
  return `${h.slice(0, visibleChars)}…`;
}

export function hasOnChainEvidence(fields: OnChainEvidenceFields): boolean {
  return Boolean(
    fields.bc_status ||
      fields.tx_hash ||
      (fields.block_number !== null && fields.block_number !== undefined && fields.block_number !== ""),
  );
}

export function isBcStatusCommitted(bcStatus: string | null | undefined): boolean {
  const key = String(bcStatus ?? "").trim().toUpperCase();
  return key === "COMMITTED" || key === "CONFIRMED" || key === "BLOCKCHAIN_COMMITTED";
}

export function formatBlockNumberDisplay(blockNumber: number | string | null | undefined): string {
  if (blockNumber === null || blockNumber === undefined || blockNumber === "") return "";
  return String(blockNumber);
}
