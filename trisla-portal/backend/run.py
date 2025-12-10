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
