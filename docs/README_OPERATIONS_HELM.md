## TriSLA Portal — Operação via Helm (Overrides de API/Worker)

### Visão geral
Este chart suporta sobrescrever o `main.py` da API e o `worker.py` (RQ) via ConfigMap, garantindo `REDIS_HOST=localhost` (sidecar Redis) e `PYTHONPATH` corretos.

### Pré-requisitos
- ConfigMap com os arquivos corrigidos:

```bash
kubectl -n trisla create configmap trisla-api-overrides \
  --from-file=main.py=/tmp/trisla_api_main.py \
  --from-file=worker.py=/tmp/trisla_worker.py \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Valores importantes (`helm/trisla-portal/values.yaml`)
```yaml
overrides:
  enabled: true
  configMapName: trisla-api-overrides
  api:
    mountPath: /app/main.py
    subPath: main.py
  worker:
    mountPath: /app/jobs/worker.py
    subPath: worker.py
```

### Deploy/Upgrade
```bash
helm upgrade --install trisla-portal ./helm/trisla-portal -n trisla --atomic --timeout 5m
```

### Verificações
```bash
kubectl get pods -n trisla
kubectl logs -n trisla deploy/trisla-portal -c trisla-api --tail=100
kubectl logs -n trisla deploy/trisla-portal -c trisla-rq-worker --tail=100
```

### Teste rápido
```bash
nohup kubectl -n trisla port-forward svc/trisla-portal 8092:8000 >/tmp/pf.log 2>&1 &
sleep 2
curl -sS -X POST http://localhost:8092/api/v1/slices \
  -H "Content-Type: application/json" \
  -d '{"slice_type":"URLLC","bandwidth":100,"latency":1,"description":"Slice"}' | jq .
```






