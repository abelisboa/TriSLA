# O5C Transport Binding Rollback Plan

**Phase:** E2E-O5C  
**Timestamp UTC:** 2026-06-06

## Quick disable

```bash
kubectl -n trisla set env deployment/trisla-nasp-adapter \
  TRANSPORT_BINDING_ENABLED=false
kubectl -n trisla rollout status deployment/trisla-nasp-adapter
```

NSI creation continues with O4C `ACCESS_CORRELATED` only.

## Full rollback

1. Revert NASP adapter digest to O4C freeze `sha256:a7e7d562baae88ae1010caf6d5e53fa18db15ee788bc746d07965219cecc7785`
2. `kubectl -n trisla rollout status deployment/trisla-nasp-adapter`

## Files introduced O5C

- `apps/nasp-adapter/src/transport_binding_adapter.py`
- `apps/nasp-adapter/src/transport_correlation.py`
- `apps/nasp-adapter/config/transport_binding_ssot.yaml`
- `apps/nasp-adapter/tests/test_transport_binding.py`

## CR impact

NSIs with `trisla.io/transport-binding` remain valid metadata; no ONOS/southbound side-effects to undo.

## ONOS safety

O5C performs **GET-only** REST calls. No flows, intents, or topology mutations.
