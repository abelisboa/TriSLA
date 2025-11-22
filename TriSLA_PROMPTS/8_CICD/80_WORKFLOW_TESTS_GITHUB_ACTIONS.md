# 80 – GitHub Actions Workflow para Testes TriSLA  

**Integração contínua para SEM / ML / DE / BC / TESTS**

---

## 🎯 Objetivo Geral

Implementar **workflows completos do GitHub Actions** para automatizar:

- **Testes unitários** de todos os módulos
- **Testes de integração** entre módulos
- **Testes E2E** do fluxo completo
- **Testes de segurança** (SAST, DAST)
- **Testes de carga** (load, stress)
- **Build e push** de imagens Docker para GHCR
- **Quality gates** antes de merge
- **Notificações** de status

---

## 📋 Workflows a Implementar

### 1. Workflow de Testes Unitários

**Arquivo:** `.github/workflows/unit-tests.yml`

- Executar testes unitários de todos os módulos
- Gerar relatórios de cobertura
- Falhar build se cobertura < 80%

### 2. Workflow de Testes de Integração

**Arquivo:** `.github/workflows/integration-tests.yml`

- Executar testes de integração
- Validar comunicação entre módulos
- Testar interfaces I-01 a I-07

### 3. Workflow de Testes E2E

**Arquivo:** `.github/workflows/e2e-tests.yml`

- Executar testes end-to-end completos
- Validar fluxo: SEM → ML → DE → BC → NASP
- Gerar evidências (screenshots, logs)

### 4. Workflow de Testes de Segurança

**Arquivo:** `.github/workflows/security-tests.yml`

- SAST (Static Application Security Testing)
- DAST (Dynamic Application Security Testing)
- Scan de dependências (Dependabot, Snyk)
- Validação de secrets

### 5. Workflow de Testes de Carga

**Arquivo:** `.github/workflows/load-tests.yml`

- Executar testes de carga (Locust, K6)
- Validar performance sob carga
- Gerar relatórios de métricas

### 6. Workflow de Build e Push

**Arquivo:** `.github/workflows/build-push.yml`

- Build de imagens Docker para todos os módulos
- Push para GitHub Container Registry (GHCR)
- Tagging semântico (v1.0.0)

### 7. Workflow Completo (CI/CD)

**Arquivo:** `.github/workflows/ci-cd.yml`

- Orquestrar todos os workflows
- Quality gates
- Deploy automático (se aprovado)

---

## 🏗️ Estrutura dos Workflows

```
.github/
├── workflows/
│   ├── unit-tests.yml
│   ├── integration-tests.yml
│   ├── e2e-tests.yml
│   ├── security-tests.yml
│   ├── load-tests.yml
│   ├── build-push.yml
│   └── ci-cd.yml
└── dependabot.yml
```

---

## 🔧 Implementação dos Workflows

### 1. Workflow de Testes Unitários

```yaml
name: Unit Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        module: [sem-csmf, ml-nsmf, decision-engine, bc-nssmf, nasp-adapter]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        working-directory: apps/${{ matrix.module }}
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run unit tests
        working-directory: apps/${{ matrix.module }}
        run: |
          pytest tests/unit/ -v --cov=src --cov-report=xml --cov-report=html
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./apps/${{ matrix.module }}/coverage.xml
          flags: ${{ matrix.module }}
      
      - name: Check coverage threshold
        working-directory: apps/${{ matrix.module }}
        run: |
          coverage report --fail-under=80
```

### 2. Workflow de Testes de Integração

```yaml
name: Integration Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: trisla_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      kafka:
        image: confluentinc/cp-kafka:latest
        env:
          KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
          KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
        ports:
          - 9092:9092
      
      zookeeper:
        image: confluentinc/cp-zookeeper:latest
        env:
          ZOOKEEPER_CLIENT_PORT: 2181
        ports:
          - 2181:2181
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r tests/requirements.txt
      
      - name: Start services with docker-compose
        run: |
          docker-compose up -d
          sleep 30  # Wait for services to be ready
      
      - name: Run integration tests
        run: |
          pytest tests/integration/ -v
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/trisla_test
          KAFKA_BOOTSTRAP_SERVERS: localhost:9092
      
      - name: Stop services
        if: always()
        run: |
          docker-compose down
```

### 3. Workflow de Testes E2E

```yaml
name: E2E Tests

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r tests/requirements.txt
      
      - name: Start full stack
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 60  # Wait for all services
      
      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v --html=reports/e2e_report.html
      
      - name: Upload E2E report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-report
          path: reports/e2e_report.html
      
      - name: Stop stack
        if: always()
        run: |
          docker-compose -f docker-compose.test.yml down
```

### 4. Workflow de Testes de Segurança

```yaml
name: Security Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Run Bandit (Python SAST)
        run: |
          pip install bandit
          bandit -r apps/ -f json -o reports/bandit-report.json
      
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/python
            p/docker
      
      - name: Upload SAST report
        uses: actions/upload-artifact@v3
        with:
          name: sast-report
          path: reports/bandit-report.json
  
  dast:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Start application
        run: |
          docker-compose up -d
          sleep 30
      
      - name: Run OWASP ZAP
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'http://localhost:8000'
      
      - name: Upload DAST report
        uses: actions/upload-artifact@v3
        with:
          name: dast-report
          path: zap_report.html
  
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Run Snyk
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
      
      - name: Run Dependabot
        uses: dependabot/dependabot-core@main
```

### 5. Workflow de Testes de Carga

```yaml
name: Load Tests

on:
  workflow_dispatch:
    inputs:
      users:
        description: 'Number of concurrent users'
        required: false
        default: '100'
      duration:
        description: 'Test duration (seconds)'
        required: false
        default: '300'

jobs:
  load-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install Locust
        run: |
          pip install locust
      
      - name: Start application
        run: |
          docker-compose up -d
          sleep 60
      
      - name: Run load tests
        run: |
          locust -f tests/load/test_load.py \
            --headless \
            --users ${{ github.event.inputs.users }} \
            --spawn-rate 10 \
            --run-time ${{ github.event.inputs.duration }}s \
            --host http://localhost:8000 \
            --html reports/load_report.html
      
      - name: Upload load report
        uses: actions/upload-artifact@v3
        with:
          name: load-report
          path: reports/load_report.html
```

### 6. Workflow de Build e Push

```yaml
name: Build and Push

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-push:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        module: [sem-csmf, ml-nsmf, decision-engine, bc-nssmf, nasp-adapter]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to GHCR
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ghcr.io/${{ github.repository_owner }}/${{ matrix.module }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: ./apps/${{ matrix.module }}
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 7. Workflow Completo (CI/CD)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  unit-tests:
    uses: ./.github/workflows/unit-tests.yml
  
  integration-tests:
    uses: ./.github/workflows/integration-tests.yml
  
  security-tests:
    uses: ./.github/workflows/security-tests.yml
  
  e2e-tests:
    needs: [unit-tests, integration-tests]
    uses: ./.github/workflows/e2e-tests.yml
  
  build-push:
    needs: [unit-tests, integration-tests, security-tests]
    if: github.ref == 'refs/heads/main'
    uses: ./.github/workflows/build-push.yml
  
  deploy:
    needs: [build-push, e2e-tests]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploy to staging"
          # Add deployment steps
```

---

## 📊 Quality Gates

### Critérios de Aprovação

- ✅ **Cobertura de testes** ≥ 80%
- ✅ **Todos os testes unitários** passando
- ✅ **Todos os testes de integração** passando
- ✅ **0 vulnerabilidades críticas** de segurança
- ✅ **Testes E2E** passando
- ✅ **Performance** dentro dos limites (latência < 500ms)

### Bloqueio de Merge

```yaml
- name: Check quality gates
  run: |
    if [ "$COVERAGE" -lt 80 ]; then
      echo "Coverage below threshold"
      exit 1
    fi
    if [ "$CRITICAL_VULNS" -gt 0 ]; then
      echo "Critical vulnerabilities found"
      exit 1
    fi
```

---

## 🔔 Notificações

### Slack

```yaml
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'CI/CD Pipeline failed'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Email

```yaml
- name: Send email
  if: failure()
  uses: dawidd6/action-send-mail@v2
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: 'CI/CD Pipeline Failed'
    to: team@example.com
```

---

## ✅ Critérios de Sucesso

- ✅ **Todos os workflows** configurados e funcionando
- ✅ **Quality gates** implementados
- ✅ **Notificações** configuradas
- ✅ **Build e push** automático para GHCR
- ✅ **Relatórios** gerados e armazenados
- ✅ **Integração** com dependabot
- ✅ **Cache** de dependências otimizado

---

## 📚 Referências

- GitHub Actions Documentation
- Docker Buildx
- GitHub Container Registry (GHCR)
- Codecov
- Snyk
- OWASP ZAP

---

## ✔ Pronto para implementação no Cursor

