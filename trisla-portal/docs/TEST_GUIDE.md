# Guia de Testes - TriSLA Observability Portal v4.0

**Versão:** 4.0  
**Data:** 2025-01-XX

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Testes Unitários](#testes-unitários)
3. [Testes de Integração](#testes-de-integração)
4. [Testes E2E](#testes-e2e)
5. [Testes de Carga](#testes-de-carga)
6. [Cobertura](#cobertura)

---

## 🎯 Visão Geral

O TriSLA Observability Portal v4.0 possui uma suíte completa de testes:

- **Unit Tests**: Validação de schemas e lógica isolada
- **Integration Tests**: Testes de API e banco de dados
- **E2E Tests**: Fluxos completos do usuário
- **Load Tests**: Testes de performance

---

## 🧪 Testes Unitários

### Executar

```bash
cd trisla-portal/tests
pytest tests/unit/ -v
```

### Cobertura

```bash
pytest tests/unit/ --cov=backend/src/schemas --cov-report=html
```

### Exemplos

- Validação de schemas Pydantic
- Validação de enums
- Validação de tipos

---

## 🔗 Testes de Integração

### Executar

```bash
# Todos os testes de integração
pytest tests/integration/ -v

# Testes específicos
pytest tests/integration/test_contracts_api.py -v
pytest tests/integration/test_xai_api.py -v
pytest tests/integration/test_batch_sla.py -v
```

### Pré-requisitos

- Backend rodando (porta 8000)
- Banco de dados acessível
- Serviços externos disponíveis (opcional)

### Exemplos

- CRUD de contratos
- Criação de SLAs
- Geração de explicações XAI
- Batch SLA creation

---

## 🎭 Testes E2E

### Executar

```bash
# Iniciar aplicação primeiro
# Terminal 1: Backend
cd backend
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Testes
cd tests
pytest tests/e2e/ -v
```

### Pré-requisitos

- Frontend rodando (porta 3000)
- Backend rodando (porta 8000)
- Playwright instalado: `playwright install chromium`

### Exemplos

- Navegação entre páginas
- Criação de SLA via PLN
- Visualização de contratos
- XAI Viewer

---

## 📊 Testes de Carga

### Executar

```bash
cd tests/load

# Teste básico
k6 run k6_script.js

# Com URL customizada
k6 run --env BASE_URL=http://localhost:8000 k6_script.js

# Com mais usuários
k6 run --vus 100 --duration 5m k6_script.js
```

### Cenários

1. **Ramp Up**: Aumento gradual de carga
2. **Sustained Load**: Carga constante
3. **Spike Test**: Picos de tráfego
4. **Stress Test**: Teste de limites

### Thresholds

- **Latência P95**: < 500ms
- **Taxa de Erro**: < 10%

---

## 📈 Cobertura

### Gerar Relatório

```bash
pytest --cov=backend/src --cov-report=html --cov-report=term-missing
```

### Abrir Relatório

```bash
# Abrir htmlcov/index.html no navegador
```

### Meta de Cobertura

- **Schemas**: 100%
- **Services**: > 80%
- **Routers**: > 70%
- **Models**: > 80%

---

## 🎯 Testes Específicos

### Testes XAI

```bash
pytest -m xai -v
```

Valida:
- Estrutura de explicações
- Valores numéricos válidos
- Métodos (SHAP, LIME, fallback)

### Testes Batch

```bash
pytest -m batch -v
```

Valida:
- Processamento CSV
- Processamento JSON
- Batch com > 100 intents

### Testes Contratos

```bash
pytest -m contracts -v
```

Valida:
- CRUD completo
- Violações
- Renegociações
- Penalidades

---

## ✅ Conclusão

O guia de testes do TriSLA Observability Portal v4.0 fornece:

- **Testes unitários** para validação de schemas
- **Testes de integração** para APIs
- **Testes E2E** para fluxos completos
- **Testes de carga** para performance
- **Cobertura** de código

---

**Status:** ✅ **GUIA DE TESTES DOCUMENTADO**







