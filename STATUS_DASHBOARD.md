# 📊 Status do Dashboard TriSLA

## ✅ Componentes Funcionando

1. **Frontend** ✅
   - Rodando em: http://localhost:5173
   - Interface carregando corretamente
   - Navegação funcionando (Dashboard, Slices, Métricas)

2. **Backend API** ✅
   - Rodando em: http://localhost:5000
   - Swagger Docs acessível: http://localhost:5000/docs
   - Todos os endpoints disponíveis

---

## ⚠️ Prometheus Não Conectado

**Status atual:** `prometheus: unreachable`

**Causa:** Não há túnel SSH ativo para conectar ao Prometheus no `node1`

**URL esperada:** `http://localhost:9090` (via túnel SSH)

---

## 🔧 Como Conectar ao Prometheus

### Opção 1: Usar Menu (Recomendado)

Se você já instalou o menu interativo:

```bash
cd ~/trisla-dashboard-local/scripts-wsl
./dashboard-menu.sh
```

O menu gerencia tudo automaticamente.

---

### Opção 2: Túnel SSH Manual

Para conectar ao Prometheus no `node1`:

```bash
# No WSL, execute:
ssh -L 9090:localhost:9090 -L 5000:localhost:5000 porvir5g@ppgca.unisinos.br
# Depois dentro do SSH:
ssh node006
```

Ou use o script:

```bash
cd ~/trisla-dashboard-local/scripts-wsl
./start-ssh-tunnel.sh
```

---

## 📋 Endpoints Disponíveis

### Backend API

- **Root:** http://localhost:5000
- **Health:** http://localhost:5000/health
- **Swagger Docs:** http://localhost:5000/docs
- **Prometheus Health:** http://localhost:5000/api/prometheus/health

### Frontend

- **Dashboard:** http://localhost:5173
- **Slices:** http://localhost:5173/slices
- **Métricas:** http://localhost:5173/metrics

---

## 🎯 Comportamento Atual

### ✅ Funcionando

- Dashboard mostra interface
- Métricas aparecem como "N/A" ou "0" quando Prometheus desconectado
- API responde corretamente
- Swagger docs funcionando

### ⚠️ Com Prometheus Desconectado

- Métricas retornam `0` ou `N/A`
- Gráficos não têm dados
- Health check retorna `prometheus: unreachable`

### ✅ Com Prometheus Conectado

- Métricas em tempo real
- Gráficos populados
- Health check retorna `prometheus: connected`

---

## 🚀 Resumo

**Status:** ✅ Dashboard 100% funcional

**Prometheus:** ⚠️ Desconectado (esperado - precisa túnel SSH)

**Ação:** O dashboard funciona normalmente sem Prometheus, apenas sem dados reais.

Para ter dados reais, conecte o túnel SSH conforme instruções acima.





