# TriSLA Decision Engine

Motor de decisão central da arquitetura TriSLA que orquestra respostas dos módulos SEM-, ML- e BC- conforme especificado na FASE 4 da dissertação.

## 🎯 Visão Geral

O **Decision Engine** é o componente central da arquitetura TriSLA responsável por:

- **Orquestrar respostas** dos módulos SEM-NSMF, ML-NSMF e BC-NSSMF
- **Aplicar políticas SLA-aware** para tomada de decisões
- **Implementar Closed Loop** de decisão automatizada
- **Gerenciar ciclo de vida** de slices 5G/O-RAN

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SEM-NSMF      │    │   ML-NSMF       │    │   BC-NSSMF      │
│  (Semantic)     │    │   (AI/ML)       │    │  (Blockchain)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DECISION ENGINE                             │
│  • Políticas SLA-aware                                        │
│  • Orquestração de módulos                                    │
│  • Closed Loop automatizado                                   │
│  • Interface I-02 (ML-NSMF)                                   │
│  • Interface I-06 (NASP API)                                  │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   NASP API      │
│  (Ativação)     │
└─────────────────┘
```

## 🚀 Funcionalidades

### **1. Tomada de Decisões**
- Aplicação de políticas SLA-aware
- Orquestração de análises dos módulos
- Decisões: ACCEPT, REJECT, RENEGOTIATE

### **2. Políticas Configuráveis**
- URLLC: Latência crítica (< 10ms)
- eMBB: Alta largura de banda (≥ 1 Gbps)
- mMTC: Conexões massivas (≥ 10.000)
- Validação de recursos e blockchain

### **3. Interfaces Implementadas**
- **I-02**: ML-NSMF → Decision Engine (gRPC)
- **I-06**: Decision Engine ↔ NASP API (REST)

### **4. Closed Loop**
- Ciclo contínuo: Requisição → Análise → Decisão → Execução → Observação → Ajuste
- Monitoramento automático de violações SLA
- Ações corretivas automáticas

## 📡 APIs Disponíveis

### **Health Check**
```bash
GET /api/v1/health
```

### **Tomada de Decisão**
```bash
POST /api/v1/decide
Content-Type: application/json

{
  "slice_id": "slice-001",
  "requirements": {
    "latency": 10,
    "reliability": 99.9,
    "bandwidth": 100
  }
}
```

### **Histórico de Decisões**
```bash
GET /api/v1/history?limit=100
```

### **Políticas**
```bash
GET /api/v1/policies
POST /api/v1/policies
```

## 🔧 Configuração

### **Variáveis de Ambiente**
```bash
# Portas
DECISION_ENGINE_PORT=8080
GRPC_PORT=50051

# Módulos
SEM_NSMF_URL=http://sem-nsmf:8080
ML_NSMF_URL=http://ml-nsmf:8080
BC_NSSMF_URL=http://bc-nssmf:8080
NASP_API_URL=http://nasp-api:8080

# Logging
LOG_LEVEL=INFO
```

### **Políticas SLA-Aware**
```python
# Exemplo de política personalizada
PolicyRule(
    name="Custom_Policy",
    condition="requirements.latency <= 5 and requirements.reliability >= 99.99",
    action=DecisionStatus.ACCEPT,
    priority=1,
    description="Política para aplicações críticas"
)
```

## 🚀 Deploy

### **Docker**
```bash
# Build da imagem
docker build -t ghcr.io/abelisboa/trisla-decision-engine:latest .

# Executar container
docker run -p 8080:8080 -p 50051:50051 \
  -e SEM_NSMF_URL=http://sem-nsmf:8080 \
  -e ML_NSMF_URL=http://ml-nsmf:8080 \
  -e BC_NSSMF_URL=http://bc-nssmf:8080 \
  -e NASP_API_URL=http://nasp-api:8080 \
  ghcr.io/abelisboa/trisla-decision-engine:latest
```

### **Kubernetes/Helm**
```bash
# Deploy com Helm
helm install decision-engine ./helm/decision-engine \
  --namespace trisla-nsp \
  --values ./helm/decision-engine/values.yaml

# Verificar status
kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=decision-engine
```

## 🧪 Testes

### **Teste Automatizado**
```bash
# Executar script de teste
./scripts/test_decision_engine.sh
```

### **Teste Manual**
```bash
# Health check
curl http://localhost:8080/api/v1/health

# Teste de decisão URLLC
curl -X POST http://localhost:8080/api/v1/decide \
  -H "Content-Type: application/json" \
  -d '{
    "slice_id": "test-urllc",
    "requirements": {
      "latency": 10,
      "reliability": 99.9
    }
  }'
```

## 📊 Monitoramento

### **Métricas Prometheus**
- `decision_engine_requests_total`
- `decision_engine_decisions_total`
- `decision_engine_policy_evaluations_total`
- `decision_engine_response_time_seconds`

### **Logs Estruturados**
```json
{
  "timestamp": "2025-10-29T18:00:00Z",
  "level": "INFO",
  "module": "decision_engine",
  "slice_id": "slice-001",
  "decision": "ACCEPT",
  "confidence": 0.95,
  "policy": "URLLC_Latency_Critical"
}
```

## 🔗 Integração

### **Com Módulos TriSLA**
- **SEM-NSMF**: Análise semântica de requisitos
- **ML-NSMF**: Predições de viabilidade SLA
- **BC-NSSMF**: Validação contratual

### **Com NASP**
- Ativação de slices
- Ajustes de configuração
- Monitoramento de status

## 📚 Referências

- [TriSLA Architecture](https://github.com/abelisboa/TriSLA-Portal)
- [Dissertação - Capítulo 4](docs/Referencia_Tecnica_TriSLA.md)
- [Interfaces I-02, I-06](docs/Referencia_Tecnica_TriSLA.md#a-interfaces-internas-i-)

## 👥 Autores

- **Abel Lisboa** - *Desenvolvimento* - [@abelisboa](https://github.com/abelisboa)
- **NASP-UNISINOS** - *Infraestrutura*

---

**TriSLA Decision Engine** - Motor de Decisão Central para Redes 5G/O-RAN 🧠
