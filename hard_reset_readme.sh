#!/bin/bash
# ============================================================
# 🧨 HARD RESET + PUBLICAÇÃO README.md (TriSLA v3.3.4 híbrido)
# ============================================================

set -euo pipefail

REPO="abelisboa/TriSLA"
BRANCH="main"
README_PATH="./README.md"
TMP_BASE64="/tmp/readme64.txt"

echo "------------------------------------------------------------"
echo "🚀 HARD RESET + PUBLICAÇÃO — README.md (${REPO})"
echo "------------------------------------------------------------"

# 🔑 Verifica token
if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "❌ ERRO: variável GITHUB_TOKEN não definida."
  echo "Use: export GITHUB_TOKEN=<token>"
  exit 1
fi

# 📁 Verifica se o README existe
if [ ! -f "$README_PATH" ]; then
  echo "❌ ERRO: README.md não encontrado em $README_PATH"
  exit 1
fi

# 🔍 Mostra resumo
LINES=$(wc -l < "$README_PATH")
BYTES=$(wc -c < "$README_PATH")
echo "📘 README.md encontrado — $LINES linhas | $BYTES bytes"

# 🧱 Codifica em Base64
base64 -w0 "$README_PATH" > "$TMP_BASE64"

# 🔍 Obtém SHA remoto (se existir)
SHA_REMOTE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$REPO/contents/README.md | jq -r .sha)

# 🚮 Remove versão antiga se houver
if [ "$SHA_REMOTE" != "null" ]; then
  echo "🗑️  Removendo README remoto anterior..."
  curl -s -X DELETE \
    -H "Authorization: token $GITHUB_TOKEN" \
    -d "{\"message\":\"��️ Removendo README antigo\",\"sha\":\"$SHA_REMOTE\"}" \
    https://api.github.com/repos/$REPO/contents/README.md > /dev/null
  sleep 3
fi

# 🚀 Publica novo conteúdo
echo "📤 Enviando novo README.md..."
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
        \"message\": \"📚 Publicando README.md híbrido v3.3.4 (recriado)\",
        \"content\": \"$(cat $TMP_BASE64)\",
        \"branch\": \"$BRANCH\"
      }" \
  https://api.github.com/repos/$REPO/contents/README.md | jq .

echo "------------------------------------------------------------"
echo "✅ Publicação completa do README.md concluída!"
echo "🌐 https://github.com/$REPO"
echo "------------------------------------------------------------"
