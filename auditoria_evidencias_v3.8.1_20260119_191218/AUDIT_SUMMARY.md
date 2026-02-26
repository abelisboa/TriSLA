=== AUDITORIA EVIDENCIAS v3.8.1 ===
Timestamp: 20260119_191218
Namespace: trisla
Evidências: /home/porvir5g/gtp5g/trisla/evidencias_resultados_v3.8.1

## FASE 0 — Pré-check
- Arquivos encontrados: 19
⚠️ ALERTA: Existem arquivos vazios (evidência parcial).
Veja: VAZIOS.txt

## FASE 1 — Varredura de erros (linha-a-linha)
- ⚠️ ALERTA: padrões de erro encontrados (não reprova sozinho; precisa contexto).
  Arquivo: ERROS_ENCONTRADOS.txt (contém linha e arquivo)
  Total de ocorrências: 69

## FASE 2 — Validação de formato (JSON/CSV)
- JSON encontrados: 4
- ✅ Todos os JSON são válidos
- CSV encontrados: 0
- ✅ CSVs aparentam conter dados

## FASE 3 — Auditoria de SLAs (Portal) — 01_slas/
- Arquivos SLA: 5
- IDs extraídos (únicos): 0
❌ FAIL: Nenhum SLA/decision_id extraído das respostas do Portal.
   Correção necessária: alinhar endpoint e payload do Portal (template_id/form_values) e repetir coleta.
- ⚠️ Há indícios de falhas em respostas do Portal (ver SLA_FALHAS.txt)

## FASE 4 — Auditoria Decision Engine — 04_decisions/
- Decisões encontradas (RENEG/ACCEPT/REJECT): 4
- Decisões persistidas (linhas): 0
- Publicações Kafka I-04 (linhas): 0
- Publicações Kafka I-05 (linhas): 0
- Marcadores XAI no Decision Engine: 0 linhas
⚠️ ALERTA: Não encontrei marcadores explícitos de XAI no log do Decision Engine.
   (Pode existir XAI apenas na mensagem Kafka ou no retorno ao Portal; checar FASE 5/6.)

## FASE 5 — Auditoria ML-NSMF — 03_ml_predictions/
- Chamadas /predict vistas: 2
- Indicadores de fallback: 2 linhas
❌ FAIL: ML-NSMF aparenta estar em fallback em algum momento.
   Correção obrigatória antes de publicar: garantir modelo carregado (model_used=true) e estabilidade.
- Marcadores XAI no ML-NSMF: 0 linhas

## FASE 6 — Auditoria Kafka — 02_kafka/ + consumo interno (sem ImagePullBackOff)
- Linhas no kafka_logs.txt: 3663
- Kafka pod: kafka-c948b8d64-jgmz5
- Kafka bin: /opt/kafka/bin
- ✅ Tópicos listados (KAFKA_TOPICS.txt)
trisla-i04-decisions
trisla-i05-actions
Consumindo amostra de trisla-i04-decisions...
Consumindo amostra de trisla-i05-actions...
- decision_id únicos em I-04 (amostra): 0
- Marcadores XAI em I-04 (amostra): 0 linhas

## FASE 7 — Auditoria Blockchain — 05_blockchain/
- Marcadores de blockchain: 0 linhas
- Indícios de ACCEPT no Decision Engine: 0
0
- ✅ Blockchain consistente com cenário observado (ou não houve ACCEPT)

## FASE 8 — Gate Final DevOps (publicar no GitHub?)
- ⚠️ ALERTA: Sem SLA IDs do Portal, mas há 4 decisões no Decision Engine (evidência parcial).
- ❌ FAIL: ML-NSMF com fallback.
- ❌ FAIL: tópicos Kafka ausentes: Topic ausente: trisla-ml-predictions 
- ⚠️ ALERTA: sem decision_id no tópico I-04 (amostra). Kafka pode não ter mensagens reais.

### ❌ GATE_FINAL_STATUS: FAIL
Publicação BLOQUEADA. Correções obrigatórias abaixo (sem regressão):

#### Plano de Correção (sem regressão / sem mock)

1) Portal (SLA submissions)
   - Se 01_slas não tem decision_id/sla_id:
     - Confirmar endpoint real via OpenAPI do portal-backend.
     - Confirmar template_id + form_values válidos.
     - Reexecutar APENAS o gate E2E de 1 SLA por tipo (URLLC/eMBB/mMTC).
     - Somente após gerar SLA IDs reais, repetir coleta.

2) Kafka obrigatório
   - Se tópicos ausentes ou sem mensagens:
     - Verificar KAFKA_ENABLED/KAFKA_BROKERS nos deployments:
       - sem-csmf, decision-engine, ml-nsmf.
     - Confirmar Service kafka:9092 e listeners.
     - Garantir que os produtores publiquem em:
       - trisla-i04-decisions
       - trisla-i05-actions
       - trisla-ml-predictions
     - Reexecutar E2E mínimo (1 SLA) e reconsumir Kafka.

3) ML-NSMF sem fallback
   - Se aparecer fallback:
     - Confirmar modelo carregado (model_used=true), dependências (numpy compatível), arquivos /app/models.
     - Confirmar logs de predição e explicabilidade.
     - Reexecutar E2E mínimo (1 SLA) e validar.

4) Blockchain (apenas se houver ACCEPT)
   - Se houve ACCEPT e não há evidência on-chain:
     - Validar BC-NSSMF -> Besu RPC, contrato e logs de tx/hash.
     - Reexecutar até obter 1 ACCEPT e registrar.

5) Somente depois: build/publish v3.8.1
   - Build e push com working tree limpo e tags uniformes v3.8.1
   - Deploy helm com a mesma versão
   - Reexecutar E2E + Coleta

=== FIM AUDITORIA ===
