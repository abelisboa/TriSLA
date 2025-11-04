#!/bin/bash
# Script para configurar Load Balancer TriSLA Portal

set -e

echo "=== Configurando Load Balancer TriSLA Portal ==="

# Verificar se kubectl está configurado
if ! kubectl cluster-info &>/dev/null; then
    echo "❌ Erro: kubectl não está configurado ou cluster não acessível"
    exit 1
fi

# Verificar se namespace trisla existe
if ! kubectl get ns trisla &>/dev/null; then
    echo "❌ Erro: Namespace 'trisla' não existe"
    exit 1
fi

# Verificar se pods do trisla-portal estão rodando
PODS=$(kubectl get pods -n trisla -l app=trisla-portal --no-headers 2>/dev/null | wc -l)
if [ "$PODS" -eq 0 ]; then
    echo "⚠️  Aviso: Nenhum pod do trisla-portal encontrado"
    read -p "Continuar mesmo assim? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Escolha a opção de Load Balancer:"
echo "1) NodePort (recomendado para bare metal/NASP)"
echo "2) LoadBalancer (requer cloud provider ou MetalLB)"
echo "3) Ingress (requer Ingress Controller instalado)"
echo ""
read -p "Opção (1-3): " OPTION

case $OPTION in
    1)
        echo "✅ Configurando NodePort..."
        kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: trisla-portal-nodeport
  namespace: trisla
  labels:
    app: trisla-portal
    service-type: nodeport
spec:
  type: NodePort
  ports:
    - name: http
      port: 8000
      targetPort: 8000
      nodePort: 30080
      protocol: TCP
  selector:
    app: trisla-portal
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600
EOF
        echo ""
        echo "✅ NodePort configurado!"
        echo ""
        echo "Serviço disponível em:"
        echo "  - http://192.168.10.16:30080"
        echo "  - http://192.168.10.15:30080"
        echo ""
        echo "Teste com:"
        echo "  curl -sS http://192.168.10.16:30080/api/v1/health | jq ."
        ;;
    2)
        echo "✅ Configurando LoadBalancer..."
        kubectl apply -f trisla-loadbalancer.yaml
        echo ""
        echo "⏳ Aguardando IP externo ser atribuído..."
        echo "   (pode levar alguns minutos)"
        echo ""
        echo "Monitore com:"
        echo "  kubectl get svc trisla-portal-lb -n trisla -w"
        ;;
    3)
        echo "✅ Verificando Ingress Controller..."
        if kubectl get ingressclass &>/dev/null; then
            echo "✅ Ingress Controller encontrado"
            read -p "Nome do host (ex: trisla.nasp.local): " HOSTNAME
            
            kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: trisla-portal-ingress
  namespace: trisla
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
    - host: ${HOSTNAME}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: trisla-portal
                port:
                  number: 8000
EOF
            echo ""
            echo "✅ Ingress configurado!"
            echo ""
            echo "Acesse via: http://${HOSTNAME}"
        else
            echo "❌ Ingress Controller não encontrado"
            echo "   Instale um Ingress Controller primeiro (ex: NGINX, Traefik)"
            exit 1
        fi
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "=== Verificando status ==="
kubectl get svc -n trisla -l app=trisla-portal

echo ""
echo "=== Testando conectividade ==="
if kubectl get svc trisla-portal-nodeport -n trisla &>/dev/null; then
    echo "Testando NodePort no node1..."
    curl -sS http://192.168.10.16:30080/api/v1/health | jq . || echo "⚠️  Não foi possível conectar"
    
    echo ""
    echo "Testando NodePort no node2..."
    curl -sS http://192.168.10.15:30080/api/v1/health | jq . || echo "⚠️  Não foi possível conectar"
fi

echo ""
echo "✅ Configuração concluída!"




