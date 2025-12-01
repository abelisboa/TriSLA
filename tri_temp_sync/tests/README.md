# Testes TriSLA

Suite completa de testes para o TriSLA.

## Estrutura

```
tests/
├── unit/              # Testes unitários
├── integration/       # Testes de integração
├── e2e/              # Testes end-to-end
├── conftest.py       # Configuração pytest
└── pytest.ini        # Configuração pytest
```

## Executar Testes

### Unit Tests
```bash
pytest tests/unit/ -v
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### E2E Tests
```bash
pytest tests/e2e/ -v
```

### Todos os Testes
```bash
pytest tests/ -v --cov=apps
```

## Cobertura

Meta: > 80% de cobertura de código

```bash
pytest tests/ --cov=apps --cov-report=html
```

