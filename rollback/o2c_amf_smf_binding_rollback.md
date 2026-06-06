# O2C AMF/SMF Binding Rollback Plan

**Phase:** E2E-O2C  
**Timestamp UTC:** 2026-06-06

## Quick disable

```bash
kubectl -n trisla set env deployment/trisla-nasp-adapter \
  AMF_BINDING_ENABLED=false SMF_BINDING_ENABLED=false
kubectl -n trisla rollout status deployment/trisla-nasp-adapter
```

NSI creation continues with O1C `NSSF_SELECTED` only.

## Full rollback

1. Revert NASP adapter digest to pre-O2C image (O1C freeze digest `581bce2b...`)
2. `kubectl -n trisla rollout status deployment/trisla-nasp-adapter`

## Files introduced O2C

- `apps/nasp-adapter/src/amf_binding_adapter.py`
- `apps/nasp-adapter/src/smf_binding_adapter.py`
- `apps/nasp-adapter/src/amf_smf_correlation.py`
- `apps/nasp-adapter/config/amf_smf_binding_ssot.yaml`
- `apps/nasp-adapter/tests/test_amf_smf_binding.py`

## CR impact

NSIs with `trisla.io/amf-binding`, `trisla.io/smf-binding`, `trisla.io/pdu-session-summary` remain valid metadata; no NF side-effects to undo.
