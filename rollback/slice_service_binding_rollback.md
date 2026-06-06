# Slice Service Binding (O6) Rollback Plan

**Phase:** O6 — Slice Service Binding SSOT  
**Timestamp UTC:** 2026-06-06

---

## Quick disable (no redeploy)

```bash
kubectl -n trisla set env deployment/trisla-nasp-adapter SLICE_SERVICE_BINDING_ENABLED=false
kubectl -n trisla rollout status deployment/trisla-nasp-adapter
```

Legacy env (fallback in code): `E2E_5G_MAPPING_ENABLED=false`

---

## Full rollback (revert digest)

1. Restore previous NASP adapter digest in Helm values
2. `helm upgrade trisla helm/trisla -n trisla`
3. Confirm rollout: `kubectl -n trisla rollout status deployment/trisla-nasp-adapter`

---

## Git revert

```bash
git revert <commit-ssb-r1>   # ou checkout branch main aprovada
```

Affected files:

- `apps/nasp-adapter/src/slice_service_binding.py`
- `apps/nasp-adapter/config/slice_service_binding_ssot.json`
- `apps/nasp-adapter/src/main.py` (API paths)
- `apps/nasp-adapter/src/controllers/nsi_controller.py`
- `helm/trisla/values.yaml` (`sliceServiceBinding`)

---

## CR cleanup (optional)

NSIs created with `trisla.io/slice-service-binding` annotation remain valid metadata-only.
No NF side-effects to undo.

---

## Verdict after rollback

```
SLICE_SERVICE_BINDING_APPROVED = NO (reverted)
```
