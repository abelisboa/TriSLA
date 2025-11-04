#!/bin/bash
set -e
echo "🔍 Verificação TriSLA Setup"

echo "📦 Verificando imagens locais..."
docker images | grep trisla || echo "Nenhuma imagem local encontrada."

echo "📁 Verificando estrutura apps/"
tree -L 2 apps || echo "⚠️ Estrutura incompleta."

echo "📜 Verificando CSV de automação..."
if [ -f ../PROMPTS/automation/TRISLA_PIPELINE_TRACKER.csv ]; then
  cat ../PROMPTS/automation/TRISLA_PIPELINE_TRACKER.csv
else
  echo "⚠️ CSV não encontrado!"
fi

echo "✅ Verificação concluída."
