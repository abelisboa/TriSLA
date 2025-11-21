# TriSLA Helm Chart

Helm chart para deploy completo do TriSLA no Kubernetes.

## Instalação

```bash
helm install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values.yaml
```

## Valores Importantes

### Network Configuration
- `network.interface`: Interface de rede principal
- `network.nodeIP`: IP do nó Kubernetes
- `network.gateway`: Gateway padrão

### Production Settings
- `production.enabled`: true
- `production.simulationMode`: false
- `production.useRealServices`: true
- `production.executeRealActions`: true

## Validação

```bash
helm lint ./helm/trisla
helm template trisla ./helm/trisla --debug
```

