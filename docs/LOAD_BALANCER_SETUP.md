# Configuração do Load Balancer - TriSLA Portal

## Opção 1: Service LoadBalancer (Cloud Provider)

Para ambientes com suporte a LoadBalancer (ex: AWS, GCP, Azure):

```bash
# Aplicar Service LoadBalancer
kubectl apply -f trisla-loadbalancer.yaml

# Verificar status
kubectl get svc trisla-portal-lb -n trisla

# Aguardar IP externo ser atribuído
kubectl get svc trisla-portal-lb -n trisla -w
```

Após o IP ser atribuído:
```bash
# Testar LoadBalancer
LB_IP=$(kubectl get svc trisla-portal-lb -n trisla -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -sS http://$LB_IP/api/v1/health | jq .
```

## Opção 2: Service NodePort (Bare Metal/NASP)

Para ambientes sem LoadBalancer nativo, use NodePort:

```bash
# Aplicar Service NodePort
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: trisla-portal-nodeport
  namespace: trisla
spec:
  type: NodePort
  ports:
    - port: 8000
      targetPort: 8000
      nodePort: 30080
  selector:
    app: trisla-portal
EOF

# Verificar Service
kubectl get svc trisla-portal-nodeport -n trisla

# Testar em ambos os nodes
curl -sS http://192.168.10.16:30080/api/v1/health | jq .
curl -sS http://192.168.10.15:30080/api/v1/health | jq .
```

## Opção 3: Ingress Controller (Recomendado para Produção)

Se houver Ingress Controller instalado (ex: NGINX, Traefik):

```bash
# Criar Ingress
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: trisla-portal-ingress
  namespace: trisla
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
    - host: trisla.nasp.local
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

# Verificar Ingress
kubectl get ingress -n trisla

# Testar (ajustar hostname conforme necessário)
curl -sS -H "Host: trisla.nasp.local" http://<INGRESS_IP>/api/v1/health | jq .
```

## Opção 4: HAProxy/Nginx Externo (Melhor para Bare Metal)

Para controle total, use HAProxy ou Nginx externo:

```bash
# Instalar HAProxy no node de controle (ou node dedicado)
sudo apt update && sudo apt install -y haproxy

# Configurar HAProxy
sudo tee /etc/haproxy/haproxy.cfg <<'EOF'
global
    log /dev/log local0
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend trisla_frontend
    bind *:80
    default_backend trisla_backend

backend trisla_backend
    balance roundrobin
    option httpchk GET /api/v1/health
    server node1 192.168.10.16:30080 check
    server node2 192.168.10.15:30080 check

listen stats
    bind *:8404
    stats enable
    stats uri /
    stats refresh 30s
EOF

# Reiniciar HAProxy
sudo systemctl restart haproxy
sudo systemctl enable haproxy

# Testar
curl -sS http://localhost/api/v1/health | jq .
```

## Verificação e Monitoramento

```bash
# Verificar distribuição de tráfego
kubectl get endpoints trisla-portal -n trisla

# Verificar métricas de serviço
kubectl top pods -n trisla -l app=trisla-portal

# Testar múltiplas requisições para ver distribuição
for i in {1..10}; do
  echo "Request $i:"
  curl -sS http://<LB_IP>/api/v1/health | jq -r '.status'
done
```

## Troubleshooting

- **LoadBalancer não recebe IP externo**: Use NodePort como alternativa
- **502 Bad Gateway**: Verificar se pods estão Running
- **503 Service Unavailable**: Verificar se seletores do Service batem com labels dos pods
- **Distribuição desigual**: Verificar sessionAffinity e balanceamento

## Status Atual

- Node1: http://192.168.10.16:8092 (port-forward)
- Node2: http://192.168.10.15:8093 (port-forward)
- LoadBalancer: A configurar conforme opção escolhida




