# Cursor Workflow Rules

## ML Calibration Rules

- ML calibration must be performed before image build and deployment.
- No threshold manipulation is allowed post-deploy to force class outcomes.
- Risk must remain continuous and calibrated; avoid probability saturation.
- Offline multiclasse validation is mandatory before promoting model artifacts.
- Bootstrap/synthetic data is allowed for training bootstrap only and must never be used as experimental evidence.

## TriSLA Figure Integrity Rules — Figure 01 and Figure 05

- Never publish Figure 01 as `semantic + decision` only; include pipeline modules `semantic`, `ml`, `decision`, `nasp`, `blockchain`.
- Use canonical latency columns in all collection and plotting scripts: `semantic_latency_ms`, `ml_latency_ms`, `decision_latency_ms`, `nasp_latency_ms`, `blockchain_latency_ms`.
- If NASP or blockchain latency is unavailable, keep the column with `NaN` and register the gap in manifest (`missing_instrumentation`), never hide it.
- Figure 05 must be data-driven with observed classes only from `ACCEPT`, `RENEGOTIATE`, `REJECT`; do not hardcode class subsets.
- Figure 05 can be `INCLUDED_IN_PAPER` only with minimum class diversity (>=2 classes with n>=5 each). Otherwise set `EXCLUDED_LOW_SIGNAL` with scientific reason.
- `UNKNOWN` must be treated as operational failure (`decision_source=operational_failure`) and excluded from scientific decision plots.
- Every final dataset export must persist canonical provenance flags: `decision_source`, `unknown_cause`, `nasp_latency_available`, `blockchain_latency_available`.
- For reproducible execution inside Cursor, always use workdir `/home/porvir5g/gtp5g/trisla`.
- Preferred one-shot command in Cursor terminal:
  - `bash /home/porvir5g/gtp5g/trisla/scripts/e2e/run_level1_fixed_pipeline.sh`
- This one-shot command must run the full paper generator (`apps/portal-frontend/scripts/generate_figures_ieee_final_master.py`) and produce the complete figure set, not only Figure 01/Figure 05 corrections.

## SLA-aware Metrics Rule

All SLA-aware metrics must be validated via real endpoint before deployment.

Deployment is strictly forbidden without validation of:
- sla_metrics presence
- non-null values
- JSON integrity

## GOVERNANÇA DE PROMPTS (SSOT — TRI-SLA)

### 1. Identificação Única de Prompt

Todo prompt deve possuir identificador único no formato:

PROMPT_<NÚMERO> — <DESCRIÇÃO>

Exemplo:

PROMPT_01 — COLETA E2E CONSOLIDADA NASP (TRISLA)

### 2. Numeração Sequencial Obrigatória

- A numeração deve ser crescente (PROMPT_01, PROMPT_02, ...)
- NÃO reutilizar números
- NÃO criar ramificações paralelas

### 3. Evolução Controlada

Todo novo prompt deve declarar:

BASE: PROMPT_<N-1>
TIPO: (EVOLUÇÃO / EXTENSÃO / CORREÇÃO)
REGRESSÃO: PROIBIDA

### 4. Regra de Substituição

- Cada novo prompt substitui logicamente o anterior
- NÃO manter múltiplos prompts equivalentes
- Apenas um prompt deve ser considerado ativo (SSOT)

### 5. Proibição de Duplicidade

É proibido criar:

- PROMPT_FINAL
- PROMPT_CORRIGIDO
- PROMPT_V2
- PROMPT_TESTE
- PROMPT_NEW

### 6. Fonte Única de Verdade (SSOT)

Sempre deve existir:

👉 1 único prompt ativo para cada tipo de execução (ex: coleta E2E)

### 7. Preservação Histórica

- Prompts antigos NÃO devem ser apagados automaticamente
- Devem ser considerados obsoletos, mas mantidos para rastreabilidade

### 8. Regra Anti-Regressão

- Nenhum prompt novo pode remover funcionalidades já validadas
- Apenas extensões ou ajustes incrementais são permitidos

### 9. Execução Científica

Todo prompt deve garantir:

- uso de dados reais
- execução end-to-end
- ausência de simulação
- reprodutibilidade

### 10. Integração com Runbook

Estas regras passam a ser parte obrigatória do fluxo operacional TriSLA.

### 11. Arquitetura multi-domínio NASP (PROMPT_15.1)

Todos os prompts e execuções experimentais devem, quando a referência for o **protótipo NASP documental**:

- utilizar explicitamente os **três domínios** **RAN + TRANSPORT + CORE** quando estes estiverem **disponíveis e ativos** no ambiente;
- seguir o **fluxo E2E completo** descrito no `docs/TRISLA_MASTER_RUNBOOK.md` (SEM → ML → Decision → verificação multi-domínio → orquestração → observabilidade);
- **não simplificar** a arquitetura alvo (ONOS/Mininet/Core/RANTester/OAI) em narrativas ou coletas sem registrar a lacuna no manifesto de evidências;
- **não usar proxies de telemetria** (por exemplo *probes* ou índices compostos) como substituto definitivo de um domínio real **quando** esse domínio existir implantado e observável — proxies só são aceitáveis como **medida transitória documentada** (ver `docs/AUDITORIA_PROMPT15_1_NASP_FULL_STACK.md`).

Quando **um domínio obrigatório não estiver ativo**, o prompt deve declarar o ensaio como **parcial** e citar o relatório de auditoria correspondente.
