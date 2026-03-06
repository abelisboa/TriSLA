# PATCH COMPLETO - BACKEND TRI-SLA PORTAL

## ✅ STATUS: TODAS AS CORREÇÕES JÁ APLICADAS

---

## 📋 BLOCO A — DIFERENÇAS (PATCH)

### Arquivo modificado: `backend/src/main.py`

**Mudança aplicada:** Removido bloco `if __name__ == "__main__"` que causava conflito com `run.py`

```diff
--- a/backend/src/main.py (ANTES)
+++ b/backend/src/main.py (DEPOIS)
@@ -133,11 +133,0 @@ async def global_exception_handler(request: Request, exc: Exception):
-    
-    
-    
-    if __name__ == "__main__":
-        import uvicorn
-        uvicorn.run(
-            "src.main:app",
-            host=settings.api_host,
-            port=settings.api_port,
-            reload=settings.api_reload,
-        )
```

**Motivo:** O bloco de execução direta no `main.py` conflitava com o launcher profissional `run.py` e podia causar problemas de reload.

---

## 📄 BLOCO B — ARQUIVOS FINAIS COMPLETOS

### Arquivo 1: `backend/src/main.py` (FINAL - SEM BLOCO DE EXECUÇÃO)

O arquivo está correto. O bloco `if __name__ == "__main__"` foi removido.

### Arquivo 2: `backend/run.py` (JÁ EXISTE E ESTÁ CORRETO)

```python
"""
Launcher profissional para o backend TriSLA Portal
Evita que o reloader do Uvicorn varre o diretório venv
"""
import uvicorn
import os
import sys
from pathlib import Path

# Diretório base do backend
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
VENV_DIR = BASE_DIR / "venv"

# Detectar modo de execução
MODE = os.getenv("BACKEND_MODE", "dev").lower()  # dev ou prod
HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
PORT = int(os.getenv("BACKEND_PORT", "8001"))


def is_wsl2():
    """Detecta se está rodando no WSL2"""
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower() or "wsl" in f.read().lower()
    except:
        return False


def run_dev():
    """Modo desenvolvimento com reload seguro"""
    print("=" * 60)
    print("🚀 TriSLA Portal Backend - Modo DESENVOLVIMENTO")
    print("=" * 60)
    print(f"Host: {HOST}")
    print(f"Porta: {PORT}")
    print(f"Reload: Ativado (apenas em {SRC_DIR})")
    print(f"Venv excluído: {VENV_DIR}")
    
    if is_wsl2():
        print("\n⚠️  WSL2 detectado - Monitore uso de memória")
    
    print("=" * 60)
    print()
    
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        reload_dirs=[str(SRC_DIR)],
        reload_excludes=[
            str(VENV_DIR),
            "*/venv/*",
            "*/__pycache__/*",
            "*.pyc",
            "*.pyo",
        ],
        log_level="info",
    )


def run_prod():
    """Modo produção (NASP-ready) sem reload"""
    print("=" * 60)
    print("🏭 TriSLA Portal Backend - Modo PRODUÇÃO (NASP)")
    print("=" * 60)
    print(f"Host: 0.0.0.0")
    print(f"Porta: {PORT}")
    print(f"Reload: Desativado")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="info",
        workers=1,  # NASP pode escalar via Kubernetes
    )


if __name__ == "__main__":
    # Verificar se estamos no diretório correto
    if not SRC_DIR.exists():
        print(f"❌ ERRO: Diretório {SRC_DIR} não encontrado!")
        print(f"   Execute este script a partir de: {BASE_DIR}")
        sys.exit(1)
    
    # Executar conforme modo
    if MODE == "prod" or MODE == "production":
        run_prod()
    else:
        run_dev()
```

### Arquivo 3: `scripts/portal_manager.sh` (JÁ EXISTE E ESTÁ CORRETO)

O script já usa `run.py` corretamente nas opções 1 (DEV) e 7 (PROD).

---

## ✅ BLOCO C — VALIDAÇÃO OPERACIONAL

### Teste 1: Verificar import do módulo

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend
python3 -c "from src.main import app; print('✓ Import OK')"
```

**Resultado esperado:** `✓ Import OK`

### Teste 2: Verificar CORS (OPTIONS)

```bash
curl -X OPTIONS http://127.0.0.1:8001/api/v1/modules -I
```

**Resultado esperado:**
```
HTTP/1.1 200 OK
access-control-allow-origin: *
access-control-allow-methods: *
access-control-allow-headers: *
```

### Teste 3: Teste endpoint health

```bash
curl http://127.0.0.1:8001/api/v1/health
```

**Resultado esperado:**
```json
{"status": "healthy"}
```

### Teste 4: Teste endpoint modules

```bash
curl http://127.0.0.1:8001/api/v1/modules
```

**Resultado esperado:**
```json
{
  "modules": [...],
  "source": "nasp",
  "updated_at": "..."
}
```

### Teste 5: Verificar que não há OOM

Ao iniciar o backend com `python3 run.py`, verificar nos logs:
- ❌ NÃO deve aparecer: `OSError: [Errno 12] Cannot allocate memory`
- ✅ Deve aparecer: `Reload: Ativado (apenas em .../src)`
- ✅ Deve aparecer: `Venv excluído: .../venv`

---

## 🎯 RESUMO DAS CORREÇÕES

| Item | Status | Descrição |
|------|--------|-----------|
| Removido `if __name__` do `main.py` | ✅ CONCLUÍDO | Bloco removido para evitar conflitos |
| `run.py` configurado | ✅ JÁ EXISTIA | Reload seguro com exclusão de venv |
| `portal-manager.sh` atualizado | ✅ JÁ EXISTIA | Usa `run.py` corretamente |
| CORS configurado | ✅ CONCLUÍDO | `allow_origins=["*"]` |
| Cache limpo | ✅ CONCLUÍDO | `__pycache__` removido |

---

## 📝 INSTRUÇÕES PARA TESTE

### Passo 1: Limpar cache (se necessário)

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

### Passo 2: Usar portal-manager

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/scripts
./portal_manager.sh
```

**Opções:**
- **Opção 1**: Iniciar Backend (DEV - com reload seguro)
- **Opção 7**: Iniciar Backend (PROD - NASP sem reload)

### Passo 3: Testar endpoints

```bash
# Health check
curl http://127.0.0.1:8001/api/v1/health

# Modules
curl http://127.0.0.1:8001/api/v1/modules

# CORS
curl -X OPTIONS http://127.0.0.1:8001/api/v1/modules -I
```

---

## ✅ CORREÇÕES APLICADAS

1. ✅ **Bloco `if __name__ == "__main__"` removido do `main.py`**
   - Evita conflito com `run.py`
   - Força uso do launcher profissional

2. ✅ **`run.py` já estava correto**
   - Reload limitado a `src/`
   - Exclusão explícita de `venv`
   - Suporte dev e prod
   - Detecção WSL2

3. ✅ **`portal-manager.sh` já estava correto**
   - Usa `run.py` para iniciar backend
   - Suporta modo dev (opção 1) e prod (opção 7)

4. ✅ **CORS configurado**
   - `allow_origins=["*"]` permite todas as origens
   - Headers e métodos permitidos

---

**PATCH COMPLETO GERADO — APLIQUE E TESTE**

Todas as correções foram aplicadas. O backend está pronto para uso seguro.
