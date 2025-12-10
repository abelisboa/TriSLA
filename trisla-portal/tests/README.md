# Testes - TriSLA Observability Portal v4.0

Estrutura completa de testes para o portal.

## 📋 Estrutura

```
tests/
├── unit/              # Testes unitários
│   ├── test_contracts.py
│   └── test_xai.py
├── integration/       # Testes de integração
│   ├── test_contracts_api.py
│   ├── test_slas_api.py
│   ├── test_xai_api.py
│   └── test_batch_sla.py
├── e2e/              # Testes end-to-end
│   ├── test_portal_flow.py
│   └── test_contract_workflow.py
├── load/             # Testes de carga
│   ├── k6_script.js
│   └── README.md
├── conftest.py       # Fixtures compartilhadas
├── pytest.ini        # Configuração pytest
└── requirements.txt   # Dependências de teste
```

## 🚀 Instalação

```bash
cd tests
pip install -r requirements.txt

# Instalar Playwright browsers
playwright install chromium
```

## 🧪 Executar Testes

### Testes Unitários

```bash
pytest tests/unit/ -v
```

### Testes de Integração

```bash
pytest tests/integration/ -v
```

### Testes E2E

```bash
# Iniciar aplicação primeiro
# Frontend: npm run dev (porta 3000)
# Backend: uvicorn src.main:app (porta 8000)

pytest tests/e2e/ -v
```

### Testes Específicos

```bash
# Testes XAI
pytest -m xai -v

# Testes Batch
pytest -m batch -v

# Testes Contratos
pytest -m contracts -v
```

### Testes de Carga

```bash
cd tests/load
k6 run k6_script.js
```

## 📊 Cobertura

```bash
pytest --cov=backend/src --cov-report=html
```

Abrir `htmlcov/index.html` no navegador.

## 🎯 Tipos de Teste

### Unit Tests
- Validação de schemas Pydantic
- Lógica de negócio isolada
- Sem dependências externas

### Integration Tests
- Testes de API endpoints
- Integração com banco de dados
- Comunicação entre serviços

### E2E Tests
- Fluxos completos do usuário
- Navegação entre páginas
- Interações com UI

### Load Tests
- Testes de carga com k6
- Validação de performance
- Thresholds de latência e erro

## 📝 Notas

- Testes E2E requerem aplicação rodando
- Testes de integração podem falhar se serviços externos não estiverem disponíveis
- Testes de carga devem ser executados em ambiente isolado







