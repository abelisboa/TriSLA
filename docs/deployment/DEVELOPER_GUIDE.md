# TriSLA — Guia do Desenvolvedor

## 1. Introdução

Este documento fornece um guia completo para desenvolvedores que desejam contribuir com o projeto **TriSLA** (Triple-SLA). O TriSLA é uma plataforma de gerenciamento de SLA para redes 5G/O-RAN baseada em microserviços, utilizando Python, gRPC, Kafka, blockchain e integração com NASP.

**Objetivos deste guia:**

- Facilitar o setup do ambiente de desenvolvimento local
- Documentar a estrutura do código e arquitetura
- Estabelecer padrões de código e práticas recomendadas
- Explicar o fluxo de contribuição e processo de PR
- Fornecer ferramentas e scripts úteis para desenvolvimento

**Público-alvo:**

- Desenvolvedores Python
- Engenheiros de DevOps
- Contribuidores open source
- Integradores de sistemas O-RAN

---

## 2. Ferramentas Necessárias

### 2.1 Requisitos de Sistema

**Sistema Operacional:**
- Linux (Ubuntu 20.04+ recomendado)
- macOS (10.15+)
- Windows 10/11 (com WSL2 recomendado)

**Versões mínimas:**
- Python 3.10+
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+

### 2.2 Instalação de Dependências

**Python 3.10+:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv python3-pip

# macOS (via Homebrew)
brew install python@3.10

# Windows (via Chocolatey)
choco install python310
```

**Docker e Docker Compose:**

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin

# macOS
brew install docker docker-compose

# Windows
# Baixar Docker Desktop de https://www.docker.com/products/docker-desktop
```

**Ferramentas adicionais:**

```bash
# Kubernetes CLI (opcional, para testes locais)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm (opcional, para deploy em Kubernetes)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# gRPCurl (para testes de gRPC)
brew install grpcurl  # macOS
# ou via Go: go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
```

### 2.3 Ferramentas de Desenvolvimento

**Editores recomendados:**
- Visual Studio Code (com extensões Python, Docker, YAML)
- PyCharm Professional
- Vim/Neovim (com plugins Python)

**Extensões VS Code recomendadas:**
- Python (Microsoft)
- Docker (Microsoft)
- YAML (Red Hat)
- GitLens
- Remote - Containers

---

## 3. Estrutura do Repositório

### 3.1 Visão Geral

```
TriSLA/
├── apps/                          # Módulos principais
│   ├── sem-csmf/                  # Semantic CSMF
│   ├── ml-nsmf/                   # Machine Learning NSMF
│   ├── decision-engine/           # Decision Engine
│   ├── bc-nssmf/                  # Blockchain NSSMF
│   ├── sla-agent-layer/           # SLA Agent Layer
│   ├── nasp-adapter/              # NASP Adapter
│   └── ui-dashboard/              # UI Dashboard
├── helm/                          # Helm charts
│   └── trisla/
│       ├── templates/
│       ├── values.yaml
│       └── values-production.yaml
├── monitoring/                    # Observabilidade
│   ├── prometheus/
│   ├── grafana/
│   └── otel-collector/
├── scripts/                       # Scripts utilitários
│   ├── build-all-images.sh
│   ├── deploy-trisla-nasp.sh
│   └── validate-local.sh
├── tests/                         # Testes
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker-compose.yml             # Ambiente local
├── pytest.ini                    # Configuração pytest
├── requirements-dev.txt           # Dependências de desenvolvimento
└── README.md                      # Documentação principal
```

### 3.2 Estrutura de um Módulo

Cada módulo em `apps/` segue a seguinte estrutura:

```
apps/<module-name>/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Ponto de entrada
│   ├── config.py                  # Configurações
│   ├── models/                    # Modelos de dados
│   ├── api/                       # Endpoints REST/gRPC
│   ├── services/                  # Lógica de negócio
│   └── utils/                     # Utilitários
├── tests/                         # Testes do módulo
│   ├── unit/
│   └── integration/
├── Dockerfile                     # Imagem Docker
├── requirements.txt               # Dependências Python
└── README.md                      # Documentação do módulo
```

### 3.3 Convenções de Nomenclatura

**Arquivos Python:**
- Módulos: `snake_case.py`
- Classes: `PascalCase`
- Funções/variáveis: `snake_case`
- Constantes: `UPPER_SNAKE_CASE`

**Docker:**
- Imagens: `ghcr.io/abelisboa/trisla-<module>:<tag>`
- Containers: `trisla-<module>`

**Kubernetes:**
- Namespace: `trisla`
- Deployments: `trisla-<module>`
- Services: `trisla-<module>`

---

## 4. Setup Local

### 4.1 Clonar o Repositório

```bash
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA
```

### 4.2 Python Virtual Environment

**Criar venv:**

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar (Linux/macOS)
source .venv/bin/activate

# Ativar (Windows)
.venv\Scripts\activate

# Ativar (PowerShell)
.venv\Scripts\Activate.ps1
```

**Instalar dependências de desenvolvimento:**

```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
```

**requirements-dev.txt (exemplo):**

```txt
# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
pytest-mock==3.12.0

# Code Quality
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.0
pylint==3.0.2

# Development Tools
ipython==8.18.1
ipdb==0.13.13
pre-commit==3.5.0

# Documentation
sphinx==7.2.6
sphinx-rtd-theme==1.3.0
```

### 4.3 Docker Setup

**Verificar instalação:**

```bash
docker --version
docker compose version
```

**Build das imagens (opcional, para desenvolvimento):**

```bash
# Build todas as imagens
./scripts/build-all-images.sh

# Build imagem específica
cd apps/sem-csmf
docker build -t ghcr.io/abelisboa/trisla-sem-csmf:dev .
```

### 4.4 Docker Compose

**Iniciar serviços de infraestrutura:**

```bash
# Iniciar apenas infraestrutura (PostgreSQL, Kafka, Prometheus, etc.)
docker compose up -d postgres kafka zookeeper prometheus grafana otlp-collector

# Verificar status
docker compose ps

# Ver logs
docker compose logs -f kafka
```

**Variáveis de ambiente (`.env`):**

```bash
# Criar arquivo .env na raiz
cat > .env << EOF
POSTGRES_DB=trisla
POSTGRES_USER=trisla
POSTGRES_PASSWORD=trisla_password
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
OTLP_ENDPOINT=http://localhost:4317
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000
EOF
```

### 4.5 Rodar SEM-CSMF Localmente

**Opção 1: Via Python (desenvolvimento):**

```bash
cd apps/sem-csmf

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export POSTGRES_URL=postgresql://trisla:trisla_password@localhost:5432/trisla
export DECISION_ENGINE_URL=localhost:50051
export KAFKA_BOOTSTRAP_SERVERS=localhost:29092

# Executar
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

**Opção 2: Via Docker Compose:**

```bash
# Na raiz do projeto
docker compose up -d sem-csmf

# Ver logs
docker compose logs -f sem-csmf
```

**Testar SEM-CSMF:**

```bash
# Health check
curl http://localhost:8080/health

# Criar intent
curl -X POST http://localhost:8080/api/v1/intents \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-001",
    "intent": "Criar slice para AR com latência < 10ms"
  }'
```

### 4.6 Rodar Decision Engine Localmente

**Via Python:**

```bash
cd apps/decision-engine

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis
export ML_NSMF_URL=http://localhost:8081
export BC_NSSMF_URL=http://localhost:8083
export KAFKA_BOOTSTRAP_SERVERS=localhost:29092

# Executar gRPC server
python src/grpc_server.py

# Executar REST API (opcional)
python -m uvicorn src.main:app --host 0.0.0.0 --port 50051 --reload
```

**Via Docker Compose:**

```bash
docker compose up -d decision-engine
```

**Testar Decision Engine (gRPC):**

```bash
# Usando gRPCurl
grpcurl -plaintext \
  -d '{
    "intent_id": "intent-001",
    "nest_id": "nest-001",
    "tenant_id": "tenant-001",
    "service_type": "eMBB",
    "sla_requirements": {
      "latency": "10ms",
      "throughput": "100Mbps"
    }
  }' \
  localhost:50051 \
  trisla.i01.DecisionEngineService/SendNESTMetadata
```

### 4.7 Rodar ML-NSMF Localmente

**Via Python:**

```bash
cd apps/ml-nsmf

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis
export KAFKA_BOOTSTRAP_SERVERS=localhost:29092
export MODEL_PATH=./models/lstm_model.h5

# Executar
python -m uvicorn src.main:app --host 0.0.0.0 --port 8081 --reload
```

**Via Docker Compose:**

```bash
docker compose up -d ml-nsmf
```

**Testar ML-NSMF:**

```bash
# Health check
curl http://localhost:8081/health

# Enviar NEST para predição
curl -X POST http://localhost:8081/api/v1/nest \
  -H "Content-Type: application/json" \
  -d @examples/nest_example.json
```

---

## 5. Execução Completa Local

### 5.1 Docker Compose Completo

**Iniciar todos os serviços:**

```bash
# Iniciar stack completo
docker compose up -d

# Verificar status de todos os serviços
docker compose ps

# Ver logs de todos os serviços
docker compose logs -f

# Parar todos os serviços
docker compose down

# Parar e remover volumes
docker compose down -v
```

### 5.2 Explicação do docker-compose.yml

**Serviços de infraestrutura:**

```yaml
postgres:
  image: postgres:15-alpine
  ports:
    - "5432:5432"
  environment:
    POSTGRES_DB: trisla
    POSTGRES_USER: trisla
    POSTGRES_PASSWORD: trisla_password
  volumes:
    - postgres-data:/var/lib/postgresql/data
  # Porta: 5432
  # Uso: Banco de dados para SEM-CSMF

kafka:
  image: confluentinc/cp-kafka:7.4.0
  ports:
    - "29092:9092"
  environment:
    KAFKA_BOOTSTRAP_SERVERS: kafka:9092
  depends_on:
    - zookeeper
  # Porta: 29092 (host) -> 9092 (container)
  # Uso: Mensageria assíncrona (I-03, I-04, I-05)

prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
  # Porta: 9090
  # Uso: Coleta de métricas

grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    GF_SECURITY_ADMIN_USER: admin
    GF_SECURITY_ADMIN_PASSWORD: admin
  # Porta: 3000
  # Uso: Visualização de métricas e dashboards
```

**Serviços TriSLA:**

```yaml
sem-csmf:
  build:
    context: ./apps/sem-csmf
  ports:
    - "8080:8080"
  environment:
    POSTGRES_URL: postgresql://trisla:trisla_password@postgres:5432/trisla
    DECISION_ENGINE_URL: decision-engine:50051
    KAFKA_BOOTSTRAP_SERVERS: kafka:9092
  depends_on:
    - postgres
    - kafka
    - decision-engine
  # Porta: 8080
  # Dependências: PostgreSQL, Kafka, Decision Engine

decision-engine:
  build:
    context: ./apps/decision-engine
  ports:
    - "50051:50051"  # gRPC
    - "50052:50052"  # REST (opcional)
  environment:
    ML_NSMF_URL: http://ml-nsmf:8081
    BC_NSSMF_URL: http://bc-nssmf:8083
    KAFKA_BOOTSTRAP_SERVERS: kafka:9092
  depends_on:
    - kafka
    - ml-nsmf
    - bc-nssmf
  # Portas: 50051 (gRPC), 50052 (REST)
  # Dependências: Kafka, ML-NSMF, BC-NSSMF

ml-nsmf:
  build:
    context: ./apps/ml-nsmf
  ports:
    - "8081:8081"
  environment:
    KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    MODEL_PATH: /app/models/lstm_model.h5
  depends_on:
    - kafka
  # Porta: 8081
  # Dependências: Kafka
```

### 5.3 Variáveis de Ambiente

**Variáveis comuns:**

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `POSTGRES_URL` | URL do PostgreSQL | `postgresql://trisla:trisla_password@postgres:5432/trisla` |
| `KAFKA_BOOTSTRAP_SERVERS` | Servidores Kafka | `kafka:9092` |
| `OTLP_ENDPOINT` | Endpoint OTLP | `http://otlp-collector:4317` |
| `PROMETHEUS_URL` | URL do Prometheus | `http://prometheus:9090` |
| `LOG_LEVEL` | Nível de log | `INFO` |
| `ENVIRONMENT` | Ambiente | `development` |

**Configurar via `.env`:**

```bash
# Criar .env
cat > .env << EOF
POSTGRES_URL=postgresql://trisla:trisla_password@postgres:5432/trisla
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
OTLP_ENDPOINT=http://otlp-collector:4317
LOG_LEVEL=DEBUG
ENVIRONMENT=development
EOF

# Docker Compose carrega automaticamente .env
docker compose up -d
```

### 5.4 Dependências entre Serviços

**Ordem de inicialização:**

1. **Infraestrutura base:**
   - PostgreSQL
   - Zookeeper
   - Kafka

2. **Observabilidade:**
   - Prometheus
   - Grafana
   - OTLP Collector

3. **Módulos TriSLA:**
   - BC-NSSMF (sem dependências externas)
   - ML-NSMF (depende de Kafka)
   - Decision Engine (depende de Kafka, ML-NSMF, BC-NSSMF)
   - SEM-CSMF (depende de PostgreSQL, Kafka, Decision Engine)
   - SLA-Agent Layer (depende de Kafka)
   - NASP Adapter (depende de SLA-Agent Layer)

**Health checks:**

```bash
# Verificar saúde de todos os serviços
docker compose ps

# Health check manual
curl http://localhost:8080/health  # SEM-CSMF
curl http://localhost:8081/health  # ML-NSMF
curl http://localhost:50052/health # Decision Engine
```

---

## 6. Integração com NASP (Modo Dev)

### 6.1 Mock NASP

Para desenvolvimento local, o `docker-compose.yml` inclui serviços mock do NASP:

```yaml
mock-nasp-ran:
  image: mockserver/mockserver:latest
  ports:
    - "1080:1080"
  # Mock RAN endpoints

mock-nasp-transport:
  image: mockserver/mockserver:latest
  ports:
    - "1081:1080"
  # Mock Transport endpoints

mock-nasp-core:
  image: mockserver/mockserver:latest
  ports:
    - "1082:1080"
  # Mock Core endpoints
```

### 6.2 Configurar NASP Adapter para Mock

**Variáveis de ambiente:**

```bash
export NASP_RAN_URL=http://localhost:1080
export NASP_TRANSPORT_URL=http://localhost:1081
export NASP_CORE_URL=http://localhost:1082
export NASP_MOCK_MODE=true
```

### 6.3 Testar Integração com Mock

```bash
# Iniciar mock NASP
docker compose up -d mock-nasp-ran mock-nasp-transport mock-nasp-core

# Configurar expectativas no MockServer
curl -X PUT http://localhost:1080/expectation \
  -H "Content-Type: application/json" \
  -d '{
    "httpRequest": {
      "path": "/api/v1/slices",
      "method": "POST"
    },
    "httpResponse": {
      "statusCode": 200,
      "body": {
        "slice_id": "slice-001",
        "status": "provisioned"
      }
    }
  }'

# Testar NASP Adapter
curl -X POST http://localhost:8085/api/v1/actions \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "PROVISION_SLICE",
    "domain": "RAN",
    "action_data": {
      "slice_id": "slice-001"
    }
  }'
```

---

## 7. Estilo de Código e Lint

### 7.1 Black (Formatação)

**Instalação:**

```bash
pip install black==23.11.0
```

**Configuração (`pyproject.toml`):**

```toml
[tool.black]
line-length = 100
target-version = ['py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''
```

**Uso:**

```bash
# Formatar arquivo
black src/main.py

# Formatar diretório
black apps/sem-csmf/src

# Verificar sem modificar
black --check apps/sem-csmf/src

# Formatar todos os módulos
black apps/
```

### 7.2 isort (Import Sorting)

**Instalação:**

```bash
pip install isort==5.12.0
```

**Configuração (`pyproject.toml`):**

```toml
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["*/migrations/*", "*/__pycache__/*"]
```

**Uso:**

```bash
# Ordenar imports
isort src/main.py

# Verificar sem modificar
isort --check-only src/

# Ordenar todos os módulos
isort apps/
```

### 7.3 flake8 (Linting)

**Instalação:**

```bash
pip install flake8==6.1.0
```

**Configuração (`.flake8` ou `setup.cfg`):**

```ini
[flake8]
max-line-length = 100
exclude =
    .git,
    __pycache__,
    .venv,
    venv,
    build,
    dist,
    *.egg-info
ignore =
    E203,  # whitespace before ':'
    E501,  # line too long (handled by black)
    W503,  # line break before binary operator
```

**Uso:**

```bash
# Lint arquivo
flake8 src/main.py

# Lint diretório
flake8 apps/sem-csmf/src

# Lint com estatísticas
flake8 --statistics apps/
```

### 7.4 mypy (Type Checking)

**Instalação:**

```bash
pip install mypy==1.7.0
```

**Configuração (`mypy.ini` ou `pyproject.toml`):**

```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
ignore_missing_imports = True
```

**Uso:**

```bash
# Type check
mypy src/main.py

# Type check com relatório
mypy apps/sem-csmf/src --html-report mypy-report
```

### 7.5 Pre-commit Hooks

**Instalação:**

```bash
pip install pre-commit==3.5.0
pre-commit install
```

**Configuração (`.pre-commit-config.yaml`):**

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**Uso:**

```bash
# Executar hooks manualmente
pre-commit run --all-files

# Pular hooks (não recomendado)
git commit --no-verify
```

### 7.6 Script de Validação

**Script unificado (`scripts/validate-code.sh`):**

```bash
#!/bin/bash
set -e

echo "🔍 Validando código..."

# Black
echo "📝 Formatando com Black..."
black --check apps/ tests/

# isort
echo "📦 Ordenando imports com isort..."
isort --check-only apps/ tests/

# flake8
echo "🔎 Executando flake8..."
flake8 apps/ tests/

# mypy
echo "🔬 Executando mypy..."
mypy apps/

echo "✅ Validação concluída!"
```

---

## 8. Testes

### 8.1 Estrutura de Testes

```
tests/
├── unit/                    # Testes unitários
│   ├── test_sem_csmf.py
│   ├── test_ml_nsmf.py
│   └── test_decision_engine.py
├── integration/             # Testes de integração
│   ├── test_grpc_communication.py
│   ├── test_kafka_flow.py
│   └── test_module_integration.py
├── e2e/                     # Testes end-to-end
│   └── test_full_workflow.py
└── conftest.py             # Configuração pytest
```

### 8.2 Testes Unitários

**Exemplo (`tests/unit/test_sem_csmf.py`):**

```python
import pytest
from unittest.mock import Mock, patch
from apps.sem_csmf.src.intent_processor import IntentProcessor
from apps.sem_csmf.src.models.intent import Intent


class TestIntentProcessor:
    """Testes unitários para IntentProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Fixture para IntentProcessor"""
        return IntentProcessor()
    
    @pytest.fixture
    def sample_intent(self):
        """Fixture para intent de exemplo"""
        return Intent(
            tenant_id="tenant-001",
            intent="Criar slice para AR",
            service_type="eMBB"
        )
    
    def test_process_intent_success(self, processor, sample_intent):
        """Testa processamento bem-sucedido de intent"""
        with patch('apps.sem_csmf.src.ontology.parser.parse_intent') as mock_parse:
            mock_parse.return_value = {"service_type": "eMBB"}
            
            result = processor.process(sample_intent)
            
            assert result is not None
            assert result.status == "processed"
            mock_parse.assert_called_once()
    
    def test_process_intent_invalid(self, processor):
        """Testa processamento de intent inválido"""
        invalid_intent = Intent(
            tenant_id="",
            intent="",
            service_type=""
        )
        
        with pytest.raises(ValueError):
            processor.process(invalid_intent)
```

**Executar testes unitários:**

```bash
# Todos os testes unitários
pytest tests/unit/ -v

# Teste específico
pytest tests/unit/test_sem_csmf.py::TestIntentProcessor::test_process_intent_success -v

# Com cobertura
pytest tests/unit/ --cov=apps/sem-csmf/src --cov-report=html
```

### 8.3 Testes de Integração

**Exemplo (`tests/integration/test_grpc_communication.py`):**

```python
import pytest
import grpc
from apps.decision_engine.src.proto.proto import i01_interface_pb2
from apps.decision_engine.src.proto.proto import i01_interface_pb2_grpc


@pytest.fixture(scope="module")
def grpc_channel():
    """Fixture para canal gRPC"""
    channel = grpc.insecure_channel('localhost:50051')
    yield channel
    channel.close()


@pytest.fixture(scope="module")
def grpc_stub(grpc_channel):
    """Fixture para stub gRPC"""
    return i01_interface_pb2_grpc.DecisionEngineServiceStub(grpc_channel)


def test_send_nest_metadata(grpc_stub):
    """Testa envio de metadados NEST via gRPC"""
    request = i01_interface_pb2.NESTMetadataRequest(
        intent_id="intent-001",
        nest_id="nest-001",
        tenant_id="tenant-001",
        service_type="eMBB",
        sla_requirements={
            "latency": "10ms",
            "throughput": "100Mbps"
        }
    )
    
    response = grpc_stub.SendNESTMetadata(request, timeout=5)
    
    assert response.success is True
    assert response.decision_id is not None
```

**Executar testes de integração:**

```bash
# Requer serviços rodando (Docker Compose)
docker compose up -d

# Executar testes de integração
pytest tests/integration/ -v

# Com marcadores
pytest tests/integration/ -m integration -v
```

### 8.4 Testes End-to-End

**Exemplo (`tests/e2e/test_full_workflow.py`):**

```python
import pytest
import requests
import time
from typing import Dict, Any


@pytest.fixture(scope="module")
def base_urls():
    """URLs base dos serviços"""
    return {
        "sem_csmf": "http://localhost:8080",
        "ml_nsmf": "http://localhost:8081",
        "decision_engine": "http://localhost:50052",
        "bc_nssmf": "http://localhost:8083"
    }


def test_full_workflow(base_urls):
    """Testa fluxo completo: Intent → NEST → Decisão → Ação"""
    
    # 1. Criar intent
    intent_response = requests.post(
        f"{base_urls['sem_csmf']}/api/v1/intents",
        json={
            "tenant_id": "tenant-001",
            "intent": "Criar slice para AR com latência < 10ms"
        }
    )
    assert intent_response.status_code == 200
    intent_data = intent_response.json()
    intent_id = intent_data["intent_id"]
    
    # 2. Aguardar geração de NEST
    time.sleep(2)
    
    # 3. Verificar NEST gerado
    nest_response = requests.get(
        f"{base_urls['sem_csmf']}/api/v1/nests/{intent_id}"
    )
    assert nest_response.status_code == 200
    nest_data = nest_response.json()
    nest_id = nest_data["nest_id"]
    
    # 4. Verificar predição ML
    prediction_response = requests.get(
        f"{base_urls['ml_nsmf']}/api/v1/predictions/{nest_id}"
    )
    assert prediction_response.status_code == 200
    
    # 5. Verificar decisão
    decision_response = requests.get(
        f"{base_urls['decision_engine']}/api/v1/decisions/{intent_id}"
    )
    assert decision_response.status_code == 200
    decision_data = decision_response.json()
    assert decision_data["decision"] in ["ACCEPT", "REJECT", "RENEGOTIATE"]
    
    # 6. Verificar registro em blockchain (se ACCEPT)
    if decision_data["decision"] == "ACCEPT":
        blockchain_response = requests.get(
            f"{base_urls['bc_nssmf']}/api/v1/slas/{intent_id}"
        )
        assert blockchain_response.status_code == 200
```

**Executar testes E2E:**

```bash
# Requer stack completo rodando
docker compose up -d

# Executar testes E2E
pytest tests/e2e/ -v -m e2e

# Com timeout aumentado
pytest tests/e2e/ -v --timeout=300
```

### 8.5 Configuração pytest

**`pytest.ini`:**

```ini
[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=apps
    --cov-report=term-missing
    --cov-report=html
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

**Marcadores:**

```python
import pytest

@pytest.mark.unit
def test_unit():
    """Teste unitário"""
    pass

@pytest.mark.integration
def test_integration():
    """Teste de integração"""
    pass

@pytest.mark.e2e
@pytest.mark.slow
def test_e2e():
    """Teste E2E lento"""
    pass
```

**Executar por marcador:**

```bash
# Apenas testes unitários
pytest -m unit

# Apenas testes de integração
pytest -m integration

# Apenas testes E2E
pytest -m e2e

# Excluir testes lentos
pytest -m "not slow"
```

---

## 9. Build e Push das Imagens GHCR

### 9.1 Configurar GitHub Container Registry

**Autenticação:**

```bash
# Login no GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Ou via GitHub CLI
gh auth login
gh auth token | docker login ghcr.io -u USERNAME --password-stdin
```

**Criar token GitHub (PAT):**

1. GitHub → Settings → Developer settings → Personal access tokens
2. Gerar token com permissões: `write:packages`, `read:packages`
3. Exportar: `export GITHUB_TOKEN=<token>`

### 9.2 Build de Imagens

**Build individual:**

```bash
# SEM-CSMF
cd apps/sem-csmf
docker build -t ghcr.io/abelisboa/trisla-sem-csmf:latest .
docker build -t ghcr.io/abelisboa/trisla-sem-csmf:v1.0.0 .

# ML-NSMF
cd apps/ml-nsmf
docker build -t ghcr.io/abelisboa/trisla-ml-nsmf:latest .

# Decision Engine
cd apps/decision-engine
docker build -t ghcr.io/abelisboa/trisla-decision-engine:latest .
```

**Build todas as imagens:**

```bash
# Usar script
./scripts/build-all-images.sh

# Ou manualmente
for module in sem-csmf ml-nsmf decision-engine bc-nssmf sla-agent-layer nasp-adapter; do
  cd apps/$module
  docker build -t ghcr.io/abelisboa/trisla-$module:latest .
  cd ../..
done
```

### 9.3 Push para GHCR

**Push individual:**

```bash
# SEM-CSMF
docker push ghcr.io/abelisboa/trisla-sem-csmf:latest
docker push ghcr.io/abelisboa/trisla-sem-csmf:v1.0.0

# ML-NSMF
docker push ghcr.io/abelisboa/trisla-ml-nsmf:latest
```

**Push todas as imagens:**

```bash
# Usar script
./scripts/push-all-images.sh

# Ou manualmente
for module in sem-csmf ml-nsmf decision-engine bc-nssmf sla-agent-layer nasp-adapter; do
  docker push ghcr.io/abelisboa/trisla-$module:latest
done
```

### 9.4 Multi-stage Build

**Exemplo de Dockerfile otimizado:**

```dockerfile
# Stage 1: Build
FROM python:3.10-slim as builder

WORKDIR /app

# Instalar dependências de build
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Copiar dependências do builder
COPY --from=builder /root/.local /root/.local

# Copiar código
COPY src/ ./src/

# Adicionar PATH
ENV PATH=/root/.local/bin:$PATH

# Expor porta
EXPOSE 8080

# Comando
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 9.5 Verificar Imagens

```bash
# Listar imagens locais
docker images | grep trisla

# Verificar imagem no GHCR
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/user/packages?package_type=container

# Testar imagem localmente
docker run -p 8080:8080 ghcr.io/abelisboa/trisla-sem-csmf:latest
```

---

## 10. Pipeline CI/CD para Desenvolvedores

### 10.1 GitHub Actions

**Estrutura básica (`.github/workflows/ci.yml`):**

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install black isort flake8 mypy
      - name: Run black
        run: black --check apps/ tests/
      - name: Run isort
        run: isort --check-only apps/ tests/
      - name: Run flake8
        run: flake8 apps/ tests/
      - name: Run mypy
        run: mypy apps/

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: trisla
          POSTGRES_USER: trisla
          POSTGRES_PASSWORD: trisla_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      kafka:
        image: confluentinc/cp-kafka:7.4.0
        env:
          KAFKA_BOOTSTRAP_SERVERS: localhost:9092
        options: >-
          --health-cmd "kafka-broker-api-versions --bootstrap-server localhost:9092"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
          pip install -r apps/sem-csmf/requirements.txt
          pip install -r apps/ml-nsmf/requirements.txt
          pip install -r apps/decision-engine/requirements.txt
      - name: Run unit tests
        run: pytest tests/unit/ -v
      - name: Run integration tests
        run: pytest tests/integration/ -v
      - name: Generate coverage
        run: pytest --cov=apps --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v3
      - name: Login to GHCR
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push
        run: |
          docker build -t ghcr.io/abelisboa/trisla-sem-csmf:${{ github.sha }} apps/sem-csmf/
          docker push ghcr.io/abelisboa/trisla-sem-csmf:${{ github.sha }}
```

### 10.2 Executar CI Localmente

**Usando act (GitHub Actions local):**

```bash
# Instalar act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Executar workflow
act -j lint
act -j test
act -j build
```

### 10.3 Pre-commit no CI

```yaml
- name: Run pre-commit
  uses: pre-commit/action@v3.0.0
```

---

## 11. Fluxo de PR no GitHub

### 11.1 Processo de Contribuição

**1. Fork do repositório:**

```bash
# Fork no GitHub (via interface web)
# Clonar fork local
git clone https://github.com/SEU_USUARIO/TriSLA.git
cd TriSLA
git remote add upstream https://github.com/abelisboa/TriSLA.git
```

**2. Criar branch:**

```bash
# Atualizar main
git checkout main
git pull upstream main

# Criar branch de feature
git checkout -b feature/nova-funcionalidade

# Ou branch de bugfix
git checkout -b fix/corrigir-bug
```

**3. Desenvolver e commitar:**

```bash
# Fazer alterações
# ...

# Adicionar arquivos
git add .

# Commitar (seguindo Conventional Commits)
git commit -m "feat: adicionar nova funcionalidade X"

# Push para fork
git push origin feature/nova-funcionalidade
```

### 11.2 Conventional Commits

**Formato:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Tipos:**

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Tarefas de manutenção

**Exemplos:**

```bash
git commit -m "feat(sem-csmf): adicionar suporte a intents OWL"
git commit -m "fix(decision-engine): corrigir timeout em gRPC"
git commit -m "docs: atualizar guia de desenvolvedor"
git commit -m "test(ml-nsmf): adicionar testes unitários para predições"
```

### 11.3 Criar Pull Request

**1. Abrir PR no GitHub:**

- Acessar: https://github.com/abelisboa/TriSLA/pulls
- Clicar em "New Pull Request"
- Selecionar branch do fork
- Preencher template de PR

**2. Template de PR:**

```markdown
## Descrição
Breve descrição das mudanças.

## Tipo de mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## Checklist
- [ ] Código segue estilo do projeto (black, isort, flake8)
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] CI passa
- [ ] Sem conflitos com main

## Testes
Como testar as mudanças:
1. ...
2. ...

## Screenshots (se aplicável)
...
```

### 11.4 Revisão e Merge

**Processo:**

1. **CI deve passar**: Todos os checks devem estar verdes
2. **Code review**: Pelo menos 1 aprovação necessária
3. **Resolução de comentários**: Responder e fazer alterações se necessário
4. **Merge**: Mantenedor faz merge após aprovação

**Comandos úteis:**

```bash
# Atualizar branch com main
git checkout main
git pull upstream main
git checkout feature/nova-funcionalidade
git rebase main

# Resolver conflitos
git rebase --continue

# Force push (após rebase)
git push origin feature/nova-funcionalidade --force-with-lease
```

---

## 12. Como Abrir Issues Técnicas

### 12.1 Template de Bug Report

```markdown
## Descrição
Descrição clara e concisa do bug.

## Passos para reproduzir
1. ...
2. ...
3. ...

## Comportamento esperado
O que deveria acontecer.

## Comportamento atual
O que está acontecendo.

## Ambiente
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.10.5]
- Docker: [e.g., 20.10.12]
- Versão: [e.g., v1.0.0]

## Logs
```
Logs relevantes aqui
```

## Screenshots
Se aplicável.
```

### 12.2 Template de Feature Request

```markdown
## Descrição
Descrição clara da funcionalidade desejada.

## Motivação
Por que essa funcionalidade é necessária?

## Solução proposta
Como você imagina que isso funcionaria?

## Alternativas consideradas
Outras soluções que você considerou.

## Contexto adicional
Qualquer outra informação relevante.
```

### 12.3 Labels

- `bug`: Bug report
- `enhancement`: Feature request
- `documentation`: Melhorias na documentação
- `question`: Pergunta
- `help wanted`: Precisa de ajuda
- `good first issue`: Bom para iniciantes

---

## 13. Ferramentas de Debug Recomendadas

### 13.1 Python Debugger (pdb/ipdb)

**Uso básico:**

```python
import ipdb

def process_intent(intent):
    ipdb.set_trace()  # Breakpoint
    # Código aqui
    result = do_something(intent)
    return result
```

**Comandos:**

- `n` (next): Próxima linha
- `s` (step): Entrar em função
- `c` (continue): Continuar
- `l` (list): Listar código
- `p <var>`: Imprimir variável
- `pp <var>`: Pretty print

### 13.2 Logging

**Configuração:**

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def process_intent(intent):
    logger.debug(f"Processing intent: {intent.id}")
    logger.info("Intent processing started")
    # ...
    logger.error("Error occurred", exc_info=True)
```

### 13.3 Docker Debug

**Entrar em container:**

```bash
# Executar comando em container
docker compose exec sem-csmf bash

# Ver logs em tempo real
docker compose logs -f sem-csmf

# Ver logs de todos os serviços
docker compose logs -f

# Inspecionar container
docker inspect trisla-sem-csmf
```

### 13.4 gRPC Debug

**Usando gRPCurl:**

```bash
# Listar serviços
grpcurl -plaintext localhost:50051 list

# Descrever serviço
grpcurl -plaintext localhost:50051 describe trisla.i01.DecisionEngineService

# Chamar método
grpcurl -plaintext \
  -d '{"intent_id": "intent-001"}' \
  localhost:50051 \
  trisla.i01.DecisionEngineService/GetDecisionStatus
```

### 13.5 Kafka Debug

**Usando kafkacat (kcat):**

```bash
# Consumir mensagens
kafkacat -b localhost:29092 -t trisla-ml-predictions -C

# Produzir mensagem
echo '{"test": "message"}' | kafkacat -b localhost:29092 -t trisla-ml-predictions -P

# Listar tópicos
kafkacat -b localhost:29092 -L
```

### 13.6 Network Debug

**Verificar conectividade:**

```bash
# Testar conexão
curl http://localhost:8080/health

# Testar gRPC
grpcurl -plaintext localhost:50051 list

# Verificar portas
netstat -tulpn | grep -E '8080|50051|29092'

# Ou com ss
ss -tulpn | grep -E '8080|50051|29092'
```

---

## 14. Apêndice

### 14.1 Scripts Úteis

**`scripts/start-local.sh`:**

```bash
#!/bin/bash
# Inicia ambiente local completo

docker compose up -d
echo "✅ Serviços iniciados"
echo "📊 Grafana: http://localhost:3000"
echo "📈 Prometheus: http://localhost:9090"
```

**`scripts/validate-local.sh`:**

```bash
#!/bin/bash
# Valida ambiente local

echo "🔍 Validando serviços..."

# Health checks
curl -f http://localhost:8080/health || echo "❌ SEM-CSMF não está respondendo"
curl -f http://localhost:8081/health || echo "❌ ML-NSMF não está respondendo"
curl -f http://localhost:50052/health || echo "❌ Decision Engine não está respondendo"

echo "✅ Validação concluída"
```

**`scripts/run-tests.sh`:**

```bash
#!/bin/bash
# Executa todos os testes

echo "🧪 Executando testes..."

# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v -m e2e

echo "✅ Testes concluídos"
```

### 14.2 Variáveis de Ambiente

**Desenvolvimento local:**

```bash
# .env
POSTGRES_URL=postgresql://trisla:trisla_password@localhost:5432/trisla
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
OTLP_ENDPOINT=http://localhost:4317
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

**Produção:**

```bash
# Kubernetes Secrets
POSTGRES_URL=postgresql://user:pass@postgres:5432/trisla
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
OTLP_ENDPOINT=http://otlp-collector:4317
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### 14.3 Referências Internas

**Documentação:**

- `README.md`: Visão geral do projeto
- `README_OPERATIONS_PROD.md`: Guia de operações em produção
- `SECURITY_HARDENING.md`: Guia de segurança
- `TROUBLESHOOTING_TRISLA.md`: Guia de troubleshooting
- `API_REFERENCE.md`: Referência de APIs
- `INTERNAL_INTERFACES_I01_I07.md`: Documentação de interfaces internas
- `NASP_DEPLOY_GUIDE.md`: Guia de deploy no NASP
- `INSTALL_FULL_PROD.md`: Guia de instalação completa

**Código:**

- `apps/*/README.md`: Documentação de cada módulo
- `helm/trisla/README.md`: Documentação do Helm chart
- `monitoring/README.md`: Documentação de observabilidade

**Scripts:**

- `scripts/build-all-images.sh`: Build de todas as imagens
- `scripts/deploy-trisla-nasp.sh`: Deploy no NASP
- `scripts/validate-local.sh`: Validação local

### 14.4 Comunidade

**Canais:**

- GitHub Issues: Para bugs e feature requests
- GitHub Discussions: Para perguntas e discussões
- Pull Requests: Para contribuições

**Contribuindo:**

1. Fork o repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request
5. Aguarde revisão e merge

---

## 12. Fluxo de Teste E2E Local vs. Deploy NASP

### 12.1 Teste E2E Local

**Objetivo:** Validar o fluxo completo I-01 → I-07 em ambiente local com Docker Compose.

**Iniciar ambiente:**
```bash
# Linux/macOS
./scripts/start-local-e2e.sh

# Windows PowerShell
.\scripts\start-local-e2e.ps1
```

**Executar testes:**
```bash
pytest tests/e2e/test_trisla_e2e.py -v
```

**Cenários de teste:**
- URLLC (cirurgia remota / missão crítica)
- eMBB (vídeo 4K / banda larga móvel)
- mMTC (IoT massivo)

**Arquivo de configuração:** `tests/e2e/scenarios_e2e_trisla.yaml`

### 12.2 Deploy NASP Node1

**Objetivo:** Deploy controlado no ambiente NASP real.

**Pré-requisitos:**
- Seguir `docs/NASP_PREDEPLOY_CHECKLIST.md`
- Descoberta de endpoints NASP
- Configuração de `helm/trisla/values-production.yaml`

**Deploy:**
```bash
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  -f ./helm/trisla/values-production.yaml \
  --wait \
  --timeout 10m
```

**Validação:**
- Health checks de todos os módulos
- Teste E2E no cluster NASP
- Verificação de conectividade com NASP

### 12.3 Diferenças entre Local e NASP

| Aspecto | Local (Docker Compose) | NASP (Kubernetes) |
|---------|------------------------|-------------------|
| **NASP Adapter** | Modo mock controlado | Modo real (endpoints reais) |
| **Blockchain** | Besu dev local | Besu permissionado no cluster |
| **Kafka** | Container local | Kafka do cluster NASP |
| **Observabilidade** | Prometheus/Grafana local | Stack do cluster NASP |
| **Network** | Bridge network Docker | CNI do cluster (Calico) |
| **Storage** | Volumes Docker | StorageClass Kubernetes |

### 12.4 Troubleshooting E2E

**Problemas comuns:**

1. **Serviços não iniciam:**
   - Verificar logs: `docker compose logs <service-name>`
   - Verificar dependências no `docker-compose.yml`

2. **Kafka topics não criados:**
   - Executar manualmente: `docker exec trisla-kafka kafka-topics --create ...`

3. **Besu não conecta:**
   - Verificar se Besu está rodando: `curl http://localhost:8545`
   - Verificar variáveis de ambiente: `BESU_RPC_URL`, `BESU_CHAIN_ID`

4. **Testes E2E falham:**
   - Verificar se todos os serviços estão saudáveis
   - Verificar logs dos módulos
   - Verificar mensagens no Kafka

---

## 13. Integração com NASP e Fluxo Dev→NASP

### 13.1 Diferença entre Testes Locais e NASP

**Ambiente Local (Docker Compose):**
- Desenvolvimento e testes rápidos
- NASP Adapter em modo mock controlado
- Besu dev local
- Kafka container local
- Observabilidade local (Prometheus/Grafana)

**Ambiente NASP (Kubernetes):**
- Produção real
- NASP Adapter conectado a serviços NASP reais
- Besu permissionado no cluster
- Kafka do cluster NASP
- Observabilidade do cluster NASP

### 13.2 Onde Ajustar Values Files

**Para NASP (ambiente UNISINOS):**
- **Arquivo canônico:** `helm/trisla/values-nasp.yaml`
- Template disponível em: `docs/nasp/values-nasp.yaml`
- Guia completo: `docs/nasp/NASP_DEPLOY_RUNBOOK.md`

**Para produção genérica (fora NASP):**
- **Arquivo:** `helm/trisla/values-production.yaml`

**Guia completo:** `docs/VALUES_PRODUCTION_GUIDE.md`

**Script de preenchimento:** `scripts/fill_values_production.sh`

**⚠️ IMPORTANTE:**
- Nunca colocar IPs reais em documentação Markdown
- Usar FQDNs Kubernetes: `http://<SERVICE>.<NS>.svc.cluster.local:<PORT>`
- Valores reais apenas no arquivo YAML local (não versionado)

### 13.3 Playbooks Ansible e Scripts Auxiliares

**Localização dos Playbooks:** `ansible/playbooks/`

**Playbooks principais:**
- `pre-flight.yml` — Validações pré-deploy
- `setup-namespace.yml` — Criação de namespace
- `deploy-trisla-nasp.yml` — Deploy Helm
- `validate-cluster.yml` — Validação pós-deploy

**Inventory:** `ansible/inventory.yaml`
- Configurar nodes NASP (usar placeholders em docs)
- Variáveis de grupo para automação

**Scripts auxiliares:**
- `scripts/discover_nasp_endpoints.sh` — Descoberta de endpoints
- `scripts/fill_values_production.sh` — Preenchimento guiado
- `scripts/audit_ghcr_images.py` — Auditoria de imagens GHCR

### 13.4 Recomendação: Não Colocar IPs Reais em Markdown

**❌ NUNCA faça:**
```markdown
# Documentação
Endpoint: http://192.168.10.16:8080
```

**✅ SEMPRE faça:**
```markdown
# Documentação
Endpoint: http://<RAN_SERVICE>.<RAN_NS>.svc.cluster.local:<RAN_PORT>
```

**Valores reais apenas em:**
- `helm/trisla/values-production.yaml` (produção genérica, não versionado)
- `helm/trisla/values-nasp.yaml` (produção NASP, não versionado)
- `ansible/inventory.yaml` (arquivo local, não versionado)
- Variáveis de ambiente

---

## Conclusão

Este guia fornece todas as informações necessárias para desenvolvedores contribuírem com o TriSLA. Para dúvidas adicionais, consulte a documentação específica de cada módulo ou abra uma issue no GitHub.

**Última atualização:** 2025-11-22  
**Versão do documento:** 1.0.0

