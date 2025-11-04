#!/bin/bash
# Obter senha correta do Grafana

echo "🔐 Obtendo credenciais do Grafana..."
echo ""

# Tentar diferentes secrets possíveis
echo "1. Tentando secret: monitoring-grafana"
PASSWORD1=$(kubectl get secret -n monitoring monitoring-grafana -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null)
if [ ! -z "$PASSWORD1" ]; then
    echo "✅ Senha encontrada no secret monitoring-grafana:"
    echo "$PASSWORD1"
    echo ""
fi

echo "2. Tentando secret: grafana"
PASSWORD2=$(kubectl get secret -n monitoring grafana -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null)
if [ ! -z "$PASSWORD2" ]; then
    echo "✅ Senha encontrada no secret grafana:"
    echo "$PASSWORD2"
    echo ""
fi

echo "3. Tentando secret: prometheus-grafana"
PASSWORD3=$(kubectl get secret -n monitoring prometheus-grafana -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null)
if [ ! -z "$PASSWORD3" ]; then
    echo "✅ Senha encontrada no secret prometheus-grafana:"
    echo "$PASSWORD3"
    echo ""
fi

echo "4. Listando todos os secrets relacionados ao Grafana:"
kubectl get secrets -n monitoring | grep -i grafana

echo ""
echo "5. Tentando usar senha padrão 'admin' (se não tiver sido alterada)"
echo "   Senha padrão: admin"

echo ""
echo "📋 Próximos passos:"
echo "   1. Se nenhuma senha funcionou, tentar resetar a senha do Grafana"
echo "   2. Ou verificar se há configmap com credenciais"




