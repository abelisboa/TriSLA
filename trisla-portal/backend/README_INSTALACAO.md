# Instalação de Dependências - Backend TriSLA Portal

## Problema de Conflito de Dependências Resolvido

Havia um conflito entre as versões do OpenTelemetry:
- `opentelemetry-sdk 1.22.0` requer `opentelemetry-semantic-conventions==0.43b0`
- `opentelemetry-instrumentation-fastapi 0.42b0` requer `opentelemetry-semantic-conventions==0.42b0`

**Solução:** Ajustamos as versões para usar `1.21.0` e `0.41b0` que são compatíveis entre si.

## Instalação Rápida

### Opção 1: Script Automático (Recomendado)

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend
bash instalar_dependencias.sh
```

### Opção 2: Instalação Manual

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

## Verificar Instalação

```bash
source venv/bin/activate
python -c "import opentelemetry; print('✅ OpenTelemetry instalado!')"
python -c "import fastapi; print('✅ FastAPI instalado!')"
```

## Iniciar o Backend

Após instalar as dependências:

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend
source venv/bin/activate
python3 run.py
```

Ou use o portal manager:

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean
bash scripts/portal_manager.sh
```

## Dependências Principais

- **FastAPI 0.109.0** - Framework web
- **Uvicorn 0.27.0** - Servidor ASGI
- **OpenTelemetry 1.21.0** - Observabilidade
- **SQLAlchemy 2.0.25** - ORM
- E outras bibliotecas (veja `requirements.txt`)

## Problemas?

Se ainda houver conflitos de dependências:

1. Tente atualizar o pip: `pip install --upgrade pip setuptools wheel`
2. Limpe o cache: `pip cache purge`
3. Reinstale: `pip install --force-reinstall -r requirements.txt`


