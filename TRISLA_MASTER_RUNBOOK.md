
## [2026-02-25T16:53:24Z] - FASTAPI METRICS PATCH (Pré-requisito)

Motivo: Cluster não está estável (há pods em erro). ABORT para evitar regressão.
Status: ABORT
Evidências: evidencias_trisla_fastapi_instrumentation_digest_only_20260225T165324Z


## [2026-02-25T17:44:58Z] - DEPLOY kafka

Imagem: ghcr.io/abelisboa/kafka@sha256:8291bed273105a3fc88df5f89096abf6a654dc92b0937245dcef85011f3fc5e6
Motivo: Rollback após ImagePullBackOff na revision 12
Validação Pull: OK
Rollout: OK
Status: PASS
Evidências: evidencias_runbook_update_20260225T174458Z

