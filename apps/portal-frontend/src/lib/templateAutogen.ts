/**
 * SSOT slice → template_id map (Sprint 4G).
 * Aligned with REAL_PAYLOAD_FREEZE and Stress Campaign V2
 * (`docs/scripts/multidomain_stress_campaign_v2.py`).
 */

export class UnknownSliceTypeError extends Error {
  constructor(sliceType: string) {
    super(`Unknown slice type for template resolution: "${sliceType}"`);
    this.name = "UnknownSliceTypeError";
  }
}

const SLICE_TEMPLATE_SSOT: Record<string, string> = {
  URLLC: "urllc-template-001",
  EMBB: "embb-template-001",
  MMTC: "mmtc-template-001",
};

const SLICE_PROFILE_LABELS: Record<string, string> = {
  URLLC: "URLLC Standard Profile",
  EMBB: "Enhanced Mobile Broadband Profile",
  MMTC: "Massive IoT Profile",
};

/** Normalizes slice/service type strings to SSOT keys. */
export function normalizeSliceType(sliceType: string | null | undefined): string {
  const raw = String(sliceType ?? "").trim().toUpperCase();
  if (raw === "EMBB") return "EMBB";
  if (raw === "URLLC") return "URLLC";
  if (raw === "MMTC") return "MMTC";
  return raw;
}

/**
 * Resolves template_id from slice_type. Throws if slice is unknown — no silent fallback.
 */
export function resolveTemplateId(sliceType: string | null | undefined): string {
  const key = normalizeSliceType(sliceType);
  const templateId = SLICE_TEMPLATE_SSOT[key];
  if (!templateId) {
    throw new UnknownSliceTypeError(String(sliceType ?? ""));
  }
  return templateId;
}

/** Operator-facing profile label (display only). */
export function slaProfileLabel(sliceType: string | null | undefined): string {
  const key = normalizeSliceType(sliceType);
  return SLICE_PROFILE_LABELS[key] ?? "Unknown SLA Profile";
}

export function isKnownSliceType(sliceType: string | null | undefined): boolean {
  const key = normalizeSliceType(sliceType);
  return key in SLICE_TEMPLATE_SSOT;
}
