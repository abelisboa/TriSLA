#!/bin/bash
# Script para obter senha do Grafana

echo "🔍 Procurando senha do Grafana..."
echo ""

# Listar todos os secrets do monitoring
echo "📋 Secrets no namespace monitoring:"
kubectl get secrets -n monitoring | grep -i grafana
echo ""

# Tentar diferentes secrets
SECRETS=$(kubectl get secrets -n monitoring -o name | grep -i grafana)

if [ -z "$SECRETS" ]; then
    echo "⚠️  Nenhum secret com 'grafana' encontrado"
    echo ""
    echo "📋 Todos os secrets em monitoring:"
    kubectl get secrets -n monitoring
    echo ""
    echo "💡 Tentando secrets padrão do prometheus-operator..."
    echo ""
    
    # Tentar prometheus-operator
    kubectl get secrets -n monitoring | grep -E "prometheus.*grafana|grafana.*admin" | while read line; do
        SECRET_NAME=$(echo $line | awk '{print $1}')
        echo "Tentando secret: $SECRET_NAME"
        
        # Tentar diferentes campos
        for field in admin-password adminPassword password admin-user; do
            PASS=$(kubectl get secret -n monitoring $SECRET_NAME -o jsonpath="{.data.${field}}" 2>/dev/null | base64 -d 2>/dev/null)
            if [ ! -z "$PASS" ]; then
                echo "✅ Senha encontrada no campo '$field':"
                echo "   Usuário: admin"
                echo "   Senha: $PASS"
                exit 0
            fi
        done
    done
else
    echo "🔍 Verificando secrets encontrados..."
    echo ""
    
    for SECRET_NAME in $SECRETS; do
        SECRET_NAME=$(echo $SECRET_NAME | cut -d'/' -f2)
        echo "Verificando: $SECRET_NAME"
        
        # Listar campos do secret
        FIELDS=$(kubectl get secret -n monitoring $SECRET_NAME -o json 2>/dev/null | jq -r '.data | keys[]' 2>/dev/null)
        
        for field in $FIELDS; do
            if echo "$field" | grep -qi "password\|pass"; then
                PASS=$(kubectl get secret -n monitoring $SECRET_NAME -o jsonpath="{.data.${field}}" 2>/dev/null | base64 -d 2>/dev/null)
                if [ ! -z "$PASS" ] && [ ${#PASS} -gt 3 ]; then
                    echo "✅ Senha encontrada!"
                    echo "   Secret: $SECRET_NAME"
                    echo "   Campo: $field"
                    echo "   Usuário: admin"
                    echo "   Senha: $PASS"
                    exit 0
                fi
            fi
        done
    done
fi

echo ""
echo "❌ Senha não encontrada automaticamente"
echo ""
echo "💡 Tentar senhas comuns:"
echo "   - admin"
echo "   - TriSLA2025!"
echo "   - trisla123"
echo "   - prom-operator"
echo "   - admin123"
echo ""
echo "💡 Ou verificar deployment/configmap:"
kubectl get deployment -n monitoring -o yaml | grep -i password
kubectl get configmap -n monitoring | grep -i grafana
echo ""




