#!/bin/bash
set -e

export TAG=v3.9.8
cd /home/porvir5g/gtp5g/trisla

echo '=== FASE 3 - Build e Push v3.9.8 ==='
echo 'Login no GHCR...'
echo "$GITHUB_TOKEN" | docker login ghcr.io -u abelisboa --password-stdin

echo ''
echo '[1/9] Building trisla-sem-csmf...'
docker build --no-cache -t ghcr.io/abelisboa/trisla-sem-csmf:$TAG apps/sem-csmf
docker push ghcr.io/abelisboa/trisla-sem-csmf:$TAG
echo '✅ trisla-sem-csmf concluído'

echo ''
echo '[2/9] Building trisla-ml-nsmf...'
docker build --no-cache -t ghcr.io/abelisboa/trisla-ml-nsmf:$TAG apps/ml-nsmf
docker push ghcr.io/abelisboa/trisla-ml-nsmf:$TAG
echo '✅ trisla-ml-nsmf concluído'

echo ''
echo '[3/9] Building trisla-decision-engine...'
docker build --no-cache -t ghcr.io/abelisboa/trisla-decision-engine:$TAG apps/decision-engine
docker push ghcr.io/abelisboa/trisla-decision-engine:$TAG
echo '✅ trisla-decision-engine concluído'

echo ''
echo '[4/9] Building trisla-nasp-adapter...'
docker build --no-cache -t ghcr.io/abelisboa/trisla-nasp-adapter:$TAG apps/nasp-adapter
docker push ghcr.io/abelisboa/trisla-nasp-adapter:$TAG
echo '✅ trisla-nasp-adapter concluído'

echo ''
echo '[5/9] Building trisla-sla-agent-layer...'
docker build --no-cache -t ghcr.io/abelisboa/trisla-sla-agent-layer:$TAG apps/sla-agent-layer
docker push ghcr.io/abelisboa/trisla-sla-agent-layer:$TAG
echo '✅ trisla-sla-agent-layer concluído'

echo ''
echo '[6/9] Building trisla-bc-nssmf...'
docker build --no-cache -t ghcr.io/abelisboa/trisla-bc-nssmf:$TAG apps/bc-nssmf
docker push ghcr.io/abelisboa/trisla-bc-nssmf:$TAG
echo '✅ trisla-bc-nssmf concluído'

echo ''
echo '[7/9] Building trisla-ui-dashboard...'
docker build --no-cache -t ghcr.io/abelisboa/trisla-ui-dashboard:$TAG apps/ui-dashboard
docker push ghcr.io/abelisboa/trisla-ui-dashboard:$TAG
echo '✅ trisla-ui-dashboard concluído'

echo ''
echo '[8/9] Building trisla-portal-backend...'
docker build --no-cache -t ghcr.io/abelisboa/trisla-portal-backend:$TAG trisla-portal/backend
docker push ghcr.io/abelisboa/trisla-portal-backend:$TAG
echo '✅ trisla-portal-backend concluído'

echo ''
echo '[9/9] Building trisla-portal-frontend...'
docker build --no-cache -t ghcr.io/abelisboa/trisla-portal-frontend:$TAG trisla-portal/frontend
docker push ghcr.io/abelisboa/trisla-portal-frontend:$TAG
echo '✅ trisla-portal-frontend concluído'

echo ''
echo '✅✅✅ FASE 3 CONCLUÍDA - Todos os builds e pushes finalizados! ✅✅✅'
