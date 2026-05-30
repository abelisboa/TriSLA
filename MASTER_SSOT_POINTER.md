# TriSLA — Master SSOT Pointer

**Purpose:** Single index of frozen evidence packs and official baselines.  
**Repository:** `/home/porvir5g/gtp5g/trisla`  
**Do not delete historical freezes.** New freezes add entries; they do not replace prior evidence trees.

---

## RESULTS_FREEZE_MAIN (primary — article Results section)

| Field | Value |
|-------|-------|
| **Role** | Official primary experimental baseline for **RESULTS AND EXPERIMENTAL EVALUATION** |
| **Freeze name** | `RESULTS_FREEZE_MAIN` |
| **Pack path** | `evidencias_multidomain_stress_campaign_v2_20260529T115740Z` |
| **Registered** | `20260529T142539Z` |
| **Manifest** | `evidencias_multidomain_stress_campaign_v2_20260529T115740Z/RESULTS_FREEZE_MAIN_MANIFEST.json` |
| **Dataset** | `…/dataset/multidomain_stress_final.csv` |
| **Dataset SHA256** | `aeb26946e0b2f81064372dfd3f743cd3492e207db0bb29c789f7983fe2c9e1f6` |
| **Executions** | 240 (8 scenarios × 3 slices × 10 reps) |
| **Figures** | R1–R12 (`…/figures/`) |
| **Freeze summary** | `…/analysis/results_freeze_summary.md` |
| **Integrity** | `…/analysis/freeze_integrity_validation.md` |
| **Scientific claim** | `…/analysis/final_scientific_claim.md` |
| **Campaign scripts** | `docs/scripts/multidomain_stress_campaign_v2.py`, `docs/scripts/multidomain_stress_v21_revalidation.py` |

**Usage:** All future *Results*, *Discussion*, and *Conclusion* sections MUST cite this pack as the primary experimental reference unless a new freeze is explicitly registered.

**Aligned manuscript (V2.1):** `evidencias_multidomain_stress_campaign_v2_20260529T115740Z/manuscript/` (`Results.tex`, `Discussion.tex`, `Conclusion.tex`); alignment audits in `…/analysis/results_alignment_audit.md`.

**Note:** Does not supersede Phase 6 runtime/math baseline below; complements it with multidomain stress experimental evidence.

---

## Runtime / mathematics baseline (historical — retained)

| Role | Path |
|------|------|
| Master SSOT document | `docs/TRISLA_MASTER_SSOT_RUNTIME_BASELINE_V1.md` |
| SSOT controlled execution | `evidencias_trisla_phase6_ssot_controlled_execution_20260517T154849Z` |
| Resource headroom runtime (DS-P6) | `evidencias_trisla_phase6_resource_headroom_runtime_20260517T150959Z` |
| Feasibility runtime | `evidencias_trisla_phase5_feasibility_runtime_20260517T150015Z` |
| Publication consolidation | `evidencias_trisla_phase4_publication_consolidation_20260517T140548Z` |
| True multidomain runtime program | `evidencias_trisla_true_multidomain_runtime_20260517T031129Z` |
| Official bibliography | `evidencias_trisla_phase6_ssot_controlled_execution_20260517T154849Z/references/references_4.bib` |

**Decision Engine digest (Phase 6):** `sha256:67659064d35a72656f1554cfbdb7a166a052d1a20a01aa5688baf201023f6be5`

---

## Supplementary Results evidence (historical — retained)

| Role | Path |
|------|------|
| Phase 6 RESULTS figures (DS-P6, n=150) | `evidencias_results_final_campaign_20260528T190802Z` |
| Multidomain stress V2 (same pack as RESULTS_FREEZE_MAIN) | `evidencias_multidomain_stress_campaign_v2_20260529T115740Z` |

---

## Operational / audit evidence (historical — retained)

| Role | Path |
|------|------|
| Light audit | `evidencias_auditoria_leve_20260509T145125Z` |
| Path audit v2 | `evidencias_auditoria_v2_20260509T145459Z` |
| Advanced audit v3 | `evidencias_auditoria_v3_20260509T150018Z` |
| Responsibility audit | `evidencias_auditoria_responsabilidades_20260511T190246Z` |
| Refactor responsibilities freeze | `evidencias_refactor_responsabilidades_20260511T191645Z` |

---

## Runbooks

| Document | Path |
|----------|------|
| Master runbook | `docs/TRISLA_MASTER_RUNBOOK.md` |
| GSMA alignment runbook | `docs/TRISLA_GSMA_ALIGNMENT_MASTER_RUNBOOK.md` |

---

## FRONTEND_OPERATIONAL_BASELINE_FINAL (official — portal frontend)

| Field | Value |
|-------|-------|
| **Role** | Official operational baseline for **TriSLA Portal Frontend** (F1–F8 consolidated + hydration fix) |
| **Baseline name** | `FRONTEND_OPERATIONAL_BASELINE_FINAL` |
| **Baseline date** | `20260529` (runtime digest updated `20260530`) |
| **Pack path** | `frontend_operational_baseline_final_20260529T193458Z/` |
| **Registered** | `20260529T193458Z` |
| **Commit (runtime)** | `1b5a762fd7eaebae4b2360054cd23fe48a164e0c` |
| **Message** | Frontend F8 hydration fix — defer Topbar timestamp to client mount |
| **Prior commit (F8 polish)** | `6395c5dd14f4a206ed5e11b10ce09a1f53d27677` |
| **Digest (runtime SSOT)** | `sha256:9f7545e408c9287509fc77c53575600a2d6e79eecf9d7093e1aea7c45f6d95d6` |
| **Image** | `ghcr.io/abelisboa/trisla-portal-frontend@sha256:9f7545e408c9287509fc77c53575600a2d6e79eecf9d7093e1aea7c45f6d95d6` |
| **Build tag** | `20260530T001028Z` |
| **Deployment** | `trisla-portal-frontend` (namespace `trisla`, container `frontend`) |
| **NodePort** | `32561` |
| **Backend NodePort** | `32002` |
| **Code root** | `apps/portal-frontend/` |
| **Hydration fix pack** | `frontend_f8_hydration_fix_20260529T235808Z/` |
| **Deploy digest pack (current)** | `frontend_f8_hydration_deploy_digest_20260530T001006Z/` |
| **Prior deploy digest (F8 polish)** | `frontend_f8_deploy_digest_20260529T192849Z/` (`b67ef185...`) |
| **Status** | DEMO READY · DISSERTATION READY · REVIEWER READY · PUBLICATION READY · **HYDRATION FIXED** |

**Phase evidence chain:** F0/F1 → F2…F8 → `frontend_f8_deploy_digest_20260529T192849Z/` → hydration audit/fix → `frontend_f8_hydration_deploy_digest_20260530T001006Z/`.

**Usage:** All frontend deploy references MUST cite digest `9f7545e408c928...` unless a new freeze is explicitly registered.

---

## SPRINT_1_BACKEND_BASELINE (official — portal backend monitoring fix)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA Portal Backend** after Sprint 1 Monitoring Stabilization |
| **Baseline name** | `SPRINT_1_BACKEND_BASELINE` |
| **Sprint** | SPRINT 1 — Monitoring Stabilization |
| **Pack path** | `sprint1_prometheus_summary_fix_20260530T005235Z/` |
| **Audit dependency** | `prometheus_summary_runtime_audit_20260530T004004Z/` |
| **Commit (runtime)** | `8d3082f15252a1cdd050ed4b2b361e11bf406e24` |
| **Message** | Fix Prometheus summary numeric normalization |
| **Prior backend digest** | `sha256:a73c667ee0bf776802359c48ef89a72261e2cd5af4380a0cb41e6b61533d34af` |
| **Digest (runtime SSOT)** | `sha256:6baba68ac09771d02917fe1c63ad0cfcdc9f8775533c6b9a975fb6c129c628ac` |
| **Image** | `ghcr.io/abelisboa/trisla-portal-backend@sha256:6baba68ac09771d02917fe1c63ad0cfcdc9f8775533c6b9a975fb6c129c628ac` |
| **Build tag** | `20260530T005317Z` |
| **Deployment** | `trisla-portal-backend` (namespace `trisla`, container `backend`) |
| **NodePort** | `32002` |
| **Fix scope** | `apps/portal-backend/src/routers/prometheus.py` — `safe_float()` before `_norm()` |
| **Status** | MONITORING STABLE · `GET /api/v1/prometheus/summary` HTTP 200 |

**Usage:** All backend deploy references MUST cite digest `6baba68ac097...` unless a new freeze is explicitly registered.

---

## SPRINT_2_BLOCKCHAIN_RECOVERY_BASELINE (official — on-chain governance)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA Blockchain / BC-NSSMF** after Sprint 2 wallet recovery |
| **Baseline name** | `SPRINT_2_BLOCKCHAIN_RECOVERY_BASELINE` |
| **Sprint** | SPRINT 2 — Blockchain Runtime Recovery |
| **Audit pack** | `sprint2_blockchain_runtime_recovery_20260530T005943Z/` |
| **Implementation pack** | `sprint2_blockchain_wallet_recovery_20260530T010431Z/` |
| **Recovery method** | Validator → BC wallet transfer (0.5 ETH); no genesis reset, no redeploy |
| **BC wallet** | `0x24f31b232A89bC9cdBc9CA36e6d161ec8f435044` |
| **Besu validator (funder)** | `0x3d86b9df7ef6a2dbce2e617acf6df08de822a86b` |
| **SLAContract** | `0x32aA9605DA54b93995F796728d6b8CEB1025af08` |
| **Funding tx** | `0xab06f60af195d6c0ffdceff4695d82b0ab1a2ab8e5eadeb6ce69d3016a795509` (block 5007102) |
| **BC wallet balance (post)** | ~0.5001567642 ETH |
| **register-sla** | HTTP 200 · COMMITTED |
| **Submit governance** | `bc_status=COMMITTED`, `governance_registration_status=REGISTERED`, tx_hash + block_number present |
| **Frontend digest (unchanged)** | `sha256:9f7545e408c9287509fc77c53575600a2d6e79eecf9d7093e1aea7c45f6d95d6` |
| **Backend digest (unchanged)** | `sha256:6baba68ac09771d02917fe1c63ad0cfcdc9f8775533c6b9a975fb6c129c628ac` |
| **Status** | BLOCKCHAIN OPERATIONAL · on-chain registration restored |

**Note:** SLA-Agent ingest failure (`SLA_AGENT_FAILED`) was resolved in Sprint 3 (`SPRINT_3_SLA_AGENT_DEPLOY_BASELINE`). Submits now reach `lifecycle_state=COMPLETED`.

**Usage:** Blockchain operational references MUST cite this baseline until superseded by explicit re-freeze.

---

## SPRINT_3_SLA_AGENT_DEPLOY_BASELINE (official — SLA-Agent layer)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA SLA-Agent Layer** after Sprint 3 digest deploy (image drift fix) |
| **Baseline name** | `SPRINT_3_SLA_AGENT_DEPLOY_BASELINE` |
| **Sprint** | SPRINT 3 — SLA-Agent Digest Deploy |
| **Audit pack** | `sprint3_sla_agent_runtime_recovery_20260530T010956Z/` |
| **Implementation pack** | `sprint3_sla_agent_digest_deploy_20260530T011919Z/` |
| **Root cause** | IMAGE DRIFT — stale runtime missing ingest/revalidate routes |
| **Prior digest** | `sha256:824b641b7ff17ba52bd93d9c0aeb6f1a4a073575ff86719bd14f67f6a80becce` |
| **Digest (runtime SSOT)** | `sha256:3dad23e25b30c6dced2f6ec8cc979da377b4cb32e6b3d67241f435bc95e966a1` |
| **Image** | `ghcr.io/abelisboa/trisla-sla-agent-layer@sha256:3dad23e25b30c6dced2f6ec8cc979da377b4cb32e6b3d67241f435bc95e966a1` |
| **Build tag** | `20260530T011920Z` |
| **Commit (build source)** | `8d3082f15252a1cdd050ed4b2b361e11bf406e24` |
| **Deployment** | `trisla-sla-agent-layer` (namespace `trisla`, container `sla-agent-layer`) |
| **Ingest endpoint** | POST `/api/v1/ingest/pipeline-event` → HTTP 200 |
| **Revalidate endpoint** | POST `/api/v1/agent/revalidate-telemetry` → HTTP 200 |
| **E2E submit** | sla_agent_status=OK, lifecycle_state=COMPLETED, failure_code=null |
| **Revalidate delegation** | `delegated_to_sla_agent=true` |
| **Frontend digest (unchanged)** | `sha256:9f7545e408c9287509fc77c53575600a2d6e79eecf9d7093e1aea7c45f6d95d6` |
| **Backend digest (unchanged)** | `sha256:6baba68ac09771d02917fe1c63ad0cfcdc9f8775533c6b9a975fb6c129c628ac` |
| **Status** | SLA-AGENT HTTP PATH OPERATIONAL · Kafka broker reachable via Service (Sprint 3B) |

**Note:** HTTP pipeline ingest complements Kafka event bus. Kafka Service restored in Sprint 3B.

**Usage:** SLA-Agent deploy references MUST cite digest `3dad23e25b30...` unless a new freeze is explicitly registered.

---

## SPRINT_3B_KAFKA_SERVICE_BASELINE (official — Kafka event bus infrastructure)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA Kafka Service** after Sprint 3B recovery |
| **Baseline name** | `SPRINT_3B_KAFKA_SERVICE_BASELINE` |
| **Sprint** | SPRINT 3B — Kafka Service Recovery |
| **Audit pack** | `sprint3b_kafka_service_recovery_20260530T012501Z/` |
| **Implementation pack** | `sprint3b_kafka_service_implementation_20260530T012856Z/` |
| **Root cause** | ClusterIP Service `kafka` missing (Helm deployment-only gap) |
| **Fix applied** | `kubectl apply` Service `kafka` selector `app: kafka`, port 9092 |
| **Service Cluster IP** | `10.233.14.87` |
| **Endpoints** | `10.233.75.34:9092` (pod `kafka-6bd4bcdc7b-rdgsm`) |
| **DNS** | `kafka.trisla.svc.cluster.local:9092` → resolves |
| **Kafka image (unchanged)** | `ghcr.io/abelisboa/trisla-kafka@sha256:8291bed273105a3fc88df5f89096abf6a654dc92b0937245dcef85011f3fc5e6` |
| **SLA-Agent digest (unchanged)** | `sha256:3dad23e25b30c6dced2f6ec8cc979da377b4cb32e6b3d67241f435bc95e966a1` |
| **SLA-Agent post-restart** | No `modo offline`; bootstrap CONNECTED |
| **E2E submit post-fix** | COMPLETED, no regression |
| **Topics** | Empty at baseline — Sprint 3C optional validation |
| **Status** | KAFKA INFRASTRUCTURE OPERATIONAL · event topics pending 3C |

**Note:** Service applied out-of-band; add `helm/trisla/templates/service-kafka.yaml` before next `helm upgrade` to prevent drift.

**Usage:** Kafka connectivity references MUST cite Service `kafka` ClusterIP baseline until superseded.

---

## SPRINT_3D_EVENT_DRIVEN_BASELINE (official — Kafka topics + DE config)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA Kafka event-driven recovery** after Sprint 3D (topics + DE Kafka enable) |
| **Baseline name** | `SPRINT_3D_EVENT_DRIVEN_BASELINE` |
| **Sprint** | SPRINT 3D — Kafka Topic Recovery Implementation |
| **Audit dependency** | `sprint3c_kafka_topic_validation_20260530T013839Z/` |
| **Implementation pack** | `sprint3d_kafka_topic_recovery_20260530T014456Z/` |
| **Topics created** | `trisla-i05-actions`, `trisla-decision-events`, `trisla-remediation-events` (partitions=1, RF=1) |
| **DE config change** | `KAFKA_ENABLED=true`, `KAFKA_BROKERS=kafka.trisla.svc.cluster.local:9092`, `USE_KAFKA_RETRY=true` |
| **DE rollout** | `trisla-decision-engine` only — no image rebuild |
| **DE health post-change** | `kafka: enabled` |
| **DE image (unchanged)** | `ghcr.io/abelisboa/trisla-decision-engine@sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6` |
| **Submit E2E post-change** | URLLC/eMBB/mMTC → COMPLETED, no regression |
| **Kafka traffic on submit** | **Not active** — evaluate path lacks publish wiring (`service.py`) |
| **SLA-Agent consumer loop** | **Not started** — `start_consuming_loop()` not hooked in `main.py` |
| **Manual infra probes** | Producer/consumer libraries + topics verified via probe messages |
| **Verdict** | `SPRINT_3D_KAFKA_TOPIC_RECOVERY_IMPLEMENTATION_PARTIAL` |
| **Status** | KAFKA TOPICS + DE CONFIG READY · submit-path event-driven pending code wiring |

**Note:** HTTP admission path remains primary. Full async DE→Kafka→SLA-Agent requires minimal code changes in Decision Engine `service.py` and SLA-Agent startup (blocked in Sprint 3D scope).

**Usage:** Kafka topic and DE env references MUST cite this baseline until superseded by code-wiring sprint or Sprint 4 hardening.

---

## SPRINT_4A_FRONTEND_CONTRACT_ALIGNMENT_BASELINE (official — portal frontend contracts)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA Portal Frontend** after Sprint 4A contract alignment |
| **Baseline name** | `SPRINT_4A_FRONTEND_CONTRACT_ALIGNMENT_BASELINE` |
| **Sprint** | SPRINT 4A — Frontend Contract Alignment |
| **Audit dependency** | `sprint4_frontend_functional_acceptance_20260530T021611Z/` |
| **Implementation pack** | `sprint4a_frontend_contract_alignment_20260530T023042Z/` |
| **Commit (runtime)** | `8569aca08105a3ed177a3ea97c53fd0b457ee13a` |
| **Message** | Align frontend contracts with runtime payloads |
| **Prior frontend digest** | `sha256:9f7545e408c9287509fc77c53575600a2d6e79eecf9d7093e1aea7c45f6d95d6` |
| **Digest (runtime SSOT)** | `sha256:9050c1cf791407e2217369b0abb1541aad89b8aa5997cae9282f06b65157f62e` |
| **Image** | `ghcr.io/abelisboa/trisla-portal-frontend@sha256:9050c1cf791407e2217369b0abb1541aad89b8aa5997cae9282f06b65157f62e` |
| **Build tag** | `20260530T023042Z` |
| **Deployment** | `trisla-portal-frontend` (namespace `trisla`, container `frontend`) |
| **NodePort** | `32561` |
| **Fix scope** | Monitoring v2 summary mapping; template decimal reliability; administration honest labels |
| **Backend digest (unchanged)** | `sha256:6baba68ac09771d02917fe1c63ad0cfcdc9f8775533c6b9a975fb6c129c628ac` |
| **SLA-Agent digest (unchanged)** | `sha256:3dad23e25b30c6dced2f6ec8cc979da377b4cb32e6b3d67241f435bc95e966a1` |
| **Status** | FRONTEND CONTRACT ALIGNED · MONITORING V2 RENDERING · TEMPLATE DECIMAL OK |

**Usage:** All frontend deploy references MUST cite digest `9050c1cf7914...` unless a new freeze is explicitly registered. Supersedes `FRONTEND_OPERATIONAL_BASELINE_FINAL` digest for runtime references.

---

## SPRINT_4C_PRODUCT_UX_HARDENING_BASELINE (official — portal product UX)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA Portal Frontend** after Sprint 4C product UX hardening |
| **Baseline name** | `SPRINT_4C_PRODUCT_UX_HARDENING_BASELINE` |
| **Sprint** | SPRINT 4C — Product UX Hardening |
| **Audit dependency** | `sprint4b_pre_hardening_ux_audit_20260530T030000Z/` |
| **Implementation pack** | `sprint4c_product_ux_hardening_20260530T030202Z/` |
| **Commit (runtime)** | `3c166dc156edbcc8d3d3b2ee74ef6f5b0ae0eb14` |
| **Message** | Product UX hardening for operational portal |
| **Prior frontend digest** | `sha256:9050c1cf791407e2217369b0abb1541aad89b8aa5997cae9282f06b65157f62e` |
| **Digest (runtime SSOT)** | `sha256:be50ab59ec98705255d18724871fd1e8ad695c754aa0cdc8562e955b47eb7872` |
| **Image** | `ghcr.io/abelisboa/trisla-portal-frontend@sha256:be50ab59ec98705255d18724871fd1e8ad695c754aa0cdc8562e955b47eb7872` |
| **Build tag** | `20260530T030541Z` |
| **Deployment** | `trisla-portal-frontend` (namespace `trisla`, container `frontend`) |
| **NodePort** | `32561` |
| **Fix scope** | Operational branding; demo/reviewer language removal; technical details collapse; platform services labels; tenant help text; stub softening |
| **Backend digest (unchanged)** | `sha256:6baba68ac09771d02917fe1c63ad0cfcdc9f8775533c6b9a975fb6c129c628ac` |
| **SLA-Agent digest (unchanged)** | `sha256:3dad23e25b30c6dced2f6ec8cc979da377b4cb32e6b3d67241f435bc95e966a1` |
| **Runtime validation** | Branding grep PASS; PNL `ACCEPT/COMPLETED/COMMITTED/REGISTERED/tx_hash`; Template `ACCEPT/tx_hash` |
| **Known limitations** | Governance sub-panels retain "Registration Evidence" titles; hidden routes `/`, `/metrics`, `/defense` not removed from bundle; `sla_agent_status` not in submit metadata (pre-existing) |
| **Status** | PRODUCT UX HARDENED · OPERATOR LANGUAGE · CONTRACTS UNCHANGED |

**Usage:** All frontend deploy references MUST cite digest `be50ab59ec98...` unless a new freeze is explicitly registered. Supersedes `SPRINT_4A_FRONTEND_CONTRACT_ALIGNMENT_BASELINE` for runtime references.

---

## SPRINT_4E_TENANT_AUTOGENERATION_BASELINE (official — portal tenant autogen UX)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA Portal Frontend** after Sprint 4E tenant autogeneration UX |
| **Baseline name** | `SPRINT_4E_TENANT_AUTOGENERATION_BASELINE` |
| **Sprint** | SPRINT 4E — Tenant Autogeneration UX |
| **Audit dependency** | `sprint4d_tenant_autogeneration_feasibility_audit_20260530T031805Z/` |
| **Implementation pack** | `sprint4e_tenant_autogen_20260530T032253Z/` |
| **Commit (runtime)** | `4a20008bfd7e3d7b269b030da6de93119c4d3fa3` |
| **Message** | Tenant autogeneration UX improvement |
| **Prior frontend digest** | `sha256:be50ab59ec98705255d18724871fd1e8ad695c754aa0cdc8562e955b47eb7872` |
| **Digest (runtime SSOT)** | `sha256:f58cfd37a0d15dbc80dd5e1065740ec322acbcab7ea533b44e9d83f2242149fd` |
| **Image** | `ghcr.io/abelisboa/trisla-portal-frontend@sha256:f58cfd37a0d15dbc80dd5e1065740ec322acbcab7ea533b44e9d83f2242149fd` |
| **Build tag** | `20260530T032509Z` |
| **Deployment** | `trisla-portal-frontend` (namespace `trisla`, container `frontend`) |
| **NodePort** | `32561` |
| **Fix scope** | Auto-generate `trisla-{8hex}` tenant_id client-side; hide Tenant ID from PNL/Template forms; payload contract unchanged |
| **Backend digest (unchanged)** | `sha256:6baba68ac09771d02917fe1c63ad0cfcdc9f8775533c6b9a975fb6c129c628ac` |
| **SLA-Agent digest (unchanged)** | `sha256:3dad23e25b30c6dced2f6ec8cc979da377b4cb32e6b3d67241f435bc95e966a1` |
| **Runtime validation** | PNL HTML: no Tenant ID field; 3 interpret cases + submit ACCEPT; monitoring/administration HTTP 200 |
| **Risks** | Campaign scripts must still supply explicit tenant labels; post-submit panels may show tenant in service profile |
| **Status** | TENANT AUTOGEN UX · OPERATOR SIMPLIFIED · CONTRACTS UNCHANGED |

**Usage:** All frontend deploy references MUST cite digest `f58cfd37a0d1...` unless a new freeze is explicitly registered. Supersedes `SPRINT_4C_PRODUCT_UX_HARDENING_BASELINE` for runtime references.

---

## SPRINT_4G_TEMPLATE_AUTORESOLUTION_BASELINE (official — portal template autogen UX)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA Portal Frontend** after Sprint 4G template autoresolution UX |
| **Baseline name** | `SPRINT_4G_TEMPLATE_AUTORESOLUTION_BASELINE` |
| **Sprint** | SPRINT 4G — Template Autoresolution Implementation |
| **Audit dependency** | `sprint4f_template_autoresolution_audit_20260530T125817Z/` |
| **Implementation pack** | `sprint4g_template_autoresolution_20260530T130839Z/` |
| **Commit (runtime)** | `dcc6172a7382303dbdbc358fa482e1d22bfd6159` |
| **Message** | SPRINT_4G_TEMPLATE_AUTORESOLUTION |
| **Prior frontend digest** | `sha256:f58cfd37a0d15dbc80dd5e1065740ec322acbcab7ea533b44e9d83f2242149fd` |
| **Digest (runtime SSOT)** | `sha256:05a92b6204c1196afb6afd4c3a0f54cb1ddd3f09fa7332ed4fe143e74a34f93e` |
| **Image** | `ghcr.io/abelisboa/trisla-portal-frontend@sha256:05a92b6204c1196afb6afd4c3a0f54cb1ddd3f09fa7332ed4fe143e74a34f93e` |
| **Build tag** | `20260530T130902Z` |
| **Deployment** | `trisla-portal-frontend` (namespace `trisla`, container `frontend`) |
| **NodePort** | `32561` |
| **Fix scope** | Auto-resolve template_id from slice_type (URLLC/eMBB/mMTC SSOT map); hide Template ID from operator UX; submit payload contract unchanged |
| **Backend digest (unchanged)** | `sha256:6baba68ac09771d02917fe1c63ad0cfcdc9f8775533c6b9a975fb6c129c628ac` |
| **SLA-Agent digest (unchanged)** | `sha256:3dad23e25b30c6dced2f6ec8cc979da377b4cb32e6b3d67241f435bc95e966a1` |
| **Runtime validation** | PNL/Template: no Template ID field; 3 intents ACCEPT; COMPLETED/COMMITTED/REGISTERED/tx_hash |
| **Risks** | Unknown slice_type throws explicit error (no silent fallback); template_id visible in collapsed technical details only |
| **Status** | TEMPLATE AUTORESOLUTION UX · OPERATOR SIMPLIFIED · CONTRACTS UNCHANGED |

**Usage:** All frontend deploy references MUST cite digest `05a92b6204c1...` unless a new freeze is explicitly registered. Supersedes `SPRINT_4E_TENANT_AUTOGENERATION_BASELINE` for runtime references.

---

## SPRINT_4I_MONITORING_DOMAIN_CARDS_BASELINE (official — portal monitoring domain cards)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA Portal Frontend** after Sprint 4I monitoring domain cards alignment |
| **Baseline name** | `SPRINT_4I_MONITORING_DOMAIN_CARDS_BASELINE` |
| **Sprint** | SPRINT 4I — Monitoring Domain Cards Alignment |
| **Audit dependency** | `sprint4h_domain_metrics_ssot_audit_20260530T133827Z/` |
| **Implementation pack** | `sprint4i_monitoring_domain_cards_alignment_20260530T134824Z/` |
| **Commit (runtime)** | `310d771c545253542b881742de24d4045ee6ef69` |
| **Message** | Align monitoring domain cards with runtime metrics |
| **Prior frontend digest** | `sha256:05a92b6204c1196afb6afd4c3a0f54cb1ddd3f09fa7332ed4fe143e74a34f93e` |
| **Digest (runtime SSOT)** | `sha256:a50668fce172bf1a35b450143a907e22b87f575092e5393e588a48b2b47562b5` |
| **Image** | `ghcr.io/abelisboa/trisla-portal-frontend@sha256:a50668fce172bf1a35b450143a907e22b87f575092e5393e588a48b2b47562b5` |
| **Build tag** | `20260530T134928Z` |
| **Deployment** | `trisla-portal-frontend` (namespace `trisla`, container `frontend`) |
| **NodePort** | `32561` |
| **Fix scope** | RAN/Transport/Core cards use I1 + prometheus/summary fallbacks; remove stub module routes from Monitoring UX |
| **Backend digest (unchanged)** | `sha256:6baba68ac09771d02917fe1c63ad0cfcdc9f8775533c6b9a975fb6c129c628ac` |
| **Runtime validation** | No v2 title / no empty ok; PNL ACCEPT; routes 200 |
| **Known limitations** | `/metrics` page still uses legacy transport module stub |
| **Status** | MONITORING DOMAIN CARDS ALIGNED · HONEST AVAILABILITY · CONTRACTS UNCHANGED |

**Usage:** All frontend deploy references MUST cite digest `a50668fce172...` unless a new freeze is explicitly registered. Supersedes `SPRINT_4G_TEMPLATE_AUTORESOLUTION_BASELINE` for runtime references.

---

## SPRINT_5A_CORE_METRICS_REAL_ALIGNMENT_BASELINE (official — portal-backend cn-i1 core)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA Portal Backend** after Sprint 5A cn-i1 real core metrics |
| **Baseline name** | `SPRINT_5A_CORE_METRICS_REAL_ALIGNMENT_BASELINE` |
| **Sprint** | SPRINT 5A — Core Metrics Real Alignment |
| **Precheck dependency** | `sprint5_precheck_core_domain_reality_20260530T140033Z/` |
| **Implementation pack** | `sprint5a_core_metrics_real_alignment_20260530T140756Z/` |
| **Commit (runtime)** | `153af99151d4bb681df840e9335ca488e052911f` |
| **Message** | Align cn-i1 core metrics with real Prometheus container series |
| **Prior backend digest** | `sha256:6baba68ac09771d02917fe1c63ad0cfcdc9f8775533c6b9a975fb6c129c628ac` |
| **Digest (runtime SSOT)** | `sha256:b0d098cfeab39f1bf7cd21a353db87dc753ba80cfdf3645298d1b93df9026fb1` |
| **Image** | `ghcr.io/abelisboa/trisla-portal-backend@sha256:b0d098cfeab39f1bf7cd21a353db87dc753ba80cfdf3645298d1b93df9026fb1` |
| **Build tag** | `20260530T140813Z` |
| **Deployment** | `trisla-portal-backend` (namespace `trisla`, container `backend`) |
| **Frontend digest (unchanged)** | `sha256:a50668fce172bf1a35b450143a907e22b87f575092e5393e588a48b2b47562b5` |
| **Fix scope** | CN-I1 defaults → scoped `container_cpu_usage` / `container_memory_working_set` for `ns-1274485`; payload/URL unchanged |
| **Runtime validation** | cn-i1 cpu/memory non-null; PNL ACCEPT; routes 200 |
| **Known limitations** | Monitoring Active Sessions row still from summary (frontend); cpu field is rate sum not % label |
| **Status** | CORE → FONTE REAL · CN-I1 ALIGNED · CONTRACTS UNCHANGED |

**Usage:** All portal-backend deploy references MUST cite digest `b0d098cfeab3...` unless a new freeze is explicitly registered.

---

## SPRINT_5_OPERATOR_CONSOLE_HARDENING_BASELINE (official — portal-frontend operator UX)

| Field | Value |
|-------|-------|
| **Role** | Official runtime baseline for **TriSLA Portal Frontend** after Sprint 5 operator console hardening |
| **Baseline name** | `SPRINT_5_OPERATOR_CONSOLE_HARDENING_BASELINE` |
| **Sprint** | SPRINT 5 — Operator Console Hardening |
| **Dependencies** | `SPRINT_4I_MONITORING_DOMAIN_CARDS_ALIGNMENT_APPROVED`, `SPRINT_5A_CORE_METRICS_REAL_ALIGNMENT_APPROVED` |
| **Implementation pack** | `sprint5_operator_console_hardening_20260530T141809Z/` |
| **Commit (runtime)** | `01190167ae2ef69131a6f2c31712aebdd8db212e` |
| **Message** | Harden operator console UX for executive demonstration |
| **Prior frontend digest** | `sha256:a50668fce172bf1a35b450143a907e22b87f575092e5393e588a48b2b47562b5` |
| **Digest (runtime SSOT)** | `sha256:9efe10e5ebf4b4f65173a7c573f1ebe6e64e772931cbd5d777cec903344b81f8` |
| **Image** | `ghcr.io/abelisboa/trisla-portal-frontend@sha256:9efe10e5ebf4b4f65173a7c573f1ebe6e64e772931cbd5d777cec903344b81f8` |
| **Build tag** | `20260530T141910Z` |
| **Deployment** | `trisla-portal-frontend` (namespace `trisla`, container `frontend`) |
| **NodePort** | `32561` |
| **Backend digest (unchanged)** | `sha256:b0d098cfeab39f1bf7cd21a353db87dc753ba80cfdf3645298d1b93df9026fb1` |
| **Fix scope** | Frontend-only: formatted KPIs, operational labels, humanized lifecycle, Technical Details collapsed; contracts/APIs unchanged |
| **Runtime validation** | PNL URLLC/eMBB/mMTC ACCEPT+COMMITTED+REGISTERED+tx_hash; routes 200; cn-i1 real metrics |
| **Known limitations** | Raw API payloads unchanged; formatting is presentation-layer only |
| **Status** | OPERATOR CONSOLE HARDENED · EXECUTIVE DEMO READY · CONTRACTS UNCHANGED |

**Usage:** All frontend deploy references MUST cite digest `9efe10e5ebf4...` unless a new freeze is explicitly registered. Supersedes `SPRINT_4I_MONITORING_DOMAIN_CARDS_BASELINE` for runtime references.

---

## Freeze policy

1. Frozen CSV, JSONL, and figure bytes are **immutable** after registration.
2. New experimental campaigns require a **new** evidence pack directory and a **new** freeze manifest entry.
3. `RESULTS_FREEZE_MAIN` is the current official Results baseline until superseded by explicit user-approved re-freeze.
