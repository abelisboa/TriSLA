# Interface Decision Recommendation - TriSLA

Base: consolidação dos artefatos de auditoria de interfaces e matriz de rastreabilidade.

## 1) Quais interfaces devem ser formalizadas primeiro?
Priorizar interfaces críticas da cadeia fim-a-fim (impactam diretamente `submit`, decisão e orquestração):

1. `POST /api/v1/sla/submit` (Frontend -> Portal)  
2. `POST /api/v1/intents` e `POST /api/v1/interpret` (Portal -> SEM)  
3. `POST /evaluate` (SEM -> Decision)  
4. `POST /api/v1/predict` (Decision -> ML)  
5. `POST /api/v1/nsi/instantiate` (Portal -> NASP Adapter)  
6. `POST /api/v1/register-sla` (Portal -> BC-NSSMF)  
7. `telemetry_snapshot` propagation e consultas Prometheus (`/api/v1/prometheus/*`)

Racional: essas interfaces concentram maior criticidade e maior risco de regressão descritos em `AUDIT_SUMMARY.md` e checklist de não regressão.

## 2) Quais devem permanecer apenas como wrappers?
Manter como wrappers (sem necessidade de substituição imediata):

- `GET /api/v1/prometheus/query` (SEM -> Portal)  
- `SLA_AGENT_PIPELINE_INGEST_URL` (endpoint configurável de ingestão)  
- `/api/v1/agents/ran/*`, `/api/v1/agents/transport/*`, `/api/v1/agents/core/*`  
- `POST /api/v1/3gpp/gate`, `POST /api/v1/sla/register` (adapter path)

Racional: interfaces auxiliares/observabilidade com menor necessidade de ruptura; melhor encapsular e padronizar naming primeiro.

## 3) Quais têm maior risco de regressão?
Interfaces de maior risco:

- `POST /api/v1/sla/submit` (entrada do pipeline completo)
- `POST /evaluate` (ponto de decisão central)
- `POST /api/v1/predict` (dependência direta do motor de decisão)
- `POST /api/v1/nsi/instantiate` (orquestração de core)
- `POST /api/v1/register-sla` + propagação `tx_hash`/`block_number`
- `metadata.telemetry_snapshot` propagation
- Kafka event bus (eventos de decisão/predição/pipeline)

Racional: falhas nesses pontos quebram o encadeamento principal ou a rastreabilidade científica/operacional.

## 4) Qual ordem segura de implementação?
Ordem recomendada (zero-regressão):

1. **Shadow**: fechar catálogo + matriz + owners + checklist operativo.  
2. **Wrapper**: encapsular interfaces críticas sem alterar endpoint/payload externo.  
3. **Dual**: executar caminho legado + caminho formal em paralelo com comparação de outputs.  
4. **Switch**: ativar por flags por domínio/interface, com rollback imediato.  
5. **Depreciação**: reduzir caminhos internos legados somente após estabilidade comprovada.

Essa sequência é consistente com `INTERFACE_MIGRATION_PLAN.md` e guardrails de não regressão.

## 5) TriSLA deve adotar RAN-I1/TN-I1/CN-I1 ou mapear diretamente para RN1/TN1/CN1 do NASP?
Recomendação: **adotar nomes próprios TriSLA (`RAN-I1`, `TN-I1`, `CN-I1`, `OBS-I1`, `BC-I1`) com tabela de mapeamento explícita para nomenclaturas NASP/padrões**.

Justificativa:
- Preserva clareza arquitetural interna do TriSLA (inclui `OBS-I1` e `BC-I1`, que não são cobertos de forma direta por naming estritamente RAN/TN/CN).
- Evita acoplamento semântico rígido a um único referencial externo.
- Mantém compatibilidade futura: basta manter matriz de equivalência (`TriSLA name -> NASP/3GPP/O-RAN/ETSI`).

Decisão prática:
- Curto prazo: `RAN-I1/TN-I1/CN-I1/OBS-I1/BC-I1` como naming canônico de governança interna.
- Paralelamente: coluna de equivalência externa obrigatória na matriz de rastreabilidade.
