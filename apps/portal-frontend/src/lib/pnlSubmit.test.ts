/**
 * P2 — PNL sla_requirements full propagation.
 * Run: npx tsx src/lib/pnlSubmit.test.ts
 */

import {
  buildFormValuesFromInterpret,
  buildSubmitPayloadFromInterpret,
  type InterpretResponse,
} from "./pnlSubmit";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

function assertEquivalentSlaTransport(
  sla: Record<string, unknown>,
  formValues: Record<string, unknown>,
) {
  for (const [key, value] of Object.entries(sla)) {
    if (value === null || value === undefined || value === "") continue;
    assert(formValues[key] === value, `field lost or changed: ${key}`);
  }
}

const URLLC_FULL: InterpretResponse = {
  tenant_id: "tenant-p2",
  slice_type: "URLLC",
  service_type: "URLLC",
  sla_requirements: {
    latency: "1ms",
    throughput: "10Mbps",
    reliability: 0.99999,
    availability: "99.999%",
    jitter: "0.5ms",
    coverage: "factory-floor",
    device_density: 50,
    original_text: "URLLC industrial telemetry",
    service_profile: "urllc-industrial",
  },
};

const EMBB_FULL: InterpretResponse = {
  tenant_id: "tenant-p2",
  slice_type: "eMBB",
  sla_requirements: {
    latency: "20ms",
    throughput: "500Mbps",
    reliability: 0.999,
    availability: "99.9%",
    jitter: "2ms",
    coverage: "urban",
    device_density: 1000,
    original_text: "eMBB video streaming",
    service_profile: "embb-video",
  },
};

const MMTC_FULL: InterpretResponse = {
  tenant_id: "tenant-p2",
  slice_type: "mMTC",
  sla_requirements: {
    latency: "100ms",
    throughput: "1Mbps",
    reliability: 0.95,
    availability: "95%",
    jitter: "10ms",
    coverage: "rural",
    device_density: 10000,
    original_text: "mMTC sensor network",
    service_profile: "mmtc-sensors",
  },
};

// T1 — URLLC completo
{
  const form = buildFormValuesFromInterpret(URLLC_FULL);
  assertEquivalentSlaTransport(URLLC_FULL.sla_requirements!, form);
  assert(form.type === "URLLC", "T1 type");
  assert(form.slice_type === "URLLC", "T1 slice_type");
  const submit = buildSubmitPayloadFromInterpret(URLLC_FULL, "tpl-urllc");
  assert(submit !== null, "T1 submit payload");
  assertEquivalentSlaTransport(URLLC_FULL.sla_requirements!, submit!.form_values);
}

// T2 — eMBB completo
{
  const form = buildFormValuesFromInterpret(EMBB_FULL);
  assertEquivalentSlaTransport(EMBB_FULL.sla_requirements!, form);
  const submit = buildSubmitPayloadFromInterpret(EMBB_FULL, "tpl-embb");
  assert(submit !== null, "T2 submit");
  assertEquivalentSlaTransport(EMBB_FULL.sla_requirements!, submit!.form_values);
}

// T3 — mMTC completo
{
  const form = buildFormValuesFromInterpret(MMTC_FULL);
  assertEquivalentSlaTransport(MMTC_FULL.sla_requirements!, form);
}

// T4 — availability, jitter, coverage, device_density reach backend
{
  const interpret: InterpretResponse = {
    tenant_id: "tenant-p2",
    slice_type: "URLLC",
    sla_requirements: {
      latency: "1ms",
      throughput: "100Mbps",
      availability: "99.999%",
      jitter: "5ms",
      coverage: "campus",
      device_density: 200,
    },
  };
  const submit = buildSubmitPayloadFromInterpret(interpret, "tpl-t4");
  assert(submit !== null, "T4 submit");
  const fv = submit!.form_values;
  assert(fv.availability === "99.999%", "T4 availability");
  assert(fv.jitter === "5ms", "T4 jitter");
  assert(fv.coverage === "campus", "T4 coverage");
  assert(fv.device_density === 200, "T4 device_density");
}

// T5 — extra fields preserved
{
  const interpret: InterpretResponse = {
    tenant_id: "tenant-p2",
    slice_type: "URLLC",
    sla_requirements: {
      latency: "1ms",
      custom_kpi_alpha: "value-alpha",
      custom_kpi_beta: 42,
      nested_hint: { region: "south" },
    },
  };
  const form = buildFormValuesFromInterpret(interpret);
  assert(form.custom_kpi_alpha === "value-alpha", "T5 custom alpha");
  assert(form.custom_kpi_beta === 42, "T5 custom beta");
  assert(
    (form.nested_hint as { region: string }).region === "south",
    "T5 nested",
  );
}

// T6 — 100% equivalence before/after PNL bridge
{
  const slaBefore = {
    latency: "1ms",
    throughput: "100Mbps",
    reliability: 0.99999,
    availability: "99.999%",
    jitter: "5ms",
    coverage: "wide",
    device_density: 10,
    original_text: "full equivalence test",
    service_profile: "profile-x",
    extra_field: "keep-me",
  };
  const interpret: InterpretResponse = {
    tenant_id: "tenant-p2",
    slice_type: "URLLC",
    sla_requirements: slaBefore,
  };
  const formAfter = buildFormValuesFromInterpret(interpret);
  for (const [key, value] of Object.entries(slaBefore)) {
    assert(formAfter[key] === value, `T6 equivalence failed: ${key}`);
  }
}

// REAL_PAYLOAD_FREEZE regression — original_text preserved
{
  const freeze = {
    tenant_id: "real_payload_freeze_v1",
    slice_type: "URLLC",
    service_type: "URLLC",
    sla_requirements: {
      latency: "5ms",
      reliability: 0.9999899999999999,
      original_text:
        "Preciso de um slice URLLC para telemetria industrial com latencia maxima de 5 ms, confiabilidade 99.999% e baixo throughput.",
    },
  } satisfies InterpretResponse;
  const form = buildFormValuesFromInterpret(freeze);
  assert(form.latency === "5ms", "freeze latency");
  assert(form.original_text === freeze.sla_requirements!.original_text, "freeze original_text");
}

console.log("pnlSubmit.test.ts: OK (T1–T6 + freeze regression)");
