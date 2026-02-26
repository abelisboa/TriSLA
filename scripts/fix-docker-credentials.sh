#!/bin/bash

echo "============================================================"
echo "🔧 TriSLA — Fix Docker Credentials"
echo "============================================================"

echo ""
echo "1️⃣ Verificando Docker..."
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker não está rodando!"
  echo "   Inicie o Docker Desktop e tente novamente."
  exit 1
fi
echo "✔ Docker está rodando"

echo ""
echo "2️⃣ Testando pull de imagem pública..."
if docker pull python:3.10-slim; then
  echo "✔ Pull funcionou! Credenciais OK"
  exit 0
else
  echo "⚠️ Pull falhou. Tentando corrigir..."
fi

echo ""
echo "3️⃣ Limpando credenciais antigas..."
if [ -f ~/.docker/config.json ]; then
  echo "   Backup de ~/.docker/config.json criado"
  cp ~/.docker/config.json ~/.docker/config.json.backup
  echo "   ⚠️ Para remover credenciais manualmente, edite ~/.docker/config.json"
  echo "   Ou remova o arquivo completamente: rm ~/.docker/config.json"
fi

echo ""
echo "4️⃣ Fazendo logout do Docker Hub..."
docker logout 2>/dev/null || true

echo ""
echo "5️⃣ Tentando pull novamente (sem credenciais)..."
if docker pull python:3.10-slim; then
  echo "✔ Pull funcionou após limpeza!"
  exit 0
else
  echo ""
  echo "❌ Ainda falhando. Possíveis causas:"
  echo "   • Problema de rede/firewall"
  echo "   • Docker Desktop não configurado corretamente"
  echo "   • Proxy bloqueando acesso ao Docker Hub"
  echo ""
  echo "💡 Soluções:"
  echo "   1. Verificar conexão: curl -I https://hub.docker.com"
  echo "   2. Reiniciar Docker Desktop"
  echo "   3. Verificar configurações de proxy no Docker Desktop"
  exit 1
fi

