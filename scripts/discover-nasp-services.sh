#!/bin/bash
# ============================================
# Script para Descobrir Serviços NASP Específicos
# ============================================
# Executar no NASP (node1) para descobrir endpoints reais
# ============================================

set -e

echo "🔍 Descobrindo serviços NASP específicos..."
echo ""

# Namespaces relevantes encontrados
NAMESPACES=("nasp" "ran-test" "open5gs" "srsran" "nonrtric")

echo "1️⃣ Procurando serviços nos namespaces relevantes..."
echo ""

# Procurar serviços RAN
echo "📡 Procurando controladores RAN..."
for ns in "${NAMESPACES[@]}"; do
    echo "   Namespace: $ns"
    SERVICES=$(kubectl get svc -n "$ns" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    
    if [ -n "$SERVICES" ]; then
        for svc in $SERVICES; do
            # Filtrar serviços que podem ser RAN
            if echo "$svc" | grep -qiE "ran|gnb|ue|base"; then
                CLUSTER_IP=$(kubectl get svc -n "$ns" "$svc" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
                PORT=$(kubectl get svc -n "$ns" "$svc" -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "")
                TYPE=$(kubectl get svc -n "$ns" "$svc" -o jsonpath='{.spec.type}' 2>/dev/null || echo "")
                
                echo "     ✅ $svc ($ns):"
                echo "        Type: $TYPE"
                echo "        ClusterIP: $CLUSTER_IP"
                echo "        Port: $PORT"
                echo "        Endpoint: http://$CLUSTER_IP:$PORT"
                echo "        FQDN: http://$svc.$ns.svc.cluster.local:$PORT"
                echo ""
            fi
        done
    fi
done

# Procurar serviços Transport
echo "🚛 Procurando controladores Transport..."
for ns in "${NAMESPACES[@]}"; do
    SERVICES=$(kubectl get svc -n "$ns" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    
    if [ -n "$SERVICES" ]; then
        for svc in $SERVICES; do
            if echo "$svc" | grep -qiE "transport|router|switch"; then
                CLUSTER_IP=$(kubectl get svc -n "$ns" "$svc" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
                PORT=$(kubectl get svc -n "$ns" "$svc" -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "")
                
                echo "     ✅ $svc ($ns):"
                echo "        Endpoint: http://$CLUSTER_IP:$PORT"
                echo "        FQDN: http://$svc.$ns.svc.cluster.local:$PORT"
                echo ""
            fi
        done
    fi
done

# Procurar serviços Core
echo "🖥️  Procurando controladores Core..."
for ns in "${NAMESPACES[@]}"; do
    SERVICES=$(kubectl get svc -n "$ns" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    
    if [ -n "$SERVICES" ]; then
        for svc in $SERVICES; do
            if echo "$svc" | grep -qiE "core|amf|smf|upf|mme"; then
                CLUSTER_IP=$(kubectl get svc -n "$ns" "$svc" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
                PORT=$(kubectl get svc -n "$ns" "$svc" -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "")
                
                echo "     ✅ $svc ($ns):"
                echo "        Endpoint: http://$CLUSTER_IP:$PORT"
                echo "        FQDN: http://$svc.$ns.svc.cluster.local:$PORT"
                echo ""
            fi
        done
    fi
done

# Listar todos os serviços nos namespaces relevantes
echo "2️⃣ Listando todos os serviços nos namespaces relevantes..."
echo ""

for ns in "${NAMESPACES[@]}"; do
    echo "📦 Namespace: $ns"
    kubectl get svc -n "$ns" 2>/dev/null || echo "   (sem serviços ou namespace não acessível)"
    echo ""
done

# Procurar no namespace "nasp" especificamente
echo "3️⃣ Detalhando namespace 'nasp'..."
if kubectl get namespace nasp &>/dev/null; then
    echo "   Serviços no namespace 'nasp':"
    kubectl get svc -n nasp -o wide
    echo ""
    
    # Listar pods também
    echo "   Pods no namespace 'nasp':"
    kubectl get pods -n nasp
    echo ""
fi

# Procurar no namespace "open5gs" (possível Core)
echo "4️⃣ Detalhando namespace 'open5gs'..."
if kubectl get namespace open5gs &>/dev/null; then
    echo "   Serviços no namespace 'open5gs':"
    kubectl get svc -n open5gs -o wide
    echo ""
fi

# Procurar no namespace "srsran" (possível RAN)
echo "5️⃣ Detalhando namespace 'srsran'..."
if kubectl get namespace srsran &>/dev/null; then
    echo "   Serviços no namespace 'srsran':"
    kubectl get svc -n srsran -o wide
    echo ""
fi

echo "✅ Descoberta concluída!"
echo ""
echo "📋 Próximos passos:"
echo "   1. Identificar os serviços corretos (RAN, Transport, Core)"
echo "   2. Usar ClusterIP ou FQDN para configurar endpoints"
echo "   3. Atualizar helm/trisla/values-production.yaml"
echo "   4. Atualizar apps/nasp-adapter/src/nasp_client.py"

