# Implementação — Portal

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `trisla-portal/docs/DEPLOY_GUIDE.md`, `trisla-portal/docs/TEST_GUIDE.md`, `trisla-portal/docs/MANUAL_USUARIO.md`

---

## 📋 Sumário

1. [Deploy](#deploy)
2. [Configuração](#configuração)
3. [Testes](#testes)
4. [Uso](#uso)

---

## Deploy

### Deploy Local

**Comando:**
```bash
cd trisla-portal
npm install
npm run dev
```

### Deploy NASP

**Comando:**
```bash
helm install trisla-portal ./helm/trisla-portal
```

**Documentação Completa:** `trisla-portal/docs/DEPLOY_GUIDE.md`

---

## Configuração

### Variáveis de Ambiente

```bash
# Backend API
API_URL=http://localhost:8080
NASP_ADAPTER_URL=http://nasp-adapter:8080

# Observability
PROMETHEUS_URL=http://prometheus:9090
LOKI_URL=http://loki:3100
TEMPO_URL=http://tempo:3200
```

---

## Testes

### Testes Unitários

```bash
cd trisla-portal
npm test
```

### Testes E2E

```bash
npm run test:e2e
```

**Documentação Completa:** `trisla-portal/docs/TEST_GUIDE.md`

---

## Uso

### Manual do Usuário

**Documentação Completa:** `trisla-portal/docs/MANUAL_USUARIO.md`

### Principais Funcionalidades

1. **Dashboards**: Visualização de métricas em tempo real
2. **XAI**: Visualização de explicações de predições
3. **SLA Management**: Gerenciamento de contratos SLA
4. **PLN**: Criação de SLAs via linguagem natural
5. **Batch SLA**: Criação em massa de SLAs

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `trisla-portal/docs/DEPLOY_GUIDE.md` — Guia de deploy
- `trisla-portal/docs/TEST_GUIDE.md` — Guia de testes
- `trisla-portal/docs/MANUAL_USUARIO.md` — Manual do usuário

**Última atualização:** 2025-01-27  
**Versão:** S4.0

