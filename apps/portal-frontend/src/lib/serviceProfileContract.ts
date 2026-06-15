/**
 * RC-P20-01 — SLA Contract (Service Profile) display helpers.
 * Requirements only — no telemetry. Source: SEM-CSMF via interpret/submit/status.
 */

export const SERVICE_PROFILE_SOURCE = "SEM-CSMF";

export type ServiceProfileContractRow = {
  label: string;
  value: unknown;
};

export function asSlaRequirementsRecord(
  value: unknown,
): Record<string, unknown> | undefined {
  if (!value || typeof value !== "object") return undefined;
  return value as Record<string, unknown>;
}

/** Build ordered SLA requirement rows for Service Profile panel. */
export function serviceProfileContractFields(
  sla: Record<string, unknown> | undefined,
  serviceType?: unknown,
): ServiceProfileContractRow[] {
  const sliceType =
    sla?.slice_type ?? sla?.type ?? sla?.sla_type ?? serviceType;
  return [
    { label: "Slice Type", value: sliceType },
    { label: "Template", value: sla?.template_id },
    { label: "Latency Requirement", value: sla?.latency ?? sla?.latency_ms },
    { label: "Throughput Requirement", value: sla?.throughput ?? sla?.throughput_mbps },
    { label: "Reliability Requirement", value: sla?.reliability ?? sla?.reliability_pct },
    {
      label: "Availability Requirement",
      value: sla?.availability ?? sla?.availability_pct ?? sla?.availability_percent,
    },
    { label: "Jitter Requirement", value: sla?.jitter ?? sla?.jitter_ms },
    { label: "Coverage Requirement", value: sla?.coverage ?? sla?.area_cobertura },
    {
      label: "Device Density Requirement",
      value: sla?.device_density ?? sla?.numero_dispositivos,
    },
  ];
}
