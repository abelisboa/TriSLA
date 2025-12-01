#!/usr/bin/env bash
# Verifica e tenta iniciar Docker Desktop no Windows

if command -v docker &> /dev/null; then
    if docker ps &> /dev/null; then
        echo "[TriSLA] ✅ Docker está rodando."
        exit 0
    else
        echo "[TriSLA] ⚠️  Docker instalado mas não está rodando."
        
        # Tentar iniciar Docker Desktop no Windows
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || -n "$WSL_DISTRO_NAME" ]]; then
            echo "[TriSLA] Tentando iniciar Docker Desktop..."
            # Caminho comum do Docker Desktop no Windows
            if [ -f "/c/Program Files/Docker/Docker/Docker Desktop.exe" ]; then
                "/c/Program Files/Docker/Docker/Docker Desktop.exe" &
                echo "[TriSLA] Aguardando Docker Desktop iniciar (30s)..."
                sleep 30
                
                # Verificar novamente
                for i in {1..10}; do
                    if docker ps &> /dev/null; then
                        echo "[TriSLA] ✅ Docker iniciado com sucesso!"
                        exit 0
                    fi
                    echo "[TriSLA] Esperando Docker... Tentativa $i/10"
                    sleep 3
                done
            fi
        fi
        
        echo "❌ ERRO: Docker não está rodando."
        echo "   Por favor, inicie o Docker Desktop manualmente e tente novamente."
        exit 1
    fi
else
    echo "❌ ERRO: Docker não está instalado."
    exit 1
fi

