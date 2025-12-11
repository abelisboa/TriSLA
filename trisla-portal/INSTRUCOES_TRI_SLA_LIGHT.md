# 🚀 TRI-SLA LIGHT - Instruções de Execução

## ✅ PATCH APLICADO

A versão leve (TRI-SLA LIGHT) foi implementada com sucesso.

---

## 📋 QUICK START

### 1. Reconstruir Backend

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend

rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Tempo estimado**: 30-60 segundos (apenas 7 dependências!)

---

### 2. Validar Backend

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend
source venv/bin/activate

# Verificar que não há OpenTelemetry
python3 -c "
try:
    import opentelemetry
    print('❌ OpenTelemetry ainda instalado')
except ImportError:
    print('✅ OpenTelemetry não instalado (correto)')
"

# Verificar importação
python3 -c "from src.main import app; print('✅ Backend OK')"
```

---

### 3. Iniciar Portal

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean
bash scripts/portal_manager.sh
```

**Menu**:
- Opção 1: Iniciar Backend (DEV)
- Opção 2: Iniciar Frontend

---

### 4. Testar Rotas

```bash
# Health Check
curl http://127.0.0.1:8001/health

# Interpret SLA
curl -X POST http://127.0.0.1:8001/api/v1/sla/interpret \
  -H "Content-Type: application/json" \
  -d '{"intent_text": "Slice URLLC com latência 10ms", "tenant_id": "tenant-001"}'
```

---

## 📊 Estrutura Simplificada

### Backend
- ✅ Apenas 4 rotas essenciais
- ✅ 7 dependências mínimas
- ✅ Comunicação direta com NASP via HTTPX
- ✅ Sem banco de dados local
- ✅ Sem filas/cache
- ✅ Sem telemetria

### Frontend
- ✅ 3 páginas essenciais
- ✅ Menu simplificado
- ✅ Gráficos com Recharts
- ✅ Interface limpa e focada

---

## 🎯 Rotas Disponíveis

1. `POST /api/v1/sla/interpret` - Criar SLA via PLN
2. `POST /api/v1/sla/submit` - Criar SLA via Template
3. `GET /api/v1/sla/status/{id}` - Status do SLA
4. `GET /api/v1/sla/metrics/{id}` - Métricas do SLA

---

**✅ TRI-SLA LIGHT PRONTO PARA USO!**

