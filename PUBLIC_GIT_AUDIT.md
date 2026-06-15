# PUBLIC_GIT_AUDIT

Branch: main

Remote:
```text
origin	https://github.com/abelisboa/TriSLA.git (fetch)
origin	https://github.com/abelisboa/TriSLA.git (push)
```

Git status --short:
```text
M apps/bc-nssmf/README.md
 D apps/bc-nssmf/src/blockchain/wallet.py
 M apps/decision-engine/README.md
 M apps/decision-engine/src/engine.py
 M apps/decision-engine/src/main.py
 M apps/decision-engine/src/models.py
 M apps/decision-engine/src/service.py
 M apps/ml-nsmf/README.md
 M apps/ml-nsmf/src/main.py
 M apps/ml-nsmf/src/predictor.py
 M apps/nasp-adapter/Dockerfile
 M apps/nasp-adapter/k8s/nasp-adapter-rbac.yaml
 M apps/nasp-adapter/src/controllers/nsi_controller.py
 M apps/nasp-adapter/src/main.py
 M apps/nasp-adapter/src/metrics_collector.py
 M apps/nasp-adapter/src/nasp_client.py
 M apps/portal-backend/README_BACKEND.md
 M apps/portal-backend/src/main.py
 M apps/portal-backend/src/routers/prometheus.py
 M apps/portal-backend/src/routers/sla.py
 M apps/portal-backend/src/schemas/sla.py
 M apps/portal-backend/src/services/nasp.py
 M apps/portal-backend/src/services/slas.py
 M apps/portal-backend/src/telemetry/collector.py
 M apps/portal-backend/src/telemetry/contract_v2.py
 M apps/portal-backend/src/telemetry/promql_ssot.py
 M apps/portal-frontend/next.config.js
 M apps/portal-frontend/src/app/administration/page.tsx
 M apps/portal-frontend/src/app/defense/page.tsx
 M apps/portal-frontend/src/app/globals.css
 M apps/portal-frontend/src/app/layout.tsx
 M apps/portal-frontend/src/app/metrics/page.tsx
 M apps/portal-frontend/src/app/monitoring/page.tsx
 M apps/portal-frontend/src/app/page.tsx
 M apps/portal-frontend/src/app/pnl/page.tsx
 M apps/portal-frontend/src/app/sla-lifecycle/page.tsx
 M apps/portal-frontend/src/app/template/page.tsx
 M apps/portal-frontend/src/components/common/DataState.tsx
 M apps/portal-frontend/src/components/layout/Sidebar.tsx
 M apps/portal-frontend/src/components/layout/Topbar.tsx
 M apps/portal-frontend/src/lib/api.ts
 M apps/portal-frontend/src/lib/endpoints.ts
 M apps/sem-csmf/README.md
 M apps/sem-csmf/src/decision_engine_client.py
 M apps/sem-csmf/src/main.py
 M apps/sem-csmf/src/models/intent.py
 M apps/sla-agent-layer/README.md
 M apps/sla-agent-layer/requirements.txt
 M apps/sla-agent-layer/src/domain_compliance.py
 M apps/sla-agent-layer/src/main.py
 M docs/README.md
 M docs/bc-nssmf/README.md
 M docs/bc-nssmf/architecture/bc_nssmf_architecture.md
 M docs/bc-nssmf/blockchain/besu_integration.md
 M docs/bc-nssmf/contracts/sla_contract_model.md
 M docs/bc-nssmf/interfaces/interfaces.md
 M docs/bc-nssmf/pipeline/sla_lifecycle.md
 M docs/decision-engine/README.md
 M docs/decision-engine/architecture/decision_engine_architecture.md
 M docs/decision-engine/interfaces/interfaces.md
 M docs/decision-engine/model/decision_model.md
 M docs/decision-engine/pipeline/decision_flow.md
 M docs/ml-nsmf/README.md
 M docs/ml-nsmf/architecture/ml_nsmf_architecture.md
 M docs/ml-nsmf/examples/usage_examples.md
 M docs/ml-nsmf/interfaces/interfaces.md
 M docs/ml-nsmf/model/ml_model.md
 M docs/ml-nsmf/pipeline/prediction_pipeline.md
 M docs/nasp-adapter/README.md
 M docs/nasp-adapter/architecture/nasp_adapter_architecture.md
 M docs/nasp-adapter/integration/nasp_integration.md
 M docs/nasp-adapter/interfaces/interfaces.md
 M docs/nasp-adapter/model/metric_normalization_model.md
 M docs/nasp-adapter/observability/observability.md
 M docs/observability/OBSERVABILITY.md
 M docs/portal/README.md
 M docs/portal/architecture/portal_architecture.md
 M docs/portal/backend/README.md
 M docs/portal/experimental/workload_injection.md
 M docs/portal/frontend/README.md
 M docs/portal/model/interaction_model.md
 M docs/sem-csmf/README.md
 M docs/sem-csmf/architecture/sem_csmf_architecture.md
 M docs/sem-csmf/examples/usage_and_reproducibility.md
 M docs/sem-csmf/interfaces/interfaces.md
 M docs/sem-csmf/ontology/README.md
 M docs/sem-csmf/ontology/semantic_model_reference.md
 M docs/sem-csmf/pipeline/processing_pipeline.md
 M docs/sla-agent/README.md
 M docs/sla-agent/architecture/sla_agent_architecture.md
 M docs/sla-agent/interfaces/interfaces.md
 M docs/sla-agent/model/slo_evaluation_model.md
 M docs/sla-agent/observability/observability.md
 M docs/sla-agent/pipeline/lifecycle_execution.md
 M helm/trisla-portal/templates/backend-deployment.yaml
 M helm/trisla-portal/templates/frontend-deployment.yaml
 M helm/trisla-portal/values.yaml
 M helm/trisla/templates/deployment-nasp-adapter.yaml
 M helm/trisla/templates/deployment-sla-agent-layer.yaml
 M helm/trisla/templates/nasp-adapter-rbac.yaml
 M helm/trisla/values.yaml
?? FINAL_PUBLICATION_SCOPE_REPORT.md
?? GITHUB_PUBLICATION_READINESS.md
?? POST_SYNC_APPS_DIFF.md
?? POST_SYNC_DOCS_DIFF.md
?? POST_SYNC_HELM_DIFF.md
?? PUBLIC_GIT_AUDIT.md
?? PUBLIC_REPOSITORY_FINAL_STATE.md
?? apps/bc-nssmf/src/governance_lineage.py
?? apps/bc-nssmf/src/observability/distributed_trace.py
?? apps/decision-engine/src/decision_evidence.py
?? apps/decision-engine/src/feasibility_runtime.py
?? apps/decision-engine/src/i01_metadata_echo.py
?? apps/decision-engine/src/i01_nest_echo.py
?? apps/decision-engine/src/interfaces/
?? apps/decision-engine/src/lifecycle_authority.py
?? apps/decision-engine/src/nest_input_resolver.py
?? apps/decision-engine/src/observability/distributed_trace.py
?? apps/decision-engine/src/orchestration_authority.py
?? apps/decision-engine/src/trisla09_slice_aware_helpers.py
?? apps/decision-engine/tests/
?? apps/ml-nsmf/models/candidate/
?? apps/ml-nsmf/src/dual_load_config.py
?? apps/ml-nsmf/src/dual_load_service.py
?? apps/ml-nsmf/src/golden_vector_loader.py
?? apps/ml-nsmf/src/model_loader.py
?? apps/ml-nsmf/src/offline_replay_config.py
?? apps/ml-nsmf/src/offline_replay_engine.py
?? apps/ml-nsmf/src/offline_replay_executor.py
?? apps/ml-nsmf/src/pm2_symmetric_executor.py
?? apps/ml-nsmf/src/prediction_pipeline.py
?? apps/ml-nsmf/src/replay_context.py
?? apps/ml-nsmf/src/replay_manifest.py
?? apps/ml-nsmf/src/replay_parity.py
?? apps/ml-nsmf/src/replay_registry_hooks.py
?? apps/ml-nsmf/src/replay_snapshot.py
?? apps/ml-nsmf/src/replay_telemetry_gate.py
?? apps/ml-nsmf/src/runtime_shadow_decision.py
?? apps/ml-nsmf/src/runtime_shadow_executor.py
?? apps/ml-nsmf/src/shadow_event_schema.py
?? apps/ml-nsmf/src/shadow_logger.py
?? apps/ml-nsmf/src/shadow_logger_config.py
?? apps/ml-nsmf/src/shadow_registry_hooks.py
?? apps/ml-nsmf/src/shadow_sinks.py
?? apps/ml-nsmf/tests/
?? apps/nasp-adapter/README.md
?? apps/nasp-adapter/config/
?? apps/nasp-adapter/src/amf_binding_adapter.py
?? apps/nasp-adapter/src/amf_smf_correlation.py
?? apps/nasp-adapter/src/domain_actions/
?? apps/nasp-adapter/src/multidomain_metrics_exporter.py
?? apps/nasp-adapter/src/nasp_connectivity.py
?? apps/nasp-adapter/src/nssf_adapter.py
?? apps/nasp-adapter/src/ran_binding_adapter.py
?? apps/nasp-adapter/src/ran_correlation.py
?? apps/nasp-adapter/src/slice_service_binding.py
?? apps/nasp-adapter/src/smf_binding_adapter.py
?? apps/nasp-adapter/src/transport_binding_adapter.py
?? apps/nasp-adapter/src/transport_correlation.py
?? apps/nasp-adapter/src/upf_binding_adapter.py
?? apps/nasp-adapter/src/upf_correlation.py
?? apps/nasp-adapter/tests/
?? apps/portal-backend/src/api/
?? apps/portal-backend/src/domain_actions/
?? apps/portal-backend/src/observability/
?? apps/portal-backend/src/services/admission_compliance.py
?? apps/portal-backend/src/services/admission_decision.py
?? apps/portal-backend/src/services/governance_metadata.py
?? apps/portal-backend/src/services/nasp_reachability.py
?? apps/portal-backend/src/services/sla_explainability.py
?? apps/portal-backend/src/services/sla_lifecycle_success.py
?? apps/portal-backend/src/services/sla_operational_summary.py
?? apps/portal-backend/src/services/sla_revalidate_telemetry.py
?? apps/portal-backend/src/services/sla_status_assurance.py
?? apps/portal-backend/src/services/sla_status_telemetry.py
?? apps/portal-backend/src/services/sla_traceability.py
?? apps/portal-backend/src/telemetry/reliability_proxy.py
?? apps/portal-backend/tests/test_admission_compliance_wiring.py
?? apps/portal-backend/tests/test_admission_decision.py
?? apps/portal-backend/tests/test_cn_i1_promql_ssot.py
?? apps/portal-backend/tests/test_distributed_trace.py
?? apps/portal-backend/tests/test_explainability_recovery.py
?? apps/portal-backend/tests/test_governance_metadata.py
?? apps/portal-backend/tests/test_i1_routes_mounted.py
?? apps/portal-backend/tests/test_interpret_no_defaults.py
?? apps/portal-backend/tests/test_nasp_reachability.py
?? apps/portal-backend/tests/test_observability_promql_ssot.py
?? apps/portal-backend/tests/test_runtime_gating.py
?? apps/portal-backend/tests/test_sla_operational_summary.py
?? apps/portal-backend/tests/test_sla_status_assurance_governance.py
?? apps/portal-backend/tests/test_sla_status_schema_alignment.py
?? apps/portal-backend/tests/test_sprint5n3_lifecycle_success.py
?? apps/portal-backend/tests/test_sprint5n3_revalidate_telemetry.py
?? apps/portal-backend/tests/test_status_endpoint_p9.py
?? apps/portal-backend/tests/test_status_runtime_assurance.py
?? apps/portal-backend/tests/test_status_telemetry_snapshot.py
?? apps/portal-backend/tests/test_throughput_promql_alignment.py
?? apps/portal-frontend/.env.example
?? apps/portal-frontend/scripts/rc_p20_09_screenshots.mjs
?? apps/portal-frontend/scripts/rc_p20_09b_validation_screenshots.mjs
?? apps/portal-frontend/scripts/sprint10f_screenshots.mjs
?? apps/portal-frontend/scripts/sprint10g9_evidence_screenshots.mjs
?? apps/portal-frontend/scripts/test-administration-cleanup.mjs
?? apps/portal-frontend/scripts/test-lifecycle-runtime-snapshot.mjs
?? apps/portal-frontend/scripts/test-operator-ux.mjs
?? apps/portal-frontend/scripts/test-platform-reachability.mjs
?? apps/portal-frontend/scripts/test-runtime-assurance.mjs
?? apps/portal-frontend/scripts/test-throughput-alignment.mjs
?? apps/portal-frontend/src/app/nasp/
?? apps/portal-frontend/src/components/admission-dashboard/
?? apps/portal-frontend/src/components/consistency/
?? apps/portal-frontend/src/components/gating/
?? apps/portal-frontend/src/components/governance-dashboard/
?? apps/portal-frontend/src/components/lifecycle/
?? apps/portal-frontend/src/components/pnl/
?? apps/portal-frontend/src/components/runtime-supervision/
?? apps/portal-frontend/src/components/submit-payload/
?? apps/portal-frontend/src/components/workflow/
?? apps/portal-frontend/src/lib/administrationDisplay.ts
?? apps/portal-frontend/src/lib/admissionLifecycleGate.test.ts
?? apps/portal-frontend/src/lib/admissionLifecycleGate.ts
?? apps/portal-frontend/src/lib/admissionOperationalCache.test.ts
?? apps/portal-frontend/src/lib/admissionOperationalCache.ts
?? apps/portal-frontend/src/lib/blockchainEvidenceDisplay.test.ts
?? apps/portal-frontend/src/lib/blockchainEvidenceDisplay.ts
?? apps/portal-frontend/src/lib/complianceSeparation.test.ts
?? apps/portal-frontend/src/lib/confidenceDisplay.ts
?? apps/portal-frontend/src/lib/domainExplainability.ts
?? apps/portal-frontend/src/lib/domainExplainabilityUx.ts
?? apps/portal-frontend/src/lib/domainMonitoringCards.ts
?? apps/portal-frontend/src/lib/explainabilityRecovery.test.ts
?? apps/portal-frontend/src/lib/governanceDisplayLabels.test.ts
?? apps/portal-frontend/src/lib/governanceDisplayLabels.ts
?? apps/portal-frontend/src/lib/governanceEvidence.ts
?? apps/portal-frontend/src/lib/lifecycleRuntimeSnapshot.ts
?? apps/portal-frontend/src/lib/lifecycleViewFilter.test.ts
?? apps/portal-frontend/src/lib/lifecycleViewFilter.ts
?? apps/portal-frontend/src/lib/observedTelemetry.ts
?? apps/portal-frontend/src/lib/operatorDiagnostics.ts
?? apps/portal-frontend/src/lib/operatorFormat.ts
?? apps/portal-frontend/src/lib/operatorLabels.ts
?? apps/portal-frontend/src/lib/phaseNextConsistency.test.ts
?? apps/portal-frontend/src/lib/phaseNextConsistency.ts
?? apps/portal-frontend/src/lib/platformReachability.ts
?? apps/portal-frontend/src/lib/pnlSubmit.test.ts
?? apps/portal-frontend/src/lib/pnlSubmit.ts
?? apps/portal-frontend/src/lib/portalNavContext.tsx
?? apps/portal-frontend/src/lib/prometheusSummary.ts
?? apps/portal-frontend/src/lib/renegotiationPanelDisplay.test.ts
?? apps/portal-frontend/src/lib/renegotiationPanelDisplay.ts
?? apps/portal-frontend/src/lib/runtimeAssurance.ts
?? apps/portal-frontend/src/lib/runtimeAssuranceExplainability.test.ts
?? apps/portal-frontend/src/lib/runtimeAssuranceExplainability.ts
?? apps/portal-frontend/src/lib/runtimeAssuranceStateModel.ts
?? apps/portal-frontend/src/lib/runtimeSupervision.ts
?? apps/portal-frontend/src/lib/serviceProfileContract.test.ts
?? apps/portal-frontend/src/lib/serviceProfileContract.ts
?? apps/portal-frontend/src/lib/submitResponse.ts
?? apps/portal-frontend/src/lib/templateAutogen.ts
?? apps/portal-frontend/src/lib/tenantAutogen.ts
?? apps/ran-ue-upf-proxy/
?? apps/sem-csmf/src/canonical_sla.py
?? apps/sem-csmf/src/observability/distributed_trace.py
?? apps/sem-csmf/src/services/classification_config.py
?? apps/sem-csmf/src/services/entity_linker.py
?? apps/sem-csmf/src/services/semantic_resolver.py
?? apps/sem-csmf/tests/
?? apps/sla-agent-layer/src/actuation/
?? apps/sla-agent-layer/src/availability_proxy.py
?? apps/sla-agent-layer/src/consistency/
?? apps/sla-agent-layer/src/observability/distributed_trace.py
?? apps/sla-agent-layer/src/reliability_proxy.py
?? apps/sla-agent-layer/src/remediation/
?? apps/sla-agent-layer/src/revalidate/
?? apps/sla-agent-layer/src/runtime_assurance_store.py
?? apps/sla-agent-layer/src/runtime_slo_evaluator.py
?? apps/sla-agent-layer/src/transport_policy.py
?? apps/sla-agent-layer/tests/
?? docs/CAPITULOS_7_8_9_FINAL_DISSERTACAO.md
?? docs/CAPITULO_6_PROTOTIPO_DISSERTACAO.md
?? docs/FINAL_CANONICAL_REFERENCE_REPORT.md
?? docs/FINAL_CLEANUP_CHANGESET.md
?? docs/FINAL_CROSS_LINK_REPORT.md
?? docs/FINAL_DOCUMENTATION_COVERAGE_REPORT.md
?? docs/FINAL_DOCUMENT_FREEZE_READINESS_REPORT.md
?? docs/FINAL_INTERFACE_VOCABULARY_REPORT.md
?? docs/FINAL_LEGACY_CONTENT_REPORT.md
?? docs/FINAL_Q1_SCIENTIFIC_READINESS_REPORT.md
?? docs/FINAL_RUNTIME_CONSISTENCY_REPORT.md
?? docs/INTERFACE_DECISION_RECOMMENDATION.md
?? docs/INTERFACE_MIGRATION_PLAN.md
?? docs/INTERFACE_NON_REGRESSION_CHECKLIST.md
?? docs/INTERFACE_TRACEABILITY_MATRIX.md
?? docs/MASTER_PLAN_UPDATE_REPORT.md
?? docs/PROMPT_TRISLA_FINAL_SCIENTIFIC_CLOSURE_PROGRAM_V1
?? docs/PROMQL_SSOT_V2.md
?? docs/PROPOSED_INTERFACE_MODEL.md
?? docs/RECOVERED/
?? docs/REFACTOR_TRISLA_RESPONSIBILITY_GUIDE.md
?? docs/SSOT_RECOVERY/
?? docs/TRISLA_ARCHITECTURE_EVIDENCE.md
?? docs/TRISLA_ARCHITECTURE_EVIDENCE_PATCHED.md
?? docs/TRISLA_CANONICAL_SLA_MODEL.md
?? docs/TRISLA_E2E_FLOW_CANONICAL.md
?? docs/TRISLA_EVOLUTION_MASTER_PLAN_V1.md
?? docs/TRISLA_EXPERIMENTAL_CANONICAL/
?? docs/TRISLA_FINAL_AUDIT_FOR_PAPER.md
?? docs/TRISLA_FINAL_RUNTIME_BASELINE_Q1.md
?? docs/TRISLA_GSMA_ALIGNMENT_EXECUTION_RULES.md
?? docs/TRISLA_GSMA_ALIGNMENT_MASTER_RUNBOOK.md
?? docs/TRISLA_INFRA_SNAPSHOT_20260413T123324Z.md
?? docs/TRISLA_INFRA_SSOT.md
?? docs/TRISLA_MASTER_RUNBOOK.md
?? docs/TRISLA_MASTER_SSOT_RUNTIME_BASELINE_V1.md
?? docs/TRISLA_SLICE_RUNTIME_EXECUTION_CONTROL.md
?? docs/TRISLA_WORKDIR_OPERACIONAL.md
?? docs/final_q1_scientific_package/
?? docs/final_scientific_freeze/
?? docs/interfaces/
?? docs/modules/
?? docs/paper/
?? docs/paper_q1_figures/
?? docs/paper_submission_package_20260518T143642Z/
?? docs/paper_submission_package_20260518T143651Z/
?? docs/paper_submission_package_20260518T143656Z/
?? docs/paper_submission_package_20260518T143702Z/
?? docs/scripts/
?? helm/trisla-portal/templates/_helpers.tpl
?? helm/trisla/templates/prometheusrule-trisla-recording.yaml
?? helm/trisla/templates/service-nasp-adapter-metrics.yaml
?? helm/trisla/templates/servicemonitor-nasp-adapter.yaml
```

Git diff --stat:
```text
apps/bc-nssmf/README.md                            | 308 +-------
 apps/bc-nssmf/src/blockchain/wallet.py             |  29 -
 apps/decision-engine/README.md                     | 328 +-------
 apps/decision-engine/src/engine.py                 |   8 +
 apps/decision-engine/src/main.py                   |   8 +-
 apps/decision-engine/src/models.py                 |   6 +-
 apps/decision-engine/src/service.py                |  11 +
 apps/ml-nsmf/README.md                             | 297 +-------
 apps/ml-nsmf/src/main.py                           |  71 +-
 apps/ml-nsmf/src/predictor.py                      |  45 +-
 apps/nasp-adapter/Dockerfile                       |   1 +
 apps/nasp-adapter/k8s/nasp-adapter-rbac.yaml       |  12 +-
 .../nasp-adapter/src/controllers/nsi_controller.py | 452 ++++++++++-
 apps/nasp-adapter/src/main.py                      | 518 ++++++++++++-
 apps/nasp-adapter/src/metrics_collector.py         |   7 +-
 apps/nasp-adapter/src/nasp_client.py               | 236 +++---
 apps/portal-backend/README_BACKEND.md              | 188 ++---
 apps/portal-backend/src/main.py                    |   9 +-
 apps/portal-backend/src/routers/prometheus.py      |  28 +-
 apps/portal-backend/src/routers/sla.py             | 806 ++++++++++++++++++--
 apps/portal-backend/src/schemas/sla.py             |  50 +-
 apps/portal-backend/src/services/nasp.py           | 136 +++-
 apps/portal-backend/src/services/slas.py           |   6 +-
 apps/portal-backend/src/telemetry/collector.py     |  67 +-
 apps/portal-backend/src/telemetry/contract_v2.py   |  20 +
 apps/portal-backend/src/telemetry/promql_ssot.py   |  65 +-
 apps/portal-frontend/next.config.js                |  19 +-
 .../src/app/administration/page.tsx                | 131 +++-
 apps/portal-frontend/src/app/defense/page.tsx      |  31 +-
 apps/portal-frontend/src/app/globals.css           | 832 +++++++++++++++++++++
 apps/portal-frontend/src/app/layout.tsx            |  20 +-
 apps/portal-frontend/src/app/metrics/page.tsx      |  47 +-
 apps/portal-frontend/src/app/monitoring/page.tsx   | 314 ++++----
 apps/portal-frontend/src/app/page.tsx              | 297 +++-----
 apps/portal-frontend/src/app/pnl/page.tsx          | 358 ++++-----
 .../portal-frontend/src/app/sla-lifecycle/page.tsx | 684 ++++++++++++-----
 apps/portal-frontend/src/app/template/page.tsx     | 340 +++------
 .../src/components/common/DataState.tsx            |   4 +-
 .../src/components/layout/Sidebar.tsx              | 121 +--
 .../src/components/layout/Topbar.tsx               |  11 +-
 apps/portal-frontend/src/lib/api.ts                | 259 +++++--
 apps/portal-frontend/src/lib/endpoints.ts          |  40 +-
 apps/sem-csmf/README.md                            |  40 +-
 apps/sem-csmf/src/decision_engine_client.py        |  28 +-
 apps/sem-csmf/src/main.py                          | 166 +++-
 apps/sem-csmf/src/models/intent.py                 |   2 +
 apps/sla-agent-layer/README.md                     | 237 ++----
 apps/sla-agent-layer/requirements.txt              |   1 +
 apps/sla-agent-layer/src/domain_compliance.py      | 433 +++++++----
 apps/sla-agent-layer/src/main.py                   | 237 +++++-
 docs/README.md                                     |   2 +
 docs/bc-nssmf/README.md                            |  84 +--
 .../bc-nssmf/architecture/bc_nssmf_architecture.md |  28 +-
 docs/bc-nssmf/blockchain/besu_integration.md       |   3 +
 docs/bc-nssmf/contracts/sla_contract_model.md      |  60 +-
 docs/bc-nssmf/interfaces/interfaces.md             |  53 +-
 docs/bc-nssmf/pipeline/sla_lifecycle.md            |  32 +-
 docs/decision-engine/README.md                     | 130 +---
 .../architecture/decision_engine_architecture.md   |  28 +-
 docs/decision-engine/interfaces/interfaces.md      |  76 +-
 docs/decision-engine/model/decision_model.md       | 103 +--
 docs/decision-engine/pipeline/decision_flow.md     |  17 +-
 docs/ml-nsmf/README.md                             |  97 +--
 docs/ml-nsmf/architecture/ml_nsmf_architecture.md  |  55 +-
 docs/ml-nsmf/examples/usage_examples.md            |  60 +-
 docs/ml-nsmf/interfaces/interfaces.md              |  68 +-
 docs/ml-nsmf/model/ml_model.md                     | 133 +---
 docs/ml-nsmf/pipeline/prediction_pipeline.md       |  96 +--
 docs/nasp-adapter/README.md                        |  58 +-
 .../architecture/nasp_adapter_architecture.md      |  98 ++-
 docs/nasp-adapter/integration/nasp_integration.md  |  84 ++-
 docs/nasp-adapter/interfaces/interfaces.md         | 104 ++-
 .../model/metric_normalization_model.md            |  69 +-
 docs/nasp-adapter/observability/observability.md   |  80 +-
 docs/observability/OBSERVABILITY.md                | 149 ++--
 docs/portal/README.md                              |   5 +-
 docs/portal/architecture/portal_architecture.md    |  47 +-
 docs/portal/backend/README.md                      | 144 ++--
 docs/portal/experimental/workload_injection.md     |   2 +
 docs/portal/frontend/README.md                     | 111 ++-
 docs/portal/model/interaction_model.md             |   2 +
 docs/sem-csmf/README.md                            |  94 +--
 .../sem-csmf/architecture/sem_csmf_architecture.md | 110 +--
 .../sem-csmf/examples/usage_and_reproducibility.md | 122 +--
 docs/sem-csmf/interfaces/interfaces.md             | 161 ++--
 docs/sem-csmf/ontology/README.md                   |  37 +-
 docs/sem-csmf/ontology/semantic_model_reference.md |   3 +
 docs/sem-csmf/pipeline/processing_pipeline.md      | 128 ++--
 docs/sla-agent/README.md                           |  78 +-
 .../architecture/sla_agent_architecture.md         |  38 +-
 docs/sla-agent/interfaces/interfaces.md            |  64 +-
 docs/sla-agent/model/slo_evaluation_model.md       |  93 ++-
 docs/sla-agent/observability/observability.md      |   4 +
 docs/sla-agent/pipeline/lifecycle_execution.md     |  69 +-
 .../templates/backend-deployment.yaml              |   2 +-
 .../templates/frontend-deployment.yaml             |   2 +-
 helm/trisla-portal/values.yaml                     |  10 +-
 helm/trisla/templates/deployment-nasp-adapter.yaml |  32 +
 .../templates/deployment-sla-agent-layer.yaml      |  26 +
 helm/trisla/templates/nasp-adapter-rbac.yaml       |   9 +
 helm/trisla/values.yaml                            |  60 +-
 101 files changed, 7081 insertions(+), 4503 deletions(-)
```
## Final Publication Preconditions

DRIFT = 0
POST_SYNC_MISSING = 0
POST_SYNC_EXTRA = 0
POST_SYNC_DIFFERENT = 0
PUBLIC_REPOSITORY_ALIGNED = TRUE

