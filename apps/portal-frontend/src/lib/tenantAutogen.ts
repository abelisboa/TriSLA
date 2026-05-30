/**
 * Auto-generated trace tenant IDs (Sprint 4E).
 * Format: trisla-{8 hex} — opaque metadata label, not operator-facing.
 */

const FORBIDDEN_TENANT_VALUES = new Set([
  "",
  "default",
  "tenant-demo-001",
  "tenant-001",
]);

/** Generates `trisla-xxxxxxxx` using 8 hex chars from crypto UUID. */
export function generateTrislaTenantId(): string {
  const hex = crypto.randomUUID().replace(/-/g, "").slice(0, 8).toLowerCase();
  const id = `trisla-${hex}`;
  if (FORBIDDEN_TENANT_VALUES.has(id)) {
    return generateTrislaTenantId();
  }
  return id;
}

export function isTrislaAutogenTenantId(value: string | null | undefined): boolean {
  if (!value || typeof value !== "string") return false;
  return /^trisla-[0-9a-f]{8}$/.test(value.trim());
}
