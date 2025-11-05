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

# 🧾 Verifica arquivo local
if [ ! -f "$README_PATH" ]; then
  echo "❌ ERRO: README.md não encontrado em ${README_PATH}."
  exit 1
fi

LINES=$(wc -l < "$README_PATH")
BYTES=$(wc -c < "$README_PATH")
echo "📄 README local → Linhas: $LINES | Bytes: $BYTES"

if [ "$BYTES" -lt 1000 ]; then
  echo "⚠️  Arquivo parece muito pequeno. Abortando para evitar upload vazio."
  exit 1
fi

# 🔍 Obtém SHA remoto
echo "📡 Obtendo SHA remoto..."
SHA_REMOTE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/${REPO}/contents/README.md" | jq -r .sha)

if [ "$SHA_REMOTE" != "null" ] && [ -n "$SHA_REMOTE" ]; then
  echo "🧾 SHA remoto encontrado: $SHA_REMOTE"
  echo "🗑️  Removendo README.md remoto..."
  curl -s -X DELETE \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
          \"message\": \"🧹 Removendo README antigo (hard reset)\",
          \"sha\": \"$SHA_REMOTE\",
          \"branch\": \"$BRANCH\"
        }" \
    "https://api.github.com/repos/${REPO}/contents/README.md" | jq .
else
  echo "ℹ️ Nenhum README remoto existente — prosseguindo com novo upload."
fi

sleep 3

# 📦 Codifica novo conteúdo
echo "📦 Gerando Base64 do README local..."
base64 -w0 "$README_PATH" > "$TMP_BASE64"
B64_SIZE=$(wc -c < "$TMP_BASE64")
echo "🧬 Tamanho codificado: $B64_SIZE bytes"

# 🚀 Publica novo conteúdo
echo "🚀 Publicando README.md v3.3.4 híbrido..."
RESP=$(curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
        \"message\": \"📚 Publicando README.md híbrido v3.3.4 (hard reset)\",
        \"content\": \"$(cat "$TMP_BASE64")\",
        \"branch\": \"$BRANCH\"
      }" \
  "https://api.github.com/repos/${REPO}/contents/README.md")

COMMIT_SHA=$(echo "$RESP" | jq -r .commit.sha)
NEW_SIZE=$(echo "$RESP" | jq -r .content.size)
NEW_HTML=$(echo "$RESP" | jq -r .content.html_url)

if [ "$COMMIT_SHA" = "null" ] || [ -z "$COMMIT_SHA" ]; then
  echo "❌ Erro na publicação! Resposta da API:"
  echo "$RESP" | jq .
  exit 1
fi

echo "✅ Publicação confirmada!"
echo "🧩 Commit: $COMMIT_SHA"
echo "📏 Tamanho remoto: $NEW_SIZE bytes"
echo "🔗 URL: $NEW_HTML"

# ⏳ Aguarda e valida CDN
sleep 5
echo "📡 Validando CDN..."
RAW_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/README.md"
RAW_BYTES=$(curl -sI "$RAW_URL?nocache=$(date +%s)" | awk '/[Cc]ontent-[Ll]ength/{print $2}' | tr -d '\r')

echo "📦 RAW CDN bytes: ${RAW_BYTES:-?}"
if [ "$RAW_BYTES" = "$BYTES" ]; then
  echo "🎯 CDN sincronizada com sucesso!"
else
  echo "⚠️  CDN ainda desatualizada. Tente novamente em 30–60s."
fi

echo "------------------------------------------------------------"
echo "🏁 README.md v3.3.4 híbrido — Hard Reset concluído!"
echo "------------------------------------------------------------"
