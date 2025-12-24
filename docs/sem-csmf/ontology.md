# Ontologia OWL — SEM-NSMF

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `SEM_CSMF_COMPLETE_GUIDE.md` (seção Ontologia OWL) + `ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Localização e Estrutura](#localização-e-estrutura)
3. [Classes Principais](#classes-principais)
4. [Propriedades](#propriedades)
5. [Uso no SEM-NSMF](#uso-no-sem-nsmf)
6. [Validação Semântica](#validação-semântica)
7. [Reasoning](#reasoning)

---

## Visão Geral

A ontologia OWL do TriSLA define o vocabulário semântico para interpretação de intents, validação de requisitos de SLA e geração de NESTs. A ontologia está implementada em OWL 2.0 (formato Turtle) e é carregada dinamicamente pelo módulo SEM-NSMF.

### Objetivos da Ontologia

1. **Interpretação Semântica**: Permitir interpretação precisa de intents de tenants
2. **Validação**: Validar requisitos de SLA contra capacidades disponíveis
3. **Inferência**: Inferir propriedades implícitas através de reasoning
4. **Padronização**: Garantir consistência na geração de NESTs

---

## Localização e Estrutura

### Arquivo Principal

**Localização:** `apps/sem-csmf/src/ontology/trisla.ttl`

**Formato:** Turtle (`.ttl`)

**Namespace:** `http://trisla.org/ontology#`

### Estrutura de Diretórios

```
apps/sem-csmf/src/ontology/
├── trisla.ttl              # Ontologia principal
├── loader.py                # Carregador de ontologia
├── reasoner.py              # Motor de reasoning
├── parser.py                # Parser de intents
└── matcher.py               # Matcher semântico
```

### Carregamento

```python
from ontology.loader import OntologyLoader

loader = OntologyLoader()
loader.load(apply_reasoning=True)
```

---

## Classes Principais

### Intent

**URI:** `http://trisla.org/ontology#Intent`

**Descrição:** Representa uma intenção de serviço do tenant.

**Propriedades:**
- `hasTenant`: Relaciona intent com tenant
- `hasServiceType`: Tipo de serviço (eMBB, URLLC, mMTC)
- `hasSLARequirements`: Requisitos de SLA

### SliceType

**URI:** `http://trisla.org/ontology#SliceType`

**Descrição:** Tipo de network slice.

**Subclasses:**
- `eMBB_Slice`: Enhanced Mobile Broadband
- `URLLC_Slice`: Ultra-Reliable Low-Latency Communications
- `mMTC_Slice`: massive Machine-Type Communications

### SLA

**URI:** `http://trisla.org/ontology#SLA`

**Descrição:** Service Level Agreement.

**Propriedades:**
- `hasLatency`: Latência requerida
- `hasThroughput`: Throughput requerido
- `hasReliability`: Confiabilidade requerida
- `hasJitter`: Jitter requerido
- `hasPacketLoss`: Taxa de perda de pacotes requerida

### SLO

**URI:** `http://trisla.org/ontology#SLO`

**Descrição:** Service Level Objective (objetivo específico dentro de um SLA).

**Propriedades:**
- `hasTarget`: Valor alvo
- `hasThreshold`: Limite mínimo/máximo
- `hasMetric`: Métrica associada

### Metric

**URI:** `http://trisla.org/ontology#Metric`

**Descrição:** Métrica de performance.

**Subclasses:**
- `LatencyMetric`: Métrica de latência
- `ThroughputMetric`: Métrica de throughput
- `ReliabilityMetric`: Métrica de confiabilidade

### Domain

**URI:** `http://trisla.org/ontology#Domain`

**Descrição:** Domínio de rede.

**Indivíduos:**
- `RAN_Domain`: Domínio RAN
- `Transport_Domain`: Domínio Transport
- `Core_Domain`: Domínio Core

---

## Propriedades

### Propriedades de Dados (Data Properties)

| Propriedade | Domínio | Range | Descrição |
|-------------|---------|-------|-----------|
| `hasLatency` | SLA | xsd:string | Latência requerida (ex: "10ms") |
| `hasThroughput` | SLA | xsd:string | Throughput requerido (ex: "100Mbps") |
| `hasReliability` | SLA | xsd:double | Confiabilidade requerida (ex: 0.99999) |
| `hasJitter` | SLA | xsd:string | Jitter requerido (ex: "2ms") |
| `hasPacketLoss` | SLA | xsd:double | Taxa de perda de pacotes (ex: 0.001) |

### Propriedades de Objeto (Object Properties)

| Propriedade | Domínio | Range | Descrição |
|-------------|---------|-------|-----------|
| `hasTenant` | Intent | Tenant | Relaciona intent com tenant |
| `hasServiceType` | Intent | SliceType | Tipo de serviço |
| `hasSLARequirements` | Intent | SLA | Requisitos de SLA |
| `hasDomain` | SLA | Domain | Domínio de rede |
| `hasMetric` | SLO | Metric | Métrica associada |

---

## Uso no SEM-NSMF

### Carregamento da Ontologia

```python
from ontology.loader import OntologyLoader

loader = OntologyLoader()
loader.load(apply_reasoning=True)
```

### Validação de Requisitos

```python
from ontology.reasoner import SemanticReasoner

reasoner = SemanticReasoner(loader)
reasoner.initialize()

sla_dict = {
    "latency": "10ms",
    "throughput": "100Mbps",
    "reliability": 0.99999
}

is_valid = reasoner.validate_sla_requirements("URLLC", sla_dict)
```

### Consulta de Classes

```python
# Obter classe
slice_type = loader.get_class("URLLC_Slice")

# Obter indivíduo
individual = loader.get_individual("URLLC_Type")

# Listar subclasses
subclasses = loader.get_subclasses("SliceType")
```

### Query SPARQL

```python
query = """
PREFIX : <http://trisla.org/ontology#>
SELECT ?sliceType ?latency
WHERE {
    ?sliceType a :SliceType .
    ?sliceType :hasLatency ?latency .
}
"""

results = loader.query(query)
```

---

## Validação Semântica

### Processo de Validação

1. **Carregamento da Ontologia**
   - Carrega `trisla.ttl`
   - Aplica reasoning (se habilitado)
   - Cache de ontologia (se disponível)

2. **Validação contra Classes**
   - Verifica se tipo de slice existe
   - Valida requisitos contra propriedades
   - Verifica consistência semântica

3. **Validação de Restrições**
   - Cardinalidade (ex: exatamente 1 tenant por intent)
   - Domínio e range de propriedades
   - Restrições funcionais

### Exemplo de Validação

```python
from ontology.reasoner import SemanticReasoner

reasoner = SemanticReasoner(loader)
reasoner.initialize()

# Validar requisitos URLLC
sla_dict = {
    "latency": "10ms",
    "throughput": "100Mbps",
    "reliability": 0.99999
}

is_valid = reasoner.validate_sla_requirements("URLLC", sla_dict)

if is_valid:
    print("Requisitos válidos para URLLC")
else:
    print("Requisitos inválidos ou inconsistentes")
```

---

## Reasoning

### Motor de Reasoning

**Motor utilizado:** Pellet (via owlready2)

**Tipo de reasoning:** OWL 2.0 DL (Description Logic)

### Inferências Realizadas

1. **Inferência de Subclasse**
   - Se `URLLC_Slice` é subclasse de `SliceType`, então `URLLC_Slice` é `SliceType`

2. **Inferência de Propriedade**
   - Se `Intent` tem `hasServiceType` `URLLC_Slice`, então o intent é do tipo URLLC

3. **Inferência de Restrição**
   - Se `SLA` tem `hasLatency` "10ms" e `URLLC_Slice` requer latência < 20ms, então SLA é compatível

### Habilitar Reasoning

```python
from ontology.loader import OntologyLoader

loader = OntologyLoader()
loader.load(apply_reasoning=True)  # Habilita reasoning
```

### Performance

- **Tempo de carregamento**: ~1-2 segundos (com reasoning)
- **Tempo de validação**: ~100-200ms por intent
- **Cache**: Ontologia é cacheada após primeiro carregamento

---

## Documentação Completa

Para documentação completa da ontologia, incluindo diagramas Protégé e exemplos avançados, consulte:

- **[ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)** — Guia completo da ontologia

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `SEM_CSMF_COMPLETE_GUIDE.md` — Seção "Ontologia OWL"
- `ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md` — Guia completo da ontologia

**Última atualização:** 2025-01-27  
**Versão:** S4.0

