# README - Módulo Semântico (SEM-CSMF)

**TriSLA – Semantic Communication Service Management Function**

---

## 🎯 Função do Módulo

O **SEM-CSMF** é responsável por:

1. **Receber intenções** de serviço em linguagem natural ou JSON
2. **Processar semanticamente** utilizando ontologia OWL
3. **Gerar NEST** (Network Slice Template) conforme 3GPP TS 28.541
4. **Enviar NEST e metadados** ao Decision Engine via interface I-01

---

## 📥 Entradas

### 1. Intenções de Serviço

**Formato 1: Linguagem Natural**
```
"Preciso de um slice URLLC com latência máxima de 10ms, 
confiabilidade de 99.999% e cobertura urbana"
```

**Formato 2: JSON Estruturado**
```json
{
  "sliceType": "URLLC",
  "requirements": {
    "latency": {"max": 10, "unit": "ms"},
    "reliability": 0.99999,
    "coverage": "urban"
  }
}
```

### 2. Tipos de Slice Suportados

- **eMBB** (Enhanced Mobile Broadband)
- **URLLC** (Ultra-Reliable Low-Latency Communications)
- **mMTC** (massive Machine-Type Communications)

---

## 📤 Saídas

### 1. NEST (Network Slice Template)

```json
{
  "nestId": "nest-urllc-001",
  "sliceType": "URLLC",
  "gst": {
    "sst": 2,
    "sd": "urllc-001"
  },
  "subsets": {
    "ran": {...},
    "transport": {...},
    "core": {...}
  },
  "qosProfile": {...}
}
```

### 2. Metadados

```json
{
  "intent_id": "intent-001",
  "tenant_id": "tenant-001",
  "processing_time": 0.5,
  "ontology_version": "1.0",
  "reasoning_applied": true
}
```

---

## 🔗 Integrações

### Interface I-01 (gRPC)

**Endpoint:** `SEMCSMFService.ProcessIntent`

**Fluxo:**
1. SEM-CSMF recebe intenção
2. Processa semanticamente
3. Gera NEST
4. Envia NEST + Metadados ao Decision Engine via I-01

---

## 🎯 Responsabilidades

1. **Validação semântica** de intenções
2. **Mapeamento** para ontologia OWL
3. **Reasoning** para inferir requisitos implícitos
4. **Geração de NEST** conforme 3GPP
5. **Persistência** de intenções e NESTs
6. **Observabilidade** (métricas, traces, logs)

---

## 🔄 Relação com Decision Engine

O SEM-CSMF é **provedor de dados** para o Decision Engine:

- **Envia:** NEST + Metadados via I-01 (gRPC)
- **Não recebe:** Decisões do Decision Engine
- **Relação:** Unidirecional (SEM-CSMF → Decision Engine)

---

## 📋 Requisitos Técnicos

### Tecnologias

- **Python 3.12+**
- **FastAPI** - Framework web
- **RDFLib / OWLReady2** - Manipulação de ontologia
- **spaCy / NLTK** - Processamento de linguagem natural
- **PostgreSQL** - Persistência
- **gRPC** - Interface I-01
- **OTLP** - Observabilidade

### Dependências

- **1_INFRA** - Infraestrutura base (PostgreSQL, Kafka, gRPC)
- **Ontologia OWL** - Arquivo `.owl` desenvolvido em Protégé

---

## 📚 Referências à Dissertação

- **Capítulo 4** - Arquitetura e Design
- **Capítulo 5** - Implementação e Validação
- **3GPP TS 28.541** - Network Resource Model

---

## ✔ Módulo Completo e Documentado

