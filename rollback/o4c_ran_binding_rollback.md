# O4C RAN Binding Rollback Plan

**Phase:** E2E-O4C  
**Timestamp UTC:** 2026-06-06

## Quick disable

```bash
kubectl -n trisla set env deployment/trisla-nasp-adapter \
  RAN_BINDING_ENABLED=false
kubectl -n trisla rollout status deployment/trisla-nasp-adapter
```

NSI creation continues with O3C `USER_PLANE_CORRELATED` only.

## Full rollback

1. Revert NASP adapter digest to pre-O4C image (O3C freeze `d581fd71...`)
2. `kubectl -n trisla rollout status deployment/trisla-nasp-adapter`

## Files introduced O4C

- `apps/nasp-adapter/src/ran_binding_adapter.py`
- `apps/nasp-adapter/src/ran_correlation.py`
- `apps/nasp-adapter/config/ran_binding_ssot.yaml`
- `apps/nasp-adapter/tests/test_ran_binding.py`

## CR impact

NSIs with `trisla.io/ran-binding` remain valid metadata; no RAN/NGAP side-effects to undo.
