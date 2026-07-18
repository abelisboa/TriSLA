# INÍCIO RÁPIDO — BACKEND TRI-SLA PORTAL LIGHT

## Início rápido

```bash
cd apps/portal-backend
bash instalar_dependencias.sh
bash start_backend.sh
```

---

## Passos

### 1. Instalar dependências

```bash
bash instalar_dependencias.sh
```

### 2. Iniciar o backend

```bash
bash start_backend.sh
```

---

## Validação rápida

```bash
curl --fail http://localhost:8001/health
```

---

## Solução de problemas

Recrie o ambiente público e reinstale as dependências:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Depois, execute novamente `bash start_backend.sh`.

---

**Backend:** http://localhost:8001
