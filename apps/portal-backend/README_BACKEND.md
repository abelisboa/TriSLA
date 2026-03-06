# BACKEND TRI-SLA PORTAL LIGHT

## 🚀 INÍCIO RÁPIDO

### 1. Diagnóstico
```bash
cd trisla-portal/backend
bash diagnose_backend.sh
```

### 2. Corrigir Ambiente
```bash
bash fix_backend_env.sh
```

### 3. Iniciar Backend
```bash
bash start_backend.sh
```

### 4. Testar Rotas
```bash
bash test_backend_routes.sh
```

---

## 📋 PRÉ-REQUISITOS

- Python 3.10+
- WSL2 (para desenvolvimento local)
- Port-forwards configurados para módulos NASP (opcional, para operação completa)

---

## 🔧 CONFIGURAÇÃO

### URLs dos Módulos TriSLA (Port-Forward)
```
SEM-CSMF:          http://localhost:8080
ML-NSMF:           http://localhost:8081
Decision Engine:   http://localhost:8082
BC-NSSMF:          http://localhost:8083
SLA-Agent Layer:   http://localhost:8084
```

---

## 📁 ESTRUTURA

```
backend/
├── src/
│   ├── main.py              # Aplicação FastAPI
│   ├── config.py            # Configurações
│   ├── routers/
│   │   └── sla.py          # Rotas SLA
│   ├── services/
│   │   └── nasp.py         # Comunicação com NASP
│   └── schemas/
│       └── sla.py          # Schemas Pydantic
├── fix_backend_env.sh       # Corrigir ambiente
├── start_backend.sh         # Iniciar backend
├── test_backend_routes.sh   # Testar rotas
├── diagnose_backend.sh      # Diagnóstico
└── requirements.txt         # Dependências
```

---

## 🌐 ROTAS DISPONÍVEIS

### Health Check
- `GET /health` - Status do backend

### SLA Routes
- `POST /api/v1/sla/interpret` - Interpretação PLN
- `POST /api/v1/sla/submit` - Pipeline completo
- `GET /api/v1/sla/status/{sla_id}` - Status do SLA
- `GET /api/v1/sla/metrics/{sla_id}` - Métricas do SLA

---

## 🔄 FLUXO COMPLETO

```
POST /api/v1/sla/submit
  ↓
1. SEM-CSMF (localhost:8080)
  ↓
2. ML-NSMF (localhost:8081)
  ↓
3. Decision Engine (localhost:8082)
  ↓
4. BC-NSSMF (localhost:8083)
  ↓
5. SLA-Agent Layer (localhost:8084)
```

---

## 🐛 SOLUÇÃO DE PROBLEMAS

### ModuleNotFoundError
```bash
bash fix_backend_env.sh
```

### CRLF em arquivos Python
```bash
bash fix_line_endings.sh
```

### Backend não inicia
```bash
bash diagnose_backend.sh
```

### Ver logs
O backend exibe logs no console. Erros aparecem em vermelho.

---

## 📝 DEPENDÊNCIAS

- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- httpx==0.26.0
- pydantic==2.5.3
- pydantic-settings==2.1.0
- python-dotenv==1.0.0
- prometheus-client==0.19.0

---

*Última atualização: 2025-01-15*

