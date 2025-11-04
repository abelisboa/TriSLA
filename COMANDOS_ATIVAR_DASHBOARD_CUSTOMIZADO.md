# 🚀 Ativar Dashboard Customizado TriSLA (Sem Grafana)

## ✅ O Que Foi Criado

1. **Backend API** - Conexão direta ao Prometheus
2. **Dashboard Completo** - Gráficos e métricas em tempo real
3. **Gestão de Slices** - Criar slices via LNP e Templates

---

## 🔧 Como Ativar

### 1. Verificar Arquivos Criados

```bash
# No node1
cd ~/gtp5g/trisla-portal

# Verificar backend
ls apps/api/prometheus.py
ls apps/api/main.py | grep -A 5 "prometheus"

# Verificar frontend
ls apps/ui/src/pages/DashboardComplete.jsx
ls apps/ui/src/pages/SlicesManagement.jsx
ls apps/ui/src/App.jsx | grep -A 5 "DashboardComplete"
```

### 2. Se arquivos não estiverem no node1

**Opção A: Copiar do repositório local**
- Os arquivos foram criados localmente
- Copiar para node1 via Git, USB, ou criar manualmente

**Opção B: Criar diretamente no node1**
- Usar `cat` ou editor para criar os arquivos

### 3. Instalar Dependências (se necessário)

```bash
# No node1 - Backend
cd apps/api
pip install httpx  # Se não estiver instalado

# Frontend - já deve ter recharts
cd ../ui
npm install recharts  # Se não estiver instalado
```

### 4. Reiniciar Services

```bash
# No node1
# Se usando Docker Compose
docker compose restart api ui

# Se usando Kubernetes
kubectl rollout restart deployment/trisla-portal-api -n trisla
kubectl rollout restart deployment/trisla-portal-ui -n trisla

# Verificar logs
kubectl logs -f deployment/trisla-portal-api -n trisla | grep prometheus
```

### 5. Verificar API Funcionando

```bash
# No node1
curl http://localhost:8000/prometheus/health
curl http://localhost:8000/prometheus/metrics/slices
```

### 6. Acessar Dashboard

- **Dashboard Completo**: http://192.168.10.16:30173/dashboard-complete
- **Gestão de Slices**: http://192.168.10.16:30173/slices
- **API Prometheus**: http://192.168.10.16:30800/prometheus/metrics/slices

---

## ✅ Checklist

- [ ] Arquivos criados no node1
- [ ] Router Prometheus integrado no `main.py`
- [ ] Rotas adicionadas no `App.jsx`
- [ ] Dependências instaladas (httpx, recharts)
- [ ] Services reiniciados
- [ ] API respondendo (`/prometheus/health`)
- [ ] Dashboard acessível via web

---

## 🎯 Testar Funcionalidades

### Testar API Prometheus:

```bash
# Health check
curl http://localhost:8000/prometheus/health

# Métricas de slices
curl http://localhost:8000/prometheus/metrics/slices | jq .

# Métricas do sistema
curl http://localhost:8000/prometheus/metrics/system | jq .
```

### Testar Dashboard Web:

1. Acessar: http://192.168.10.16:30173/dashboard-complete
2. Verificar se gráficos aparecem
3. Testar refresh automático
4. Criar slice via: http://192.168.10.16:30173/slices

---

## 💡 Vantagens

- ✅ **Sem Grafana** - Não precisa instalar/configurar
- ✅ **Sem Login Separado** - Usa autenticação do TriSLA Portal
- ✅ **Totalmente Integrado** - Parte do TriSLA Portal
- ✅ **Customizável** - Código aberto, pode modificar
- ✅ **Tempo Real** - Métricas atualizadas automaticamente

---

## 📚 Documentação Completa

Ver: `docs/DASHBOARD_CUSTOMIZADO_TRISLA.md`

---

**Pronto!** Dashboard customizado criado e integrado ao TriSLA Portal! 🎉




