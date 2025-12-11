#!/usr/bin/env bash
# FASE T3 — Testar Helm Chart trisla-besu isolado
# TriSLA - Verificação Pré-Publicação

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "📦 FASE T3 — Testar Helm Chart trisla-besu isolado"
echo "==================================================="
echo ""
echo "📁 Diretório do repositório: $REPO_ROOT"
echo "📁 Helm Chart: helm/trisla-besu/"
echo ""

cd "$REPO_ROOT"

# Verificar se helm está instalado
if ! command -v helm &> /dev/null; then
    echo "❌ ERRO: helm não está instalado"
    echo "   Instale com: https://helm.sh/docs/intro/install/"
    exit 1
fi

# 1. Validar sintaxe
echo "1️⃣ Validando sintaxe do Helm Chart..."
echo "   Comando: helm lint helm/trisla-besu"
echo ""

if helm lint helm/trisla-besu 2>&1; then
    echo ""
    echo "   ✅ helm lint executado sem erros"
    T3_LINT="APROVADO"
else
    echo ""
    echo "   ❌ helm lint encontrou erros"
    T3_LINT="REPROVADO"
fi
echo ""

# 2. Renderizar templates
echo "2️⃣ Renderizando templates (dry-run)..."
echo "   Comando: helm template trisla-besu helm/trisla-besu > /tmp/trisla-besu-rendered.yaml"
echo ""

if helm template trisla-besu helm/trisla-besu > /tmp/trisla-besu-rendered.yaml 2>&1; then
    echo "   ✅ Templates renderizados com sucesso"
    echo "   Arquivo gerado: /tmp/trisla-besu-rendered.yaml"
    T3_TEMPLATE="APROVADO"
else
    echo "   ❌ Falha ao renderizar templates"
    T3_TEMPLATE="REPROVADO"
    exit 1
fi
echo ""

# 3. Verificações no arquivo renderizado
echo "3️⃣ Verificando conteúdo do arquivo renderizado..."
echo ""

# Verificar imagem
if grep -q "hyperledger/besu:23.10.1" /tmp/trisla-besu-rendered.yaml; then
    echo "   ✅ Imagem correta: hyperledger/besu:23.10.1"
    T3_IMAGE="APROVADO"
else
    echo "   ❌ Imagem incorreta ou não encontrada"
    T3_IMAGE="REPROVADO"
fi

# Verificar portas
if grep -q "containerPort: 8545" /tmp/trisla-besu-rendered.yaml && \
   grep -q "containerPort: 8546" /tmp/trisla-besu-rendered.yaml && \
   grep -q "containerPort: 30303" /tmp/trisla-besu-rendered.yaml; then
    echo "   ✅ Portas corretas: 8545, 8546, 30303"
    T3_PORTS="APROVADO"
else
    echo "   ❌ Portas incorretas ou ausentes"
    T3_PORTS="REPROVADO"
fi

# Verificar volumes
if grep -q "/opt/besu/data" /tmp/trisla-besu-rendered.yaml && \
   grep -q "genesis.json" /tmp/trisla-besu-rendered.yaml; then
    echo "   ✅ Volumes configurados: /opt/besu/data e genesis.json"
    T3_VOLUMES="APROVADO"
else
    echo "   ❌ Volumes incorretos ou ausentes"
    T3_VOLUMES="REPROVADO"
fi

# Verificar flags inválidas
if grep -q "miner-strategy" /tmp/trisla-besu-rendered.yaml; then
    echo "   ❌ Flag inválida encontrada: --miner-strategy"
    T3_FLAGS="REPROVADO"
else
    echo "   ✅ Nenhuma flag inválida encontrada"
    T3_FLAGS="APROVADO"
fi

# Verificar comando Besu
if grep -q "/opt/besu/bin/besu" /tmp/trisla-besu-rendered.yaml || \
   grep -q "besu" /tmp/trisla-besu-rendered.yaml; then
    echo "   ✅ Comando Besu presente"
    T3_COMMAND="APROVADO"
else
    echo "   ❌ Comando Besu não encontrado"
    T3_COMMAND="REPROVADO"
fi

# Verificar ConfigMap genesis
if grep -q "kind: ConfigMap" /tmp/trisla-besu-rendered.yaml && \
   grep -q "genesis.json" /tmp/trisla-besu-rendered.yaml; then
    echo "   ✅ ConfigMap genesis.json presente"
    T3_CONFIGMAP="APROVADO"
else
    echo "   ❌ ConfigMap genesis.json não encontrado"
    T3_CONFIGMAP="REPROVADO"
fi

# Verificar Service
if grep -q "kind: Service" /tmp/trisla-besu-rendered.yaml && \
   grep -q "port: 8545" /tmp/trisla-besu-rendered.yaml; then
    echo "   ✅ Service configurado com porta 8545"
    T3_SERVICE="APROVADO"
else
    echo "   ❌ Service não encontrado ou incorreto"
    T3_SERVICE="REPROVADO"
fi

# Verificar PVC
if grep -q "kind: PersistentVolumeClaim" /tmp/trisla-besu-rendered.yaml; then
    echo "   ✅ PVC configurado"
    T3_PVC="APROVADO"
else
    echo "   ⚠️  PVC não encontrado (pode ser opcional)"
    T3_PVC="VERIFICAR"
fi
echo ""

# 4. Instruções para inspeção manual
echo "4️⃣ Instruções para inspeção manual:"
echo ""
echo "   Abra o arquivo renderizado:"
echo "   cat /tmp/trisla-besu-rendered.yaml"
echo ""
echo "   Ou use um editor:"
echo "   nano /tmp/trisla-besu-rendered.yaml"
echo "   # ou"
echo "   code /tmp/trisla-besu-rendered.yaml"
echo ""
echo "   Verifique manualmente:"
echo "   - Deployment com container hyperledger/besu:23.10.1"
echo "   - Volumes corretos (/opt/besu/data, genesis via ConfigMap)"
echo "   - Service com portas 8545, 8546, 30303"
echo "   - Nenhuma flag inválida (--miner-strategy, etc.)"
echo ""

# 5. Resultado final T3
echo "=========================================="
echo "📋 RESULTADO FASE T3"
echo "=========================================="
echo "helm lint:            $T3_LINT"
echo "helm template:        $T3_TEMPLATE"
echo "Imagem correta:       $T3_IMAGE"
echo "Portas corretas:      $T3_PORTS"
echo "Volumes corretos:     $T3_VOLUMES"
echo "Flags válidas:        $T3_FLAGS"
echo "Comando Besu:         $T3_COMMAND"
echo "ConfigMap genesis:    $T3_CONFIGMAP"
echo "Service:              $T3_SERVICE"
echo "PVC:                  $T3_PVC"
echo ""

if [ "$T3_LINT" = "APROVADO" ] && [ "$T3_TEMPLATE" = "APROVADO" ] && \
   [ "$T3_IMAGE" = "APROVADO" ] && [ "$T3_PORTS" = "APROVADO" ] && \
   [ "$T3_VOLUMES" = "APROVADO" ] && [ "$T3_FLAGS" = "APROVADO" ] && \
   [ "$T3_COMMAND" = "APROVADO" ] && [ "$T3_CONFIGMAP" = "APROVADO" ] && \
   [ "$T3_SERVICE" = "APROVADO" ]; then
    echo "✅ T3: APROVADO"
    echo ""
    echo "Helm Chart está válido e pronto para uso."
    exit 0
else
    echo "❌ T3: REPROVADO"
    echo ""
    echo "Algumas verificações falharam. Revise os erros acima."
    exit 1
fi
