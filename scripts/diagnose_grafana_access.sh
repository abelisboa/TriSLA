#!/bin/bash
# Script para diagnosticar acesso ao Grafana

echo "=========================================="
echo "🔍 Diagnóstico de Acesso ao Grafana"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "1️⃣ Verificando Service do Grafana..."
echo ""

# Verificar se Grafana está rodando
echo "   📊 Services do Grafana:"
kubectl get svc -n monitoring | grep grafana || echo "   ⚠️  Grafana service não encontrado no namespace monitoring"
echo ""

# Verificar tipo de service
GRAFANA_SVC=$(kubectl get svc -n monitoring -o jsonpath='{.items[?(@.metadata.name==*"grafana"*)].spec.type}' 2>/dev/null || echo "ClusterIP")

echo "   🔧 Tipo de Service: $GRAFANA_SVC"
echo ""

if [ "$GRAFANA_SVC" = "NodePort" ] || kubectl get svc -n monitoring | grep -q "NodePort.*grafana"; then
    echo "   ✅ Grafana tem NodePort configurado"
    NODEPORT=$(kubectl get svc -n monitoring -o jsonpath='{.items[?(@.metadata.name==*"grafana"*)].spec.ports[?(@.port==80||@.port==3000)].nodePort}' 2>/dev/null || echo "N/A")
    echo "   📌 NodePort: $NODEPORT"
    echo ""
    echo "   🌐 Tente acessar: http://192.168.10.16:${NODEPORT}"
else
    echo "   ⚠️  Grafana não tem NodePort - apenas ClusterIP"
    echo "   💡 Solução: Usar port-forward"
    echo ""
fi

echo ""
echo "2️⃣ Verificando Pods do Grafana..."
echo ""
kubectl get pods -n monitoring | grep grafana || echo "   ⚠️  Pods do Grafana não encontrados"
echo ""

echo ""
echo "3️⃣ Obtendo Credenciais de Login..."
echo ""

# Tentar diferentes formas de obter a senha
echo "   Tentando obter senha do Secret..."
echo ""

# Método 1: Secret padrão do Grafana
GRAFANA_PASS=$(kubectl get secret -n monitoring grafana -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null)

if [ ! -z "$GRAFANA_PASS" ]; then
    echo "   ✅ Senha encontrada no Secret 'grafana':"
    echo "   ${GREEN}   Usuário: admin${NC}"
    echo "   ${GREEN}   Senha: $GRAFANA_PASS${NC}"
else
    # Método 2: Outro secret
    GRAFANA_PASS=$(kubectl get secret -n monitoring -l app.kubernetes.io/name=grafana -o jsonpath='{.items[0].data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null)
    
    if [ ! -z "$GRAFANA_PASS" ]; then
        echo "   ✅ Senha encontrada:"
        echo "   ${GREEN}   Usuário: admin${NC}"
        echo "   ${GREEN}   Senha: $GRAFANA_PASS${NC}"
    else
        # Método 3: Verificar todos os secrets
        echo "   🔍 Procurando em todos os secrets..."
        kubectl get secrets -n monitoring | grep -i grafana | while read line; do
            SECRET_NAME=$(echo $line | awk '{print $1}')
            echo "   Verificando secret: $SECRET_NAME"
            kubectl get secret -n monitoring $SECRET_NAME -o json | jq -r '.data | keys[]' 2>/dev/null | grep -i password && {
                PASS=$(kubectl get secret -n monitoring $SECRET_NAME -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d)
                [ ! -z "$PASS" ] && echo "   ${GREEN}✅ Senha encontrada: $PASS${NC}" || echo "   ⚠️  Campo admin-password não encontrado"
            }
        done
        
        if [ -z "$GRAFANA_PASS" ]; then
            echo "   ${YELLOW}⚠️  Senha não encontrada automaticamente${NC}"
            echo "   💡 Tente senhas comuns:"
            echo "      - admin"
            echo "      - TriSLA2025!"
            echo "      - trisla123"
            echo "      - prom-operator"
        fi
    fi
fi

echo ""
echo "4️⃣ Verificando Port-Forward..."
echo ""

# Verificar se port-forward está ativo
PF_PID=$(ps aux | grep "kubectl.*port-forward.*grafana" | grep -v grep | awk '{print $2}' | head -1)

if [ ! -z "$PF_PID" ]; then
    echo "   ✅ Port-forward ativo (PID: $PF_PID)"
    echo "   🌐 Acesse: http://localhost:3000"
else
    echo "   ⚠️  Port-forward não está ativo"
    echo "   💡 Para ativar:"
    echo "      kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &"
fi

echo ""
echo "5️⃣ Testando Conectividade..."
echo ""

# Testar localhost
echo "   Testando localhost:3000..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health 2>/dev/null | grep -q "200\|401\|302"; then
    echo "   ${GREEN}✅ localhost:3000 está respondendo${NC}"
else
    echo "   ${RED}❌ localhost:3000 não está respondendo${NC}"
fi

# Testar via IP (se NodePort configurado)
if [ ! -z "$NODEPORT" ] && [ "$NODEPORT" != "N/A" ]; then
    echo "   Testando 192.168.10.16:${NODEPORT}..."
    if curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://192.168.10.16:${NODEPORT}/api/health 2>/dev/null | grep -q "200\|401\|302"; then
        echo "   ${GREEN}✅ 192.168.10.16:${NODEPORT} está respondendo${NC}"
    else
        echo "   ${RED}❌ 192.168.10.16:${NODEPORT} não está respondendo (timeout)${NC}"
        echo "   💡 Possíveis causas:"
        echo "      - Firewall bloqueando porta ${NODEPORT}"
        echo "      - Grafana não está exposto via NodePort"
        echo "      - Service não está configurado corretamente"
    fi
fi

echo ""
echo "=========================================="
echo "📋 RESUMO"
echo "=========================================="
echo ""
echo "🔧 Configuração:"
echo "   - Service Type: $GRAFANA_SVC"
[ ! -z "$NODEPORT" ] && [ "$NODEPORT" != "N/A" ] && echo "   - NodePort: $NODEPORT"
echo ""
echo "🔐 Credenciais:"
echo "   - Usuário: admin"
[ ! -z "$GRAFANA_PASS" ] && echo "   - Senha: $GRAFANA_PASS" || echo "   - Senha: (não encontrada automaticamente)"
echo ""
echo "🌐 Acesso:"
[ ! -z "$PF_PID" ] && echo "   ✅ Port-forward: http://localhost:3000"
[ ! -z "$NODEPORT" ] && [ "$NODEPORT" != "N/A" ] && echo "   🌐 NodePort: http://192.168.10.16:${NODEPORT}"
echo ""

if [ -z "$NODEPORT" ] || [ "$NODEPORT" = "N/A" ]; then
    echo "💡 RECOMENDAÇÃO:"
    echo "   Use port-forward para acessar do seu computador:"
    echo "   ssh -L 3000:localhost:3000 porvir5g@192.168.10.16"
    echo "   Ou configure NodePort no Service do Grafana"
    echo ""
fi

echo "✅ Diagnóstico completo!"
echo ""




