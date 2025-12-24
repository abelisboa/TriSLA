# SEM-NSMF — Semantic-enhanced Network Slice Management Function

**Versão:** 3.7.10  
**Fase:** S (SEM-NSMF)  
**Status:** Estabilizado

---

## 1. Visão Geral do Módulo

### Objetivo no TriSLA (Papel Arquitetural)

O **SEM-NSMF** é o módulo de entrada do TriSLA, responsável por receber intents de alto nível dos tenants, interpretá-los semanticamente usando ontologias OWL, processá-los com NLP (quando necessário) e gerar Network Slice Templates (NEST) estruturados para provisionamento de network slices.

**Papel no fluxo TriSLA:**
- **Entrada**: Intents de tenants (linguagem natural ou estruturado)
- **Processamento**: Interpretação semântica + NLP + Geração de NEST
- **Saída**: NEST validado enviado para Decision Engine (I-01) e ML-NSMF (I-02)

### Entradas e Saídas (Alto Nível)

**Entradas:**
- Intent de tenant (HTTP REST ou gRPC)
- Requisitos de SLA (latência, throughput, confiabilidade, etc.)
- Tipo de slice (eMBB, URLLC, mMTC)

**Saídas:**
- NEST (Network Slice Template) validado semanticamente
- Metadados de NEST para Decision Engine (I-01)
- NEST completo para ML-NSMF (I-02)

---

## 2. Componentes Internos

### 2.1 IntentProcessor
Processador principal que orquestra o fluxo completo de processamento de intents, desde a recepção até a geração de NEST.

### 2.2 OntologyLoader e SemanticReasoner
Carregamento e validação semântica usando ontologia OWL. Valida requisitos de SLA contra classes e propriedades definidas na ontologia.

### 2.3 NLPParser
Processamento de linguagem natural para extrair informações de intents em texto livre. Identifica tipo de slice e requisitos de SLA.

### 2.4 NESTGenerator
Geração de Network Slice Templates a partir de intents validados. Converte GST (Generic Slice Template) para NEST estruturado.

### 2.5 DecisionEngineClient
Cliente gRPC para comunicação com Decision Engine via interface I-01.

### 2.6 NESTProducer
Producer Kafka para envio de NESTs para ML-NSMF via interface I-02.

---

## 3. Fluxo Operacional

### Passo a Passo

1. **Recepção de Intent**
   - Recebe intent via HTTP REST (`POST /api/v1/intents`) ou gRPC
   - Valida formato e campos obrigatórios

2. **Processamento NLP** (se linguagem natural)
   - Extrai tipo de slice (eMBB, URLLC, mMTC)
   - Extrai requisitos de SLA (latência, throughput, etc.)
   - Normaliza dados para formato estruturado

3. **Validação Semântica**
   - Carrega ontologia OWL (`trisla.ttl`)
   - Valida intent contra classes e propriedades da ontologia
   - Executa reasoning semântico (Pellet)

4. **Geração de NEST**
   - Converte GST (Generic Slice Template) para NEST
   - Valida requisitos contra ontologia
   - Persiste em PostgreSQL

5. **Envio para Módulos Downstream**
   - **I-01 (gRPC)**: Envia metadados de NEST para Decision Engine
   - **I-02 (Kafka)**: Envia NEST completo para ML-NSMF

---

## 4. Interfaces

### 4.1 Interface I-01 (gRPC)

**Protocolo:** gRPC  
**Direção:** SEM-NSMF → Decision Engine  
**Endpoint:** `decision-engine:50051`  
**Serviço:** `ProcessNESTMetadata`

**Descrição Conceitual:**
Transmissão síncrona de metadados de NEST para o Decision Engine. Inclui informações essenciais para tomada de decisão (intent_id, nest_id, tipo de slice, requisitos de SLA).

**Payload (conceitual):**
- `nest_id`: Identificador único do NEST
- `intent_id`: Identificador do intent original
- `tenant_id`: Identificador do tenant
- `service_type`: Tipo de slice (eMBB, URLLC, mMTC)
- `sla_requirements`: Requisitos de SLA (latência, throughput, confiabilidade)

### 4.2 Interface I-02 (Kafka)

**Protocolo:** Kafka  
**Direção:** SEM-NSMF → ML-NSMF  
**Tópico:** `sem-csmf-nests`  
**Partições:** 3  
**Replicação:** 1

**Descrição Conceitual:**
Transmissão assíncrona de NEST completo para o ML-NSMF. O NEST contém todas as informações necessárias para análise de viabilidade e predição.

**Payload (conceitual):**
- `nest_id`: Identificador único do NEST
- `intent_id`: Identificador do intent original
- `slice_type`: Tipo de slice
- `sla_requirements`: Requisitos de SLA completos
- `domain_config`: Configuração por domínio (RAN, Transport, Core)
- `timestamp`: Timestamp de geração

---

## 5. Dados e Modelos

### 5.1 Ontologia OWL

**Localização:** `apps/sem-csmf/src/ontology/trisla.ttl`

**Classes Principais:**
- **Intent**: Intenção de serviço do tenant
- **SliceType**: Tipo de slice (eMBB, URLLC, mMTC)
- **SLA**: Service Level Agreement
- **SLO**: Service Level Objective
- **Metric**: Métricas de performance

**Propriedades:**
- `hasLatency`: Latência requerida
- `hasThroughput`: Throughput requerido
- `hasReliability`: Confiabilidade requerida
- `hasDomain`: Domínio de rede (RAN, Transport, Core)

**Documentação Completa:** [`ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)

### 5.2 Entidades Principais

**Intent:**
- `intent_id`: Identificador único
- `tenant_id`: Identificador do tenant
- `service_type`: Tipo de slice (eMBB, URLLC, mMTC)
- `sla_requirements`: Requisitos de SLA

**NEST (Network Slice Template):**
- `nest_id`: Identificador único
- `intent_id`: Referência ao intent original
- `slice_type`: Tipo de slice
- `sla_requirements`: Requisitos de SLA validados
- `domain_config`: Configuração por domínio
- `created_at`: Timestamp de criação

### 5.3 Mapeamento GST → NEST

**GST (Generic Slice Template):**
- Template genérico extraído do intent
- Não validado semanticamente

**NEST (Network Slice Template):**
- Template validado contra ontologia
- Estruturado conforme especificação O-RAN
- Pronto para provisionamento

---

## 6. Observabilidade e Métricas

### 6.1 Métricas Expostas

O módulo expõe métricas via endpoint `/metrics` (Prometheus):

- `trisla_intents_total`: Total de intents processados
- `trisla_nests_generated_total`: Total de NESTs gerados
- `trisla_intent_processing_duration_seconds`: Duração de processamento de intent
- `trisla_ontology_validation_duration_seconds`: Duração de validação semântica
- `trisla_nest_generation_duration_seconds`: Duração de geração de NEST

### 6.2 Traces OpenTelemetry

Traces distribuídos são gerados para rastreabilidade:
- Span: `sem_nsmf.process_intent`
- Span: `sem_nsmf.validate_semantic`
- Span: `sem_nsmf.generate_nest`
- Span: `sem_nsmf.send_to_decision_engine` (I-01)
- Span: `sem_nsmf.send_to_ml_nsmf` (I-02)

### 6.3 Logs Estruturados

Logs estruturados incluem:
- `intent_id`: Identificador do intent
- `nest_id`: Identificador do NEST gerado
- `processing_time`: Tempo de processamento
- `validation_status`: Status da validação semântica

---

## 7. Limitações Conhecidas

### 7.1 Processamento NLP

- **Limitação**: Processamento de linguagem natural é limitado a português brasileiro e inglês
- **Impacto**: Intents em outros idiomas podem não ser processados corretamente
- **Mitigação**: Usar formato estruturado quando possível

### 7.2 Validação Semântica

- **Limitação**: Validação depende da completude da ontologia OWL
- **Impacto**: Requisitos não cobertos pela ontologia podem não ser validados
- **Mitigação**: Manter ontologia atualizada com novos requisitos

### 7.3 Performance

- **Limitação**: Processamento semântico pode ser lento para ontologias grandes
- **Impacto**: Latência de processamento pode aumentar
- **Mitigação**: Cache de ontologia e otimização de queries

### 7.4 Persistência

- **Limitação**: PostgreSQL é ponto único de falha
- **Impacto**: Falha no banco impede persistência de intents e NESTs
- **Mitigação**: Replicação e backup automático

---

## 8. Como Ler a Documentação deste Módulo

### 8.1 Ordem Recomendada de Leitura

1. **Este README.md** — Visão geral e guia de leitura
2. **[pipeline.md](pipeline.md)** — Pipeline de processamento detalhado
3. **[ontology.md](ontology.md)** — Ontologia OWL e validação semântica
4. **[implementation.md](implementation.md)** — Detalhes de implementação

### 8.2 Documentação Adicional

- **[SEM_CSMF_COMPLETE_GUIDE.md](SEM_CSMF_COMPLETE_GUIDE.md)** — Guia completo (referência)
- **[ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)** — Guia completo da ontologia
- **[../ARCHITECTURE.md](../ARCHITECTURE.md)** — Arquitetura geral do TriSLA

### 8.3 Links para Outros Módulos

- **[ML-NSMF](../ml-nsmf/README.md)** — Módulo de predição ML (recebe NEST via I-02)
- **[Decision Engine](../../apps/decision-engine/README.md)** — Motor de decisão (recebe metadados via I-01)
- **[BC-NSSMF](../bc-nssmf/README.md)** — Módulo de blockchain

---

**Última atualização:** 2025-01-27  
**Versão:** S4.0
