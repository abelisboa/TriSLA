# NSSF Adapter (O1C) Rollback Plan

**Phase:** E2E-O1C  
**Timestamp UTC:** 2026-06-06

## Quick disable

```bash
kubectl -n trisla set env deployment/trisla-nasp-adapter NSSF_ADAPTER_ENABLED=false
kubectl -n trisla rollout status deployment/trisla-nasp-adapter
```

NSI creation continues with O6 `METADATA_ONLY` only.

## Full rollback

1. Revert NASP adapter digest to pre-O1C image
2. `kubectl -n trisla rollout status deployment/trisla-nasp-adapter`

## Files introduced O1C

- `apps/nasp-adapter/src/nssf_adapter.py`
- `apps/nasp-adapter/config/nssf_adapter_ssot.yaml`
- `apps/nasp-adapter/tests/test_nssf_adapter.py`

## CR impact

NSIs with `trisla.io/nssf-selection` annotation remain valid metadata; no NF side-effects to undo.
