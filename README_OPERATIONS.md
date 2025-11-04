# TriSLA Dashboard v3.2.4 – Monitor Integrado

## Passos de execução

```bash
# 1. Conectar ao NASP (túneis Prometheus + SEM-NSMF)
bash scripts/connect-trisla-nasp-v3.2.4.sh

# 2. Iniciar backend e frontend
bash scripts/start-dashboard.sh

# 3. Encerrar tudo
bash scripts/stop-dashboard.sh
```

Monitor visual:
- Prometheus e SEM-NSMF são verificados via `/api/status`
- Atualização automática a cada 10 segundos
