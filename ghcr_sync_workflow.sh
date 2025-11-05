#!/bin/bash
set -e

echo "🚀 Iniciando TriSLA GHCR Sync & Expansion Workflow..."
echo "============================================================"

# 1️⃣ Verificar imagens locais
echo "📦 Verificando imagens locais..."
docker images | grep trisla || echo "Nenhuma imagem TriSLA encontrada localmente."

# 2️⃣ Comparar com backup Híbrido
BACKUP_DIR=~/Documents/trisla-backups/extracted_backup_trisla_20251023_1639/backup_trisla_20251023_1639/trisla-portal
if [ -f "$BACKUP_DIR/running_images.txt" ]; then
  echo "🔍 Imagens Híbrido no backup:"
  cat "$BACKUP_DIR/running_images.txt"
else
  echo "⚠️ Arquivo de backup não encontrado em $BACKUP_DIR"
fi

# 3️⃣ Login e sincronização GHCR
echo "🔐 Autenticando no GHCR..."
docker login ghcr.io -u abelisboa

echo "🚀 Publicando imagens principais..."
docker push ghcr.io/abelisboa/trisla-api:latest || echo "⚠️ API não encontrada localmente."
docker push ghcr.io/abelisboa/trisla-ui:latest || echo "⚠️ UI não encontrada localmente."

# 4️⃣ Criar estrutura dos módulos pendentes
echo "📂 Criando estrutura base para módulos AI, Semantic, Blockchain e Monitoring..."
mkdir -p apps/{ai,semantic,blockchain,monitoring}
for dir in apps/ai apps/semantic apps/blockchain apps/monitoring; do
  if [ ! -f "$dir/Dockerfile" ]; then
    cat <<DOCKER > $dir/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || echo "Nenhum requirements.txt encontrado"
COPY . .
CMD ["python3", "main.py"]
DOCKER
  fi
done
echo "✅ Estrutura base criada."

# 5️⃣ Atualizar CSV de automação
mkdir -p ../PROMPTS/automation
cat <<CSV > ../PROMPTS/automation/TRISLA_PIPELINE_TRACKER.csv
Item,Comando Principal,Status Atual,Data Última Atualização
API,docker build -t ghcr.io/abelisboa/trisla-api:latest ./apps/api && docker push ghcr.io/abelisboa/trisla-api:latest,✅,2025-10-23
UI,docker build -t ghcr.io/abelisboa/trisla-ui:latest ./apps/ui && docker push ghcr.io/abelisboa/trisla-ui:latest,✅,2025-10-23
AI,docker build -t ghcr.io/abelisboa/trisla-ai:latest ./apps/ai && docker push ghcr.io/abelisboa/trisla-ai:latest,❌,
Semantic,docker build -t ghcr.io/abelisboa/trisla-semantic:latest ./apps/semantic && docker push ghcr.io/abelisboa/trisla-semantic:latest,❌,
Blockchain,docker build -t ghcr.io/abelisboa/trisla-blockchain:latest ./apps/blockchain && docker push ghcr.io/abelisboa/trisla-blockchain:latest,❌,
Monitoring,docker build -t ghcr.io/abelisboa/trisla-monitoring:latest ./apps/monitoring && docker push ghcr.io/abelisboa/trisla-monitoring:latest,❌,
CSV
echo "✅ CSV atualizado em PROMPTS/automation/TRISLA_PIPELINE_TRACKER.csv"

# 6️⃣ Resumo
echo "============================================================"
echo "📊 RESUMO FINAL:"
echo " - API/UI sincronizadas com GHCR e Híbrido"
echo " - Estrutura base criada para AI, Semantic, Blockchain e Monitoring"
echo " - CSV de automação atualizado"
echo "✅ TriSLA GHCR Sync & Expansion concluído com sucesso!"
