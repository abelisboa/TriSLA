#!/bin/bash
set -e

echo "🟦 FASE 0 — Validando diretório..."
cd /mnt/c/Users/USER/Documents/TriSLA-clean
pwd

echo ""
echo "🟦 FASE 2 — Validando arquivos..."
ls -lh apps/ui-dashboard/nginx.conf.template
ls -lh apps/ui-dashboard/Dockerfile

echo ""
echo "🟦 FASE 2.1 — Verificando se resolver está dentro do bloco server..."
if grep -A 5 "^server {" apps/ui-dashboard/nginx.conf.template | grep -q "resolver kube-dns"; then
    echo "✅ Resolver encontrado DENTRO do bloco server"
else
    echo "❌ Resolver NÃO encontrado DENTRO do bloco server"
    exit 1
fi

echo ""
echo "🟦 FASE 4 — Rebuild local v3.7.9 (sem cache)..."
cd apps/ui-dashboard
docker build --no-cache -t trisla-ui-dashboard:v3.7.9 .

echo ""
echo "🟦 FASE 4.1 — Validando criação da imagem..."
docker images | grep trisla-ui-dashboard

echo ""
echo "🟦 FASE 5 — Teste local da imagem..."
echo "Parando container anterior se existir..."
docker stop ui_test 2>/dev/null || true
docker rm ui_test 2>/dev/null || true

echo "Iniciando container de teste..."
docker run --rm -d \
  --name ui_test \
  -p 18080:80 \
  -e API_BACKEND_HOST=localhost \
  -e API_BACKEND_PORT=8082 \
  trisla-ui-dashboard:v3.7.9

echo "Aguardando inicialização..."
sleep 3

echo ""
echo "🟦 FASE 5.1 — Verificando logs..."
docker logs ui_test --tail=200

echo ""
echo "🟦 FASE 5.2 — Testando healthcheck..."
curl -v http://localhost:18080/healthz || echo "❌ Healthcheck falhou"

echo ""
echo "🟦 FASE 5.3 — Verificando erros críticos nos logs..."
if docker logs ui_test 2>&1 | grep -iE "host not found|nginx: \[emerg\]|upstream not found"; then
    echo "❌ ERROS CRÍTICOS ENCONTRADOS NOS LOGS"
    docker stop ui_test
    exit 1
else
    echo "✅ Nenhum erro crítico encontrado nos logs"
fi

echo ""
echo "🟦 FASE 5.4 — Aguardando 2 minutos para validar estabilidade..."
sleep 120

echo ""
echo "🟦 FASE 5.5 — Verificando logs finais..."
docker logs ui_test --tail=50

echo ""
echo "🟦 FASE 5.6 — Parando container de teste..."
docker stop ui_test

echo ""
echo "✅ TESTE LOCAL CONCLUÍDO COM SUCESSO"

