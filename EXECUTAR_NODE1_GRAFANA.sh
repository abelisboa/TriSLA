#!/bin/bash
# Comandos para executar no node1 - Resolver Grafana

echo "=========================================="
echo "🔍 Diagnosticando Grafana"
echo "=========================================="
echo ""

# 1. Verificar Service
echo "1️⃣ Service do Grafana:"
kubectl get svc -n monitoring | grep grafana
echo ""

# 2. Procurar senha
echo "2️⃣ Procurando senha..."
echo ""

# Tentar prometheus-grafana
echo "   Verificando prometheus-grafana:"
PASS1=$(kubectl get secret -n monitoring prometheus-grafana -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null)
[ ! -z "$PASS1" ] && echo "   ✅ Senha encontrada: $PASS1" || echo "   ❌ Não encontrada"

# Listar todos os secrets e procurar
echo ""
echo "   Verificando todos os secrets:"
for secret in $(kubectl get secrets -n monitoring -o name 2>/dev/null); do
    SECRET_NAME=$(echo $secret | cut -d'/' -f2)
    if kubectl get $secret -n monitoring -o json 2>/dev/null | jq -r '.data | keys[]' 2>/dev/null | grep -qi "password\|admin"; then
        PASS=$(kubectl get $secret -n monitoring -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null)
        if [ ! -z "$PASS" ] && [ ${#PASS} -gt 3 ]; then
            echo "   ✅ Secret: $SECRET_NAME"
            echo "      Senha: $PASS"
            GRAFANA_PASS="$PASS"
            break
        fi
    fi
done

echo ""
echo "3️⃣ Informações:"
echo "   NodePort: 30000"
echo "   URL NodePort: http://192.168.10.16:30000"
echo "   URL Local: http://localhost:30000"
echo "   Usuário: admin"
if [ ! -z "$GRAFANA_PASS" ]; then
    echo "   Senha: $GRAFANA_PASS"
else
    echo "   Senha: Não encontrada automaticamente"
    echo "   💡 Tentar: admin, TriSLA2025!, trisla123, prom-operator"
fi
echo ""

# 4. Testar conectividade
echo "4️⃣ Testando conectividade:"
echo "   Testando localhost:30000..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:30000/api/health 2>/dev/null | grep -q "200\|401\|302"; then
    echo "   ✅ localhost:30000 responde"
else
    echo "   ❌ localhost:30000 não responde"
fi

echo "   Testando 192.168.10.16:30000..."
if curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://192.168.10.16:30000/api/health 2>/dev/null | grep -q "200\|401\|302"; then
    echo "   ✅ 192.168.10.16:30000 responde"
else
    echo "   ❌ 192.168.10.16:30000 não responde (timeout)"
    echo "   💡 Problema: Firewall provavelmente bloqueando porta 30000"
    echo ""
    echo "   Resolver firewall:"
    echo "   sudo ufw allow 30000/tcp"
    echo "   sudo ufw reload"
fi

echo ""
echo "=========================================="
echo "✅ Diagnóstico completo!"
echo "=========================================="
echo ""




