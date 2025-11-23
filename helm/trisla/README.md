# TriSLA Helm Chart

Helm chart para deploy completo do TriSLA no Kubernetes.

## Instalação no NASP

O arquivo de valores canônico para deploy no NASP é `values-nasp.yaml`:

```bash
cd ~/gtp5g/trisla

# Deploy no NASP
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

## Arquivo de Valores Canônico

**Para NASP:** `helm/trisla/values-nasp.yaml`

Este é o arquivo padrão para deploy em produção no ambiente NASP. Contém:
- Configurações de rede do NASP
- Endpoints dos controladores (RAN, Transport, Core)
- Configurações de produção real
- Recursos otimizados para produção

## Valores Importantes

### Network Configuration
- `network.interface`: Interface de rede principal (ex: "my5g")
- `network.nodeIP`: IP do node1 (ex: "192.168.10.16")
- `network.gateway`: Gateway padrão

### Production Settings
- `production.enabled`: true
- `production.simulationMode`: false (⚠️ NÃO usar simulação)
- `production.useRealServices`: true (⚠️ Usar serviços REAIS)
- `production.executeRealActions`: true (⚠️ Executar ações REAIS)

### NASP Endpoints
- `naspAdapter.naspEndpoints.ran`: Endpoint do controlador RAN
- `naspAdapter.naspEndpoints.core_upf`: Endpoint UPF (Core)
- `naspAdapter.naspEndpoints.transport`: Endpoint do controlador Transport

## Validação

```bash
# Lint do chart
helm lint ./helm/trisla

# Template com values-nasp.yaml
helm template trisla ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --debug
```

## Verificação Pós-Deploy

```bash
# Verificar pods
kubectl get pods -n trisla

# Verificar serviços
kubectl get svc -n trisla

# Verificar status do Helm release
helm status trisla -n trisla
```

