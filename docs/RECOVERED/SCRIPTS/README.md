# Scripts — executable index

All paths are **relative to repository root** `trisla/`. These scripts are retained for **audit, validation, enrichment, or local tooling**; they are **not** a substitute for the in-cluster E2E path unless documented.

## `docs/scripts/` (cross-cutting / campaigns)

| Script | Role | Cleanup |
|--------|------|---------|
| `docs/scripts/run_fase2_enrichment_with_paths.py` | Wrapper: runs `fase2_transport_enrichment_v2` from known paths | LINK_ARCHIVED - source not present in current tree |
| [../../scripts/fase2_transport_enrichment_v2.py](../../scripts/fase2_transport_enrichment_v2.py) | Transport enrichment (Fase 2) | LINK_FIXED |
| `docs/scripts/fase2_generate_ieee_figures.py` | IEEE figure generation | LINK_ARCHIVED - source not present in current tree |
| `docs/scripts/fase2_generate_ieee_figures_curated.py` | Curated IEEE figures | LINK_ARCHIVED - source not present in current tree |
| `docs/scripts/prompt230_contrast_campaign.py` | Contrast campaign (Python) | LINK_ARCHIVED - source not present in current tree |
| `docs/scripts/prompt230_contrast_campaign.sh` | Contrast campaign (shell) | LINK_ARCHIVED - source not present in current tree |
| `docs/scripts/prompt230_postprocess.sh` | Post-process step for campaign | LINK_ARCHIVED - source not present in current tree |

## `apps/portal-backend/scripts/`

| Script | Role |
|--------|------|
| [../../../apps/portal-backend/scripts/validate_portal_nasp.py](../../../apps/portal-backend/scripts/validate_portal_nasp.py) | Multi-phase portal ↔ NASP validation |
| [../../../apps/portal-backend/scripts/validar_rotas.sh](../../../apps/portal-backend/scripts/validar_rotas.sh) | Route checks |
| [../../../apps/portal-backend/scripts/validar_instalacao.sh](../../../apps/portal-backend/scripts/validar_instalacao.sh) | Installation validation |
| [../../../apps/portal-backend/scripts/rebuild_venv.sh](../../../apps/portal-backend/scripts/rebuild_venv.sh) | Local venv rebuild |
| [../../../apps/portal-backend/scripts/fix_line_endings.sh](../../../apps/portal-backend/scripts/fix_line_endings.sh) | Line endings (maintenance) |
| [../../../apps/portal-backend/scripts/audit_portal_backend_imports.sh](../../../apps/portal-backend/scripts/audit_portal_backend_imports.sh) | Import audit |
| [../../../apps/portal-backend/scripts/fix_all_line_endings.py](../../../apps/portal-backend/scripts/fix_all_line_endings.py) | Line endings (Python) |

## `apps/portal-frontend/scripts/` (figures / datasets / pipelines)

| Script | Role |
|--------|------|
| [../../../apps/portal-frontend/scripts/execute_prompt5_pipeline.py](../../../apps/portal-frontend/scripts/execute_prompt5_pipeline.py) | Prompt5 pipeline |
| [../../../apps/portal-frontend/scripts/execute_prompt_v21_pipeline.py](../../../apps/portal-frontend/scripts/execute_prompt_v21_pipeline.py) | Prompt v21 pipeline |
| [../../../apps/portal-frontend/scripts/generate_figures_*.py](../../../apps/portal-frontend/scripts/) | Multiple figure generators (IEEE / domain evidence) |
| [../../../apps/portal-frontend/scripts/qualify_dataset_unknown.py](../../../apps/portal-frontend/scripts/qualify_dataset_unknown.py) | Dataset qualification |
| [../../../apps/portal-frontend/scripts/fix_*.py](../../../apps/portal-frontend/scripts/) | Figure/dataset fix utilities |

Use `ls apps/portal-frontend/scripts` for the authoritative list (12+ Python utilities).

---

**Total scripts listed in tables above:** 7 (`docs/scripts`) + 7 (`portal-backend`) + **12** (`portal-frontend` glob) = **26** tracked paths (portal-frontend count from workspace listing).

**Runtime note:** some Python helpers assume **compatible NumPy/pandas** versions in the local venv; if a script fails on import, treat it as an **environment** issue, not as permission to change cluster telemetry.
