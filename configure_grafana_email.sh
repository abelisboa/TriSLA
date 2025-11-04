#!/bin/bash
# Configurar Email no Grafana para Reset de Senha

set -e

echo "=========================================="
echo "📧 Configuração de Email no Grafana"
echo "=========================================="
echo ""

# Obter pod do Grafana
GRAFANA_POD=$(kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana -o jsonpath='{.items[0].metadata.name}')
echo "Pod do Grafana: $GRAFANA_POD"
echo ""

# Ler informações de email
read -p "Digite seu email para receber reset de senha: " USER_EMAIL
read -p "Digite o servidor SMTP (ex: smtp.gmail.com): " SMTP_SERVER
read -p "Digite a porta SMTP (ex: 587 para TLS, 465 para SSL): " SMTP_PORT
read -p "Digite seu usuário SMTP (ou email): " SMTP_USER
read -s -p "Digite sua senha SMTP (ou app password): " SMTP_PASSWORD
echo ""
read -p "Usar TLS? (s/n, padrão: s): " USE_TLS
USE_TLS=${USE_TLS:-s}

echo ""
echo "📧 Configurando email no Grafana..."
echo ""

# Criar ConfigMap com configurações de email
kubectl create configmap grafana-smtp-config -n monitoring \
  --from-literal=GF_SMTP_ENABLED=true \
  --from-literal=GF_SMTP_HOST="${SMTP_SERVER}:${SMTP_PORT}" \
  --from-literal=GF_SMTP_USER="${SMTP_USER}" \
  --from-literal=GF_SMTP_PASSWORD="${SMTP_PASSWORD}" \
  --from-literal=GF_SMTP_FROM_ADDRESS="${SMTP_USER}" \
  --from-literal=GF_SMTP_FROM_NAME="Grafana TriSLA" \
  --dry-run=client -o yaml | kubectl apply -f -

if [ "$USE_TLS" = "s" ] || [ "$USE_TLS" = "S" ]; then
    kubectl patch configmap grafana-smtp-config -n monitoring --type merge \
      -p '{"data":{"GF_SMTP_SKIP_VERIFY":"true"}}'
fi

echo "✅ ConfigMap de email criado"
echo ""

# Opção 1: Criar usuário novo com email
echo "👤 Criando usuário novo com email configurado..."
kubectl exec -n monitoring $GRAFANA_POD -c grafana -- grafana cli admin create-user \
  --email "${USER_EMAIL}" \
  --name "Admin" \
  --password "TriSLA2025!" \
  --org-role Admin || echo "Usuário pode já existir"
echo ""

echo "✅ Configuração concluída!"
echo ""
echo "📋 Informações de login:"
echo "   Email: ${USER_EMAIL}"
echo "   Senha temporária: TriSLA2025!"
echo ""
echo "🔐 Próximos passos:"
echo "   1. Reiniciar o pod do Grafana para aplicar configurações de email:"
echo "      kubectl delete pod -n monitoring $GRAFANA_POD"
echo ""
echo "   2. Aguardar pod reiniciar e então fazer login"
echo ""
echo "   3. Após login, alterar senha e configurar email no perfil"
echo ""
echo "   4. Testar reset de senha via email"
echo ""




