# README - Integração NASP

**TriSLA – Adaptador para Integração com NASP (Network Automation Service Platform)**

---

## 🎯 Função do Módulo

O **NASP Adapter** é responsável por:

1. **Receber comandos** do Decision Engine via interface I-07
2. **Conectar a serviços reais** do NASP (RAN, Transport, Core)
3. **Provisionar slices** na infraestrutura real
4. **Coletar métricas reais** do NASP
5. **Executar ações reais** nos domínios da rede

---

## 📥 Entradas

### 1. Comando do Decision Engine (I-07)

```json
{
  "command": "PROVISION_SLICE",
  "nest_id": "nest-urllc-001",
  "sla_data": {
    "tenant_id": "tenant-001",
    "slice_type": "URLLC",
    "requirements": {...}
  }
}
```

### 2. Requisições de Métricas

```json
{
  "request_type": "GET_METRICS",
  "domain": "RAN",
  "time_range": {
    "start": "2025-01-19T10:00:00Z",
    "end": "2025-01-19T10:30:00Z"
  }
}
```

---

## 📤 Saídas

### 1. Confirmação de Provisionamento

```json
{
  "status": "SUCCESS",
  "slice_id": "slice-001",
  "provisioned_at": "2025-01-19T10:30:00Z",
  "resources": {
    "ran": {...},
    "transport": {...},
    "core": {...}
  }
}
```

### 2. Métricas do NASP

```json
{
  "domain": "RAN",
  "metrics": {
    "cpu_utilization": 0.65,
    "memory_utilization": 0.70,
    "prb_utilization": 0.45,
    "active_slices": 15
  },
  "timestamp": "2025-01-19T10:30:00Z"
}
```

---

## 🔗 Integrações

### Interface I-07 (REST)

**Endpoint:** `POST /nasp-adapter/provision`

**Fluxo:**
1. Decision Engine envia comando via I-07
2. NASP Adapter conecta a serviços reais do NASP
3. NASP Adapter provisiona slice
4. NASP Adapter retorna confirmação

### Integração com NASP Real

**Domínios:**
- **RAN** - Radio Access Network
- **Transport** - Transport Network
- **Core** - Core Network

**Serviços:**
- Controllers de cada domínio
- APIs REST do NASP
- Autenticação real

---

## 🎯 Responsabilidades

1. **Conectividade** com serviços reais do NASP
2. **Provisionamento** de slices na infraestrutura real
3. **Coleta de métricas** reais dos domínios
4. **Execução de ações** reais (configurações, políticas)
5. **Validação** de produção real (não simulação)
6. **Observabilidade** (métricas, traces, logs)

---

## 🔄 Relação com Decision Engine

O NASP Adapter é **executor de ações** do Decision Engine:

- **Recebe:** Comandos via I-07
- **Executa:** Ações reais no NASP
- **Retorna:** Confirmação e métricas
- **Relação:** Bidirecional (Decision Engine ↔ NASP Adapter)

---

## 📋 Requisitos Técnicos

### Tecnologias

- **Python 3.12+**
- **FastAPI** - Framework web
- **HTTP Client** - Comunicação com NASP
- **Autenticação** - JWT, OAuth2, mTLS
- **OTLP** - Observabilidade

### Dependências

- **Decision Engine** - Recebe comandos via I-07
- **1_INFRA** - Conectividade com NASP
- **NASP Real** - Serviços reais (RAN, Transport, Core)

### Configuração

- **Endpoints reais** do NASP
- **Credenciais** de autenticação
- **Flags de produção** (não simulação)

---

## 📚 Referências à Dissertação

- **Capítulo 4** - Arquitetura e Design
- **Capítulo 5** - Implementação e Validação
- **Integração Real** - Conectividade com NASP
- **Produção Real** - Não usar mocks ou simulações

---

## ⚠️ Importante

**O NASP Adapter deve conectar a SERVIÇOS REAIS do NASP:**

- ✅ **NÃO usar mocks** em produção
- ✅ **NÃO usar stubs** em produção
- ✅ **NÃO simular** ações em produção
- ✅ **Validar** que está em modo produção real
- ✅ **Alertar** se detectar modo simulação

---

## ✔ Módulo Completo e Documentado

