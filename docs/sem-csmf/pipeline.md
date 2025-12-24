# Pipeline de Processamento — SEM-NSMF

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `SEM_CSMF_COMPLETE_GUIDE.md` (seções Pipeline de Processamento, NLP, Geração de NEST)

---

## 📋 Sumário

1. [Visão Geral do Pipeline](#visão-geral-do-pipeline)
2. [Etapas Detalhadas](#etapas-detalhadas)
3. [Processamento NLP](#processamento-nlp)
4. [Geração de NEST](#geração-de-nest)
5. [Fluxo de Dados](#fluxo-de-dados)

---

## Visão Geral do Pipeline

O pipeline de processamento do SEM-NSMF transforma intents de alto nível (linguagem natural ou estruturado) em Network Slice Templates (NEST) validados semanticamente, prontos para análise de viabilidade e decisão.

### Fluxo Completo

```
┌─────────────────┐
│  Intent Recebido│  (HTTP REST ou gRPC)
│  (Linguagem     │
│   Natural ou    │
│   Estruturado)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NLP Parser     │  (Extrai tipo de slice e requisitos)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ontology       │  (Valida semanticamente)
│  Parser         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Semantic       │  (Match semântico)
│  Matcher        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NEST Generator │  (Gera Network Slice Template)
└────────┬────────┘
         │
         ├───► I-01 (gRPC) ──► Decision Engine
         │
         └───► I-02 (Kafka) ──► ML-NSMF
```

### Tempo de Processamento

- **Total**: ~2-5 segundos (p95)
- **NLP**: ~200-500ms (se linguagem natural)
- **Validação Semântica**: ~500ms-1s
- **Geração de NEST**: ~200-300ms
- **Envio (I-01 + I-02)**: ~100-200ms

---

## Etapas Detalhadas

### Etapa 1: Recepção de Intent

**Entrada:**
- HTTP REST: `POST /api/v1/intents`
- gRPC: `ProcessIntent`

**Validação:**
- Formato JSON válido
- Campos obrigatórios presentes
- Tipos de dados corretos

**Saída:**
- Intent validado (formato estruturado)
- Metadados (tenant_id, timestamp, etc.)

### Etapa 2: Processamento NLP (Condicional)

**Quando executado:**
- Intent em linguagem natural (texto livre)
- Intent parcialmente estruturado

**Processo:**
1. **Extração de Tipo de Slice**
   - Identifica eMBB, URLLC, mMTC
   - Usa heurísticas e spaCy
   - Fallback para padrão (eMBB)

2. **Extração de Requisitos SLA**
   - Latência (ex: "10ms", "menos de 10ms")
   - Throughput (ex: "100Mbps", "pelo menos 100Mbps")
   - Confiabilidade (ex: "99.999%", "cinco noves")
   - Jitter (ex: "2ms", "máximo 2ms")
   - Perda de pacotes (ex: "0.1%", "menos de 0.1%")

3. **Normalização de Dados**
   - Conversão de unidades
   - Validação de valores
   - Padronização de formato

**Exemplo:**
```python
from nlp.parser import NLPParser

parser = NLPParser()
text = "Preciso de um slice URLLC com latência máxima de 10ms"
result = parser.parse_intent_text(text)

# Resultado:
# {
#   "slice_type": "URLLC",
#   "requirements": {"latency": "10ms"}
# }
```

### Etapa 3: Validação Semântica

**Processo:**
1. **Carregamento da Ontologia OWL**
   - Carrega `trisla.ttl`
   - Aplica reasoning (Pellet)
   - Cache de ontologia (se disponível)

2. **Validação contra Classes e Propriedades**
   - Verifica se tipo de slice existe na ontologia
   - Valida requisitos de SLA contra propriedades
   - Verifica consistência semântica

3. **Reasoning Semântico**
   - Infere propriedades implícitas
   - Detecta inconsistências
   - Valida restrições (cardinalidade, domínio, range)

**Exemplo:**
```python
from ontology.loader import OntologyLoader
from ontology.reasoner import SemanticReasoner

loader = OntologyLoader()
loader.load(apply_reasoning=True)

reasoner = SemanticReasoner(loader)
reasoner.initialize()

sla_dict = {"latency": "10ms", "throughput": "100Mbps"}
is_valid = reasoner.validate_sla_requirements("URLLC", sla_dict)
```

### Etapa 4: Geração de NEST

**Processo:**
1. **Conversão GST → NEST**
   - GST (Generic Slice Template) é convertido para NEST
   - Validação contra ontologia
   - Estruturação conforme especificação O-RAN

2. **Persistência**
   - Salvo em PostgreSQL
   - Metadados armazenados
   - Histórico de gerações

3. **Envio**
   - gRPC para Decision Engine (I-01)
   - Kafka para ML-NSMF (I-02)

**Estrutura de NEST:**
```json
{
  "nest_id": "nest-urllc-001",
  "intent_id": "intent-001",
  "slice_type": "URLLC",
  "sla_requirements": {
    "latency": "10ms",
    "throughput": "100Mbps",
    "reliability": 0.99999
  },
  "domains": ["RAN", "Transport", "Core"],
  "domain_config": {
    "ran": {
      "cell_density": "high",
      "mimo_layers": 4
    },
    "core": {
      "upf_location": "edge",
      "amf_pool_size": 2
    }
  },
  "created_at": "2025-01-27T10:00:00Z"
}
```

---

## Processamento NLP

### Funcionalidades

1. **Extração de Tipo de Slice**
   - Identifica eMBB, URLLC, mMTC
   - Usa heurísticas e spaCy
   - Fallback para padrão

2. **Extração de Requisitos SLA**
   - Latência
   - Throughput
   - Confiabilidade
   - Jitter
   - Perda de pacotes

### Limitações

- **Idiomas suportados**: Português brasileiro e inglês
- **Precisão**: ~85-90% para intents bem formados
- **Fallback**: Usa formato estruturado quando NLP falha

### Exemplo de Uso

```python
from nlp.parser import NLPParser

parser = NLPParser()

# Exemplo 1: URLLC
text1 = "Preciso de um slice URLLC com latência máxima de 10ms"
result1 = parser.parse_intent_text(text1)
# {"slice_type": "URLLC", "requirements": {"latency": "10ms"}}

# Exemplo 2: eMBB
text2 = "Slice para streaming de vídeo 4K, throughput mínimo de 100Mbps"
result2 = parser.parse_intent_text(text2)
# {"slice_type": "eMBB", "requirements": {"throughput": "100Mbps"}}

# Exemplo 3: mMTC
text3 = "Slice para IoT, suportar 10k dispositivos simultâneos"
result3 = parser.parse_intent_text(text3)
# {"slice_type": "mMTC", "requirements": {"device_count": "10000"}}
```

---

## Geração de NEST

### Processo de Conversão GST → NEST

1. **GST (Generic Slice Template)**
   - Template genérico extraído do intent
   - Não validado semanticamente
   - Formato interno

2. **Validação contra Ontologia**
   - Verifica se requisitos são válidos
   - Aplica restrições da ontologia
   - Infere propriedades implícitas

3. **Estruturação NEST**
   - Converte para formato O-RAN
   - Adiciona metadados
   - Configura domínios (RAN, Transport, Core)

### Mapeamento de Requisitos

| Requisito SLA | Mapeamento NEST | Domínio |
|---------------|-----------------|---------|
| Latência | `latency_ms` | RAN, Transport, Core |
| Throughput | `throughput_mbps` | RAN, Transport |
| Confiabilidade | `reliability` | RAN, Core |
| Jitter | `jitter_ms` | Transport |
| Perda de Pacotes | `packet_loss_rate` | Transport |

### Persistência

**PostgreSQL:**
- Tabela `intents`: Armazena intents originais
- Tabela `nests`: Armazena NESTs gerados
- Relacionamento: `intent_id` → `nest_id`

**Modelos:**
```python
class IntentModel(Base):
    intent_id = Column(String, primary_key=True)
    tenant_id = Column(String)
    service_type = Column(String)
    sla_requirements = Column(JSON)
    created_at = Column(DateTime)

class NESTModel(Base):
    nest_id = Column(String, primary_key=True)
    intent_id = Column(String, ForeignKey('intents.intent_id'))
    slice_type = Column(String)
    sla_requirements = Column(JSON)
    domain_config = Column(JSON)
    created_at = Column(DateTime)
```

---

## Fluxo de Dados

### Fluxo Completo com Timestamps

```
t=0ms:   Intent recebido (HTTP REST ou gRPC)
t=50ms:  Validação de formato concluída
t=250ms: Processamento NLP concluído (se necessário)
t=750ms: Validação semântica concluída
t=950ms: Geração de NEST concluída
t=1000ms: Persistência em PostgreSQL concluída
t=1050ms: Envio I-01 (gRPC) iniciado
t=1100ms: Envio I-02 (Kafka) iniciado
t=1150ms: Pipeline completo
```

### Tratamento de Erros

**Erro em NLP:**
- Fallback para formato estruturado
- Log de erro
- Continua processamento

**Erro em Validação Semântica:**
- Retorna erro ao tenant
- Log de erro
- Não gera NEST

**Erro em Geração de NEST:**
- Retorna erro ao tenant
- Log de erro
- Não persiste

**Erro em Envio (I-01 ou I-02):**
- Retry automático (3 tentativas)
- Queue de retry
- Log de erro

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `SEM_CSMF_COMPLETE_GUIDE.md` — Seções "Pipeline de Processamento", "NLP", "Geração de NEST"
- `SEM_CSMF_COMPLETE_GUIDE.md` — Seção "Interfaces" (I-01, I-02)
- `SEM_CSMF_COMPLETE_GUIDE.md` — Seção "Persistência"

**Última atualização:** 2025-01-27  
**Versão:** S4.0

