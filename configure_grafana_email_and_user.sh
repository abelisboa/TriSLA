#!/bin/bash
# Configurar Email no Grafana e Criar Usuário com Email

set -e

echo "=========================================="
echo "📧 Configuração de Email no Grafana"
echo "   Criar Usuário com Email"
echo "=========================================="
echo ""

# Obter pod do Grafana
GRAFANA_POD=$(kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana -o jsonpath='{.items[0].metadata.name}')
echo "Pod do Grafana: $GRAFANA_POD"
echo ""

# Solicitar informações
read -p "Digite seu email para receber reset de senha: " USER_EMAIL
read -p "Digite o servidor SMTP (ex: smtp.gmail.com): " SMTP_SERVER
read -p "Digite a porta SMTP (ex: 587 para TLS): " SMTP_PORT
SMTP_PORT=${SMTP_PORT:-587}

read -p "Digite seu usuário SMTP (seu email): " SMTP_USER
SMTP_USER=${SMTP_USER:-$USER_EMAIL}

read -s -p "Digite sua senha SMTP (ou app password para Gmail): " SMTP_PASSWORD
echo ""

echo ""
echo "📧 Configurando email no Grafana..."
echo ""

# Criar ou atualizar Secret com configurações SMTP
kubectl create secret generic grafana-smtp -n monitoring \
  --from-literal=GF_SMTP_ENABLED=true \
  --from-literal=GF_SMTP_HOST="${SMTP_SERVER}" \
  --from-literal=GF_SMTP_PORT="${SMTP_PORT}" \
  --from-literal=GF_SMTP_USER="${SMTP_USER}" \
  --from-literal=GF_SMTP_PASSWORD="${SMTP_PASSWORD}" \
  --from-literal=GF_SMTP_FROM_ADDRESS="${SMTP_USER}" \
  --from-literal=GF_SMTP_FROM_NAME="Grafana TriSLA" \
  --from-literal=GF_SMTP_SKIP_VERIFY=true \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✅ Secret de email criado"
echo ""

# Aplicar configurações SMTP via variáveis de ambiente no deployment
echo "🔧 Aplicando configurações SMTP no deployment..."
kubectl patch deployment monitoring-grafana -n monitoring --type='json' \
  -p='[
    {
      "op": "add",
      "path": "/spec/template/spec/containers/0/env/-",
      "value": {
        "name": "GF_SMTP_ENABLED",
        "value": "true"
      }
    },
    {
      "op": "add",
      "path": "/spec/template/spec/containers/0/env/-",
      "value": {
        "name": "GF_SMTP_HOST",
        "value": "'"${SMTP_SERVER}"'"
      }
    },
    {
      "op": "add",
      "path": "/spec/template/spec/containers/0/env/-",
      "value": {
        "name": "GF_SMTP_PORT",
        "value": "'"${SMTP_PORT}"'"
      }
    },
    {
      "op": "add",
      "path": "/spec/template/spec/containers/0/env/-",
      "value": {
        "name": "GF_SMTP_USER",
        "valueFrom": {
          "secretKeyRef": {
            "name": "grafana-smtp",
            "key": "GF_SMTP_USER"
          }
        }
      }
    },
    {
      "op": "add",
      "path": "/spec/template/spec/containers/0/env/-",
      "value": {
        "name": "GF_SMTP_PASSWORD",
        "valueFrom": {
          "secretKeyRef": {
            "name": "grafana-smtp",
            "key": "GF_SMTP_PASSWORD"
          }
        }
      }
    },
    {
      "op": "add",
      "path": "/spec/template/spec/containers/0/env/-",
      "value": {
        "name": "GF_SMTP_FROM_ADDRESS",
        "valueFrom": {
          "secretKeyRef": {
            "name": "grafana-smtp",
            "key": "GF_SMTP_FROM_ADDRESS"
          }
        }
      }
    },
    {
      "op": "add",
      "path": "/spec/template/spec/containers/0/env/-",
      "value": {
        "name": "GF_SMTP_FROM_NAME",
        "value": "Grafana TriSLA"
      }
    },
    {
      "op": "add",
      "path": "/spec/template/spec/containers/0/env/-",
      "value": {
        "name": "GF_SMTP_SKIP_VERIFY",
        "value": "true"
      }
    }
  ]' || echo "Erro ao aplicar patch (pode já estar configurado)"

echo "✅ Configurações aplicadas"
echo ""

# Aguardar pod reiniciar
echo "⏳ Aguardando pod reiniciar..."
kubectl rollout status deployment/monitoring-grafana -n monitoring --timeout=120s || true

# Obter novo pod
sleep 5
GRAFANA_POD=$(kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana -o jsonpath='{.items[0].metadata.name}')
echo "Novo pod: $GRAFANA_POD"
echo ""

# Resetar senha do admin
echo "🔐 Resetando senha do admin..."
kubectl exec -n monitoring $GRAFANA_POD -c grafana -- grafana cli admin reset-admin-password "TriSLA2025!" || true
echo ""

# Criar novo usuário com email
echo "👤 Criando usuário novo com email..."
kubectl exec -n monitoring $GRAFANA_POD -c grafana -- grafana cli admin create-user \
  --email "${USER_EMAIL}" \
  --name "Admin TriSLA" \
  --password "TriSLA2025!" \
  --org-role Admin || echo "Usuário pode já existir"

echo ""
echo "=========================================="
echo "✅ Configuração Concluída!"
echo "=========================================="
echo ""
echo "📧 Email configurado:"
echo "   SMTP Server: ${SMTP_SERVER}:${SMTP_PORT}"
echo "   From: ${SMTP_USER}"
echo ""
echo "👤 Credenciais de login:"
echo "   Opção 1 - Admin tradicional:"
echo "      Usuário: admin"
echo "      Senha: TriSLA2025!"
echo ""
echo "   Opção 2 - Usuário com email:"
echo "      Email: ${USER_EMAIL}"
echo "      Senha: TriSLA2025!"
echo ""
echo "🌐 Acesse:"
echo "   http://localhost:3000"
echo "   ou"
echo "   http://192.168.10.16:30000"
echo ""
echo "📋 Próximos passos:"
echo "   1. Fazer login com uma das opções acima"
echo "   2. Ir em Settings > Profile e confirmar email"
echo "   3. Testar reset de senha via email"
echo ""




