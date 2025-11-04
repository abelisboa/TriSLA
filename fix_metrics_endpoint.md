# Correção do Endpoint /metrics para Prometheus

## Problema
Prometheus está tentando coletar métricas de `http://10.233.102.179:8001/metrics` mas recebe "connection refused".

## Verificar Endpoint Atual

```bash
# Verificar se o endpoint /metrics existe na API
curl -sS http://localhost:8092/api/v1/metrics || echo "Endpoint não encontrado"
curl -sS http://localhost:8092/metrics || echo "Endpoint não encontrado"

# Verificar ServiceMonitor
kubectl get servicemonitor -n trisla

# Verificar Service e portas
kubectl get svc -n trisla trisla-portal -o yaml | grep -A 10 ports
```

## Solução

O endpoint `/metrics` precisa estar disponível na porta que o ServiceMonitor está configurado. Opções:

1. **Configurar endpoint correto na API** (se já existe em outra porta)
2. **Ajustar ServiceMonitor** para usar a porta correta
3. **Expor endpoint /metrics na API** (se não existe)

## Comandos para Executar

```bash
# 1) Verificar configuração do ServiceMonitor
kubectl get servicemonitor -n trisla trisla-portal-servicemonitor -o yaml

# 2) Verificar qual porta a API está usando para métricas
kubectl exec -n trisla deploy/trisla-portal -c trisla-api -- curl -sS http://localhost:8000/metrics | head -5

# 3) Verificar se há endpoint /metrics na porta 8001
kubectl exec -n trisla deploy/trisla-portal -c trisla-api -- curl -sS http://localhost:8001/metrics || echo "Porta 8001 não existe"
```

## Próximos Passos

1. Acessar dashboard no Grafana (já funciona mesmo sem métricas)
2. Verificar logs da API para ver se /metrics está configurado
3. Corrigir ServiceMonitor ou expor endpoint correto




