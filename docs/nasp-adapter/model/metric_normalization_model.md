# NASP Adapter SLA Normalization

The NASP Adapter normalizes the SLA portion of a Network Slice Instance request before sending it to the Kubernetes controller.

## Identifier normalization

- `nsiId`, `nsi_id`, and `intent_id` are accepted as NSI identifier sources.
- `serviceProfile`, `service_profile`, and `service_type` are accepted as service profile sources.
- `tenantId` and `tenant_id` are accepted as tenant sources.
- `nestId` and `nest_id` are accepted as NEST identifier sources.
- Generated resource names are converted to lowercase RFC 1123 names.

## Slice selection

The `nssai` object retains `sst` and optional `sd`. When `sst` is absent, the adapter uses `1`.

## SLA fields

The normalizer accepts common names for latency, throughput, reliability, availability, jitter, packet loss, and device density. Values are converted to the form expected by the Network Slice Instance resource when conversion is possible. Unsupported or empty values are omitted.

## Defaults

| Field | Default |
|---|---|
| `serviceProfile` | `eMBB` |
| `tenantId` | `default` |
| `nssai.sst` | `1` |
| `nsiId` | generated `nsi-` identifier |

The implemented normalization helpers are in [`main.py`](../../../apps/nasp-adapter/src/main.py).
