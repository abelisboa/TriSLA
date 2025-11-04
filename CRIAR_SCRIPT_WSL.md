# 📝 Como Criar o Script no WSL

O arquivo já existe em `scripts-wsl/start-backend-and-open.sh` no Windows, mas precisa estar disponível no WSL.

## 🔧 Opção 1: Copiar do Windows para WSL

Execute no **WSL**:

```bash
cd ~/trisla-dashboard-local

# Se o diretório scripts-wsl não existir
mkdir -p scripts-wsl

# Copiar o script do Windows (se estiver no mesmo projeto)
cp /mnt/c/Users/USER/Documents/trisla-deploy/trisla-dashboard-local/scripts-wsl/start-backend-and-open.sh scripts-wsl/

# Dar permissão de execução
chmod +x scripts-wsl/start-backend-and-open.sh
```

## 🔧 Opção 2: Criar Diretamente no WSL

Execute no **WSL**:

```bash
cd ~/trisla-dashboard-local
mkdir -p scripts-wsl

cat > scripts-wsl/start-backend-and-open.sh << 'EOF'
#!/bin/bash
# Script para iniciar backend e abrir no navegador
# Uso: ./scripts-wsl/start-backend-and-open.sh

set -e

cd ~/trisla-dashboard-local

echo "🚀 Iniciando TriSLA Backend..."
echo ""

if [ ! -f "backend/main.py" ]; then
    echo "❌ Erro: Execute este script da raiz do projeto"
    exit 1
fi

if [ ! -d "backend/venv" ]; then
    echo "❌ Erro: Virtual environment não encontrado"
    echo "   Execute: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Porta 5000 já está em uso!"
    read -p "Deseja abrir o navegador mesmo assim? (S/N) " response
    if [ "$response" = "S" ] || [ "$response" = "s" ]; then
        wslview "http://localhost:5000" 2>/dev/null || cmd.exe /c start "http://localhost:5000" 2>/dev/null || echo "Abra manualmente: http://localhost:5000"
    fi
    exit 0
fi

cd backend
source venv/bin/activate

echo "2️⃣ Iniciando backend FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 5000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!

echo "   ✅ Backend iniciado (PID: $BACKEND_PID)"
echo ""
echo "3️⃣ Aguardando backend iniciar..."
sleep 3

MAX_RETRIES=10
RETRY_COUNT=0
BACKEND_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$BACKEND_READY" = false ]; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        BACKEND_READY=true
        echo "   ✅ Backend está respondendo!"
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "   ⏳ Tentativa $RETRY_COUNT/$MAX_RETRIES..."
        sleep 1
    fi
done

echo ""
echo "4️⃣ Abrindo navegador em http://localhost:5000..."

wslview "http://localhost:5000" 2>/dev/null || cmd.exe /c start "http://localhost:5000" 2>/dev/null || echo "⚠️  Abra manualmente: http://localhost:5000"

echo ""
echo "✅ Backend rodando!"
echo "📊 URLs: http://localhost:5000 | http://localhost:5000/docs"
echo "📝 Logs: tail -f ~/trisla-dashboard-local/backend.log"
echo "🛑 Parar: kill $BACKEND_PID"

echo $BACKEND_PID > ../backend.pid
EOF

chmod +x scripts-wsl/start-backend-and-open.sh
```

## ✅ Testar

Após criar, execute:

```bash
./scripts-wsl/start-backend-and-open.sh
```

## 🎯 O Que Ocorre

1. ✅ Verifica se backend/main.py existe
2. ✅ Verifica se venv existe
3. ✅ Verifica se porta 5000 está livre
4. ✅ Inicia backend em background
5. ✅ Aguarda backend estar pronto
6. ✅ Abre navegador automaticamente

---

**Pronto! O script deve funcionar no WSL agora!** 🎉





