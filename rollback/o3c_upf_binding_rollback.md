# O3C UPF Binding Rollback Plan

**Phase:** E2E-O3C  
**Timestamp UTC:** 2026-06-06

## Quick disable

```bash
kubectl -n trisla set env deployment/trisla-nasp-adapter \
  UPF_BINDING_ENABLED=false
kubectl -n trisla rollout status deployment/trisla-nasp-adapter
```

NSI creation continues with O2C `PDU_CORRELATED` only.

## Full rollback

1. Revert NASP adapter digest to pre-O3C image (`7948f1945...` O2C freeze)
2. `kubectl -n trisla rollout status deployment/trisla-nasp-adapter`

## Files introduced O3C

- `apps/nasp-adapter/src/upf_binding_adapter.py`
- `apps/nasp-adapter/src/upf_correlation.py`
- `apps/nasp-adapter/config/upf_binding_ssot.yaml`
- `apps/nasp-adapter/tests/test_upf_binding.py`

## CR impact

NSIs with `trisla.io/upf-binding` remain valid metadata; no UPF/PFCP side-effects to undo.
