# Comandos para Deploy no Node2

## Pré-requisitos
- Node1 já funcionando com TriSLA
- Node2 acessível via SSH (192.168.10.17)
- Ansible configurado

## 1. Verificar Conectividade
```bash
# Testar conectividade com node2
ssh porvir5g@192.168.10.17 "echo 'Node2 acessível'"

# Verificar se Kubernetes está rodando no node2
ssh porvir5g@192.168.10.17 "kubectl get nodes"
```

## 2. Executar Deploy Ansible no Node2
```bash
# Navegar para diretório ansible
cd ansible

# Executar playbook apenas no node2
ansible-playbook -i inventory.yaml deploy_trisla_nasp.yml --limit node2 --ask-become-pass

# Ou usando hosts.ini
ansible-playbook -i hosts.ini deploy_trisla_nasp.yml --limit 192.168.10.17 --ask-become-pass
```

## 3. Verificar Deploy no Node2
```bash
# Verificar pods no node2
ssh porvir5g@192.168.10.17 "kubectl get pods -n trisla"

# Verificar serviços
ssh porvir5g@192.168.10.17 "kubectl get svc -n trisla"

# Verificar logs
ssh porvir5g@192.168.10.17 "kubectl logs -n trisla deploy/trisla-portal -c trisla-api --tail=20"
```

## 4. Configurar Port-Forward no Node2
```bash
# Configurar port-forward para acesso local
ssh porvir5g@192.168.10.17 "kubectl -n trisla port-forward svc/trisla-portal 8093:8000 &"

# Testar API do node2
curl -sS http://192.168.10.17:8093/api/v1/health | jq .
```

## 5. Configurar Load Balancer (Opcional)
```bash
# Criar serviço LoadBalancer para distribuir entre node1 e node2
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: trisla-portal-lb
  namespace: trisla
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: trisla-portal
EOF
```

## 6. Validação Final
```bash
# Testar criação de slice no node2
curl -sS -X POST http://192.168.10.17:8093/api/v1/slices \
  -H "Content-Type: application/json" \
  -d '{"slice_type":"eMBB","bandwidth":200,"latency":5,"description":"Teste Node2"}' | jq .

# Verificar processamento
ssh porvir5g@192.168.10.17 "kubectl logs -n trisla deploy/trisla-portal -c trisla-rq-worker --tail=10"
```

## Troubleshooting
- Se houver erro de conectividade, verificar firewall
- Se pods não subirem, verificar recursos disponíveis
- Se API não responder, verificar configuração de rede




