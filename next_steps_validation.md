# Próximos Passos - Validação E2E

## Status Atual
- ✅ Sistema TriSLA funcionando no node1
- ✅ Pod trisla-portal-6bdbdb5469-5fm2h com 4/4 containers Running
- ✅ Jobs sendo processados com sucesso (logs mostram "Job OK")

## Comandos para Executar no node1

### 1. Verificar Status do Sistema
```bash
# Verificar pods
kubectl get pods -n trisla

# Verificar se port-forward está ativo
ps aux | grep port-forward

# Se não estiver ativo, reiniciar:
pkill -f "kubectl port-forward .* 8092:8000" || true
nohup kubectl -n trisla port-forward svc/trisla-portal 8092:8000 >/tmp/pf-uiapi.log 2>&1 &
sleep 2
```

### 2. Testar API e Criar Slice
```bash
# Testar health check
curl -sS http://localhost:8092/api/v1/health | jq .

# Criar slice de teste
curl -sS -X POST http://localhost:8092/api/v1/slices \
  -H "Content-Type: application/json" \
  -d '{"slice_type":"URLLC","bandwidth":100,"latency":1,"description":"Teste E2E"}' | jq .

# Verificar logs do worker
kubectl logs -n trisla deploy/trisla-portal -c trisla-rq-worker --tail=20
```

### 3. Testar Grafana (se disponível)
```bash
# Verificar se Prometheus está rodando
kubectl get pods -n monitoring

# Acessar Grafana (se configurado)
# http://<IP-node1>:30000
# Usuário: admin, Senha: (verificar no secret)
kubectl get secret -n monitoring grafana -o jsonpath='{.data.admin-password}' | base64 -d
```

### 4. Preparar Node2
```bash
# Verificar inventário Ansible
cat inventory/hosts

# Executar playbook no node2
ansible-playbook -i inventory/hosts playbooks/deploy-trisla.yml --limit node2
```

## Próximas Ações Recomendadas

1. **Validação E2E**: Execute os comandos acima para confirmar funcionamento completo
2. **Grafana**: Configure dashboards para monitoramento
3. **Node2**: Execute deployment no segundo nó
4. **Documentação**: Atualize README com passos consolidados

## Status dos TODOs
- ✅ Sistema funcionando
- 🔄 Validação E2E em andamento
- ⏳ Grafana pendente
- ⏳ Node2 pendente
- ⏳ Documentação pendente




