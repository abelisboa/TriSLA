# ML-NSMF — Machine Learning Network Slice Management Function

**Versão:** 3.7.10  
**Fase:** M (ML-NSMF)  
**Status:** Estabilizado

---

## 1. Visão Geral do Módulo

### Objetivo no TriSLA (Papel Arquitetural)

O **ML-NSMF** é responsável por prever a viabilidade de aceitação de SLAs baseado em métricas históricas, características do NEST e estado atual dos recursos da infraestrutura. O módulo utiliza Machine Learning (Random Forest) com Explainable AI (XAI) para fornecer predições transparentes e explicáveis.

**Papel no fluxo TriSLA:**
- **Entrada**: NEST completo do SEM-NSMF (via I-02 Kafka)
- **Processamento**: Análise de viabilidade usando modelo ML + XAI
- **Saída**: Predição de viabilidade com explicações enviada para Decision Engine (I-03)

### Entradas e Saídas (Alto Nível)

**Entradas:**
- NEST completo (Network Slice Template)
- Métricas atuais da infraestrutura (CPU, memória, bandwidth, slices ativos)
- Histórico de violações (quando disponível)

**Saídas:**
- Score de viabilidade (0.0 a 1.0)
- Confiança da predição (0.0 a 1.0)
- Explicação XAI (SHAP/LIME)
- Recomendação (ACCEPT/REJECT/RENEGOTIATE)

---

## 2. Componentes Internos

### 2.1 RiskPredictor
Classe principal que orquestra predição de viabilidade. Carrega modelo treinado, normaliza features e gera predições com explicações.

### 2.2 NESTConsumer
Consumer Kafka que recebe NESTs do SEM-NSMF via interface I-02. Processa mensagens assíncronas e dispara predições.

### 2.3 MetricsCollector
Coleta métricas atuais da infraestrutura via NASP Adapter. Agrega métricas de RAN, Transport e Core.

### 2.4 FeatureExtractor
Extrai e engenheira features do NEST e métricas. Cria features derivadas (ratios, combinações) para melhorar predição.

### 2.5 XAIExplainer
Gera explicações de predições usando SHAP (preferencial) ou LIME (fallback). Fornece feature importance e reasoning textual.

### 2.6 PredictionProducer
Producer Kafka que envia predições para Decision Engine via interface I-03.

---

## 3. Fluxo Operacional

### Passo a Passo

1. **Recepção de NEST**
   - Consumer Kafka recebe NEST do SEM-NSMF (I-02)
   - Tópico: `sem-csmf-nests`
   - Validação de formato

2. **Coleta de Métricas**
   - Consulta NASP Adapter para métricas atuais
   - Domínios: RAN, Transport, Core
   - Agregação e normalização

3. **Extração de Features**
   - Do NEST: tipo de slice, requisitos de SLA
   - Das métricas: CPU, memória, bandwidth, slices ativos
   - Feature engineering: ratios e combinações

4. **Normalização**
   - Usa scaler treinado (`scaler.pkl`)
   - Normalização StandardScaler

5. **Predição ML**
   - Modelo Random Forest gera score de viabilidade (0-1)
   - Threshold configurável (padrão: 0.7)

6. **Explicação XAI**
   - SHAP ou LIME gera explicação
   - Feature importance ranking
   - Reasoning textual

7. **Envio ao Decision Engine**
   - Producer Kafka envia predição (I-03)
   - Tópico: `ml-nsmf-predictions`

---

## 4. Interfaces

### 4.1 Interface I-02 (Kafka) — Entrada

**Protocolo:** Kafka  
**Direção:** SEM-NSMF → ML-NSMF  
**Tópico:** `sem-csmf-nests`  
**Partições:** 3  
**Replicação:** 1

**Descrição Conceitual:**
Recebe NEST completo do SEM-NSMF para análise de viabilidade. O NEST contém todas as informações necessárias para extração de features e predição.

**Payload (conceitual):**
- `nest_id`: Identificador único do NEST
- `intent_id`: Identificador do intent original
- `slice_type`: Tipo de slice (eMBB, URLLC, mMTC)
- `sla_requirements`: Requisitos de SLA completos
- `domain_config`: Configuração por domínio

### 4.2 Interface I-03 (Kafka) — Saída

**Protocolo:** Kafka  
**Direção:** ML-NSMF → Decision Engine  
**Tópico:** `ml-nsmf-predictions`  
**Partições:** 3  
**Replicação:** 1

**Descrição Conceitual:**
Envia predição de viabilidade com explicações XAI para o Decision Engine. A predição inclui score, confiança e explicação detalhada.

**Payload (conceitual):**
- `prediction_id`: Identificador único da predição
- `nest_id`: Referência ao NEST analisado
- `viability_score`: Score de viabilidade (0.0-1.0)
- `confidence`: Confiança da predição (0.0-1.0)
- `recommendation`: Recomendação (ACCEPT/REJECT/RENEGOTIATE)
- `xai_explanation`: Explicação XAI (SHAP/LIME)
- `feature_importance`: Importância de cada feature
- `timestamp`: Timestamp da predição

---

## 5. Dados e Modelos

### 5.1 Modelo de Decisão

**Modelo ML:** Random Forest Regressor

**Features (13 features):**
1. `latency`: Latência requerida (ms)
2. `throughput`: Throughput requerido (Mbps)
3. `reliability`: Confiabilidade requerida (0-1)
4. `jitter`: Jitter requerido (ms)
5. `packet_loss`: Taxa de perda de pacotes (0-1)
6. `cpu_utilization`: Utilização de CPU (0-1)
7. `memory_utilization`: Utilização de memória (0-1)
8. `network_bandwidth_available`: Bandwidth disponível (Mbps)
9. `active_slices_count`: Número de slices ativos
10. `slice_type_encoded`: Tipo de slice codificado (1=eMBB, 2=URLLC, 3=mMTC)
11. `latency_throughput_ratio`: Ratio latência/throughput
12. `reliability_packet_loss_ratio`: Ratio confiabilidade/perda
13. `jitter_latency_ratio`: Ratio jitter/latência

**Target:** `viability_score` (0.0-1.0)

**Documentação Completa:** [`decision-model.md`](decision-model.md)

### 5.2 Features e Regras

**Feature Engineering:**
- Ratios entre requisitos (latency/throughput, reliability/packet_loss)
- Combinações de métricas (CPU + memória)
- Normalização de valores

**Regras de Interpretação:**
- Score < 0.4: Baixo risco → ACCEPT
- Score 0.4-0.7: Risco médio → CONDITIONAL_ACCEPT ou RENEGOTIATE
- Score > 0.7: Alto risco → REJECT

**Documentação Completa:** [`decision-model.md`](decision-model.md)

### 5.3 XAI (Explainable AI)

**Métodos:**
- **SHAP (preferencial)**: SHapley Additive exPlanations
- **LIME (fallback)**: Local Interpretable Model-agnostic Explanations
- **Fallback**: Feature importance do modelo

**Explicação Inclui:**
- Feature importance ranking
- Contribuição de cada feature para a predição
- Reasoning textual explicando a decisão

**Documentação Completa:** [`xai.md`](xai.md)

---

## 6. Observabilidade e Métricas

### 6.1 Métricas Expostas

O módulo expõe métricas via endpoint `/metrics` (Prometheus):

- `trisla_predictions_total`: Total de predições realizadas
- `trisla_prediction_duration_seconds`: Duração de predição
- `trisla_prediction_accuracy`: Acurácia do modelo (quando disponível)
- `trisla_xai_explanations_total`: Total de explicações XAI geradas
- `trisla_xai_duration_seconds`: Duração de geração de explicação

### 6.2 Traces OpenTelemetry

Traces distribuídos são gerados para rastreabilidade:
- Span: `ml_nsmf.receive_nest` (I-02)
- Span: `ml_nsmf.collect_metrics`
- Span: `ml_nsmf.extract_features`
- Span: `ml_nsmf.predict_viability`
- Span: `ml_nsmf.generate_xai`
- Span: `ml_nsmf.send_prediction` (I-03)

### 6.3 Logs Estruturados

Logs estruturados incluem:
- `prediction_id`: Identificador da predição
- `nest_id`: Referência ao NEST
- `viability_score`: Score de viabilidade
- `confidence`: Confiança da predição
- `processing_time`: Tempo de processamento

---

## 7. Limitações Conhecidas

### 7.1 Modelo ML

- **Limitação**: Modelo Random Forest pode não capturar dependências temporais
- **Impacto**: Predições podem não refletir tendências de longo prazo
- **Mitigação**: Retreinar modelo periodicamente com novos dados

### 7.2 XAI

- **Limitação**: SHAP pode ser lento para modelos grandes
- **Impacto**: Latência de explicação pode aumentar
- **Mitigação**: Usar LIME como fallback ou limitar número de features

### 7.3 Coleta de Métricas

- **Limitação**: Métricas podem estar desatualizadas
- **Impacto**: Predições baseadas em dados obsoletos
- **Mitigação**: Cache de métricas com TTL curto

### 7.4 Feature Engineering

- **Limitação**: Features derivadas podem não capturar todas as relações
- **Impacto**: Predições podem ser menos precisas
- **Mitigação**: Revisar e adicionar features periodicamente

---

## 8. Como Ler a Documentação deste Módulo

### 8.1 Ordem Recomendada de Leitura

1. **Este README.md** — Visão geral e guia de leitura
2. **[decision-model.md](decision-model.md)** — Modelo de decisão e features
3. **[xai.md](xai.md)** — Explainable AI e explicações
4. **[implementation.md](implementation.md)** — Detalhes de implementação

### 8.2 Documentação Adicional

- **[ML_NSMF_COMPLETE_GUIDE.md](ML_NSMF_COMPLETE_GUIDE.md)** — Guia completo (referência)
- **[../ARCHITECTURE.md](../ARCHITECTURE.md)** — Arquitetura geral do TriSLA

### 8.3 Links para Outros Módulos

- **[SEM-NSMF](../sem-csmf/README.md)** — Módulo de interpretação semântica (envia NEST via I-02)
- **[Decision Engine](../../apps/decision-engine/README.md)** — Motor de decisão (recebe predição via I-03)
- **[BC-NSSMF](../bc-nssmf/README.md)** — Módulo de blockchain

---

**Última atualização:** 2025-01-27  
**Versão:** S4.0
