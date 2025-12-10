# Backend - TriSLA Observability Portal v4.0

Backend desenvolvido com FastAPI (Python 3.11).

## 🚀 Instalação

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 🛠️ Desenvolvimento

```bash
# Criar arquivo .env baseado em .env.example
cp .env.example .env

# Executar
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse [http://localhost:8000/docs](http://localhost:8000/docs) para ver a documentação Swagger.

## 📁 Estrutura

```
src/
├── main.py              # FastAPI app
├── config.py            # Configurações
├── routers/             # Endpoints da API
│   ├── health.py
│   ├── modules.py
│   ├── prometheus.py
│   ├── loki.py
│   ├── tempo.py
│   ├── intents.py
│   ├── contracts.py
│   ├── slas.py
│   ├── xai.py
│   └── slos.py
├── services/            # Lógica de negócio
│   ├── health.py
│   ├── modules.py
│   ├── prometheus.py
│   ├── loki.py
│   ├── tempo.py
│   ├── contracts.py
│   ├── slas.py
│   ├── xai.py
│   ├── intents.py
│   ├── slos.py
│   └── trisla.py
├── models/              # Database models
│   ├── database.py
│   └── contract.py
├── schemas/             # Pydantic schemas
│   ├── health.py
│   ├── contracts.py
│   ├── slas.py
│   ├── xai.py
│   └── common.py
└── repositories/         # Database access (futuro)
```

## 🔌 Endpoints Principais

### Health & Status
- `GET /api/v1/health/global` - Saúde global
- `GET /api/v1/modules` - Lista de módulos

### Observabilidade
- `GET /api/v1/prometheus/query` - Query Prometheus
- `GET /api/v1/logs` - Logs do Loki
- `GET /api/v1/traces` - Traces do Tempo

### Contracts
- `GET /api/v1/contracts` - Lista contratos
- `GET /api/v1/contracts/{id}` - Detalhes do contrato
- `POST /api/v1/contracts` - Criar contrato

### SLAs
- `POST /api/v1/slas/create/pln` - Criar SLA via PLN
- `POST /api/v1/slas/create/template` - Criar SLA via template
- `POST /api/v1/slas/create/batch` - Criar SLAs em lote

### XAI
- `GET /api/v1/xai/explanations` - Lista explicações
- `POST /api/v1/xai/explain` - Gerar explicação

## 🗄️ Database

Por padrão, usa SQLite (`trisla_portal.db`). Para PostgreSQL, configure `DATABASE_URL` no `.env`.

## 📝 Notas

- OpenTelemetry integrado para traces
- Suporte a Prometheus, Loki e Tempo
- Contract Manager com SQLAlchemy
- Integração com módulos TriSLA via HTTP







