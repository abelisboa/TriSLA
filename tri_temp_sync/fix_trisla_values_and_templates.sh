#!/bin/bash
set -e

echo "==============================================================="
echo "  🔧 TRISLA — Patch Automático Global para Helm + values-nasp"
echo "==============================================================="

ROOT_DIR="$HOME/gtp5g/trisla"
VALUES="$ROOT_DIR/helm/trisla/values-nasp.yaml"
TEMPLATES="$ROOT_DIR/helm/trisla/templates"

echo "➡ Localizando módulos com deployment..."
MODULES=$(ls $TEMPLATES/deployment-* | sed 's#.*/deployment-##; s#.yaml##')

echo "Modules encontrados:"
echo "$MODULES"
echo

echo "➡ Garantindo que existe bloco .image.repository e .image.tag para cada módulo..."

for module in $MODULES; do
  echo "  - Corrigindo módulo: $module"
  if ! grep -q "^$module:" "$VALUES"; then
    cat <<MODBLOCK >> "$VALUES"

$module:
  image:
    repository: "localhost/trisla-$module"
    tag: "local"

MODBLOCK
  fi
done

echo "➡ Aplicando patch para replacements locais (forçando images localhost)"
sed -i 's#ghcr.io/abelisboa/#localhost/#g' "$VALUES"
sed -i 's/tag: latest/tag: local/g' "$VALUES"
sed -i 's/pullPolicy:.*/pullPolicy: IfNotPresent/g' "$VALUES"

echo
echo "➡ Validando templates do Helm..."
if ! helm template trisla "$ROOT_DIR/helm/trisla" -f "$VALUES" > "$ROOT_DIR/rendered.yaml" 2> "$ROOT_DIR/helm_errors.log"; then
    echo "❌ ERRO — Templates inválidos!"
    echo "Veja logs em: $ROOT_DIR/helm_errors.log"
    exit 1
fi

echo "✔ Helm template validado sem erros."
echo

echo "➡ Aplicando helm upgrade..."
helm upgrade --install trisla "$ROOT_DIR/helm/trisla" -n trisla -f "$VALUES" --cleanup-on-fail

echo "✔ Deploy aplicado com sucesso!"
echo "Use: kubectl get pods -n trisla -o wide"
