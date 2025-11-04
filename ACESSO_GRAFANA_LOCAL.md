# Como Acessar Grafana Localmente

## Problema
NodePort 30000 não está acessível diretamente (ERR_CONNECTION_TIMED_OUT).

## Solução: Port-Forward

### Opção 1: SSH Tunnel (Mais Simples)

**No seu computador Windows (PowerShell):**
```powershell
# Criar tunnel SSH
ssh -L 3000:localhost:30000 porvir5g@192.168.10.16
```

**Manter essa janela aberta e acessar:**
- URL: http://localhost:3000
- Usuário: admin
- Senha: C30zAwgGdxm4JKUuNEK3WlUeBw765RplgDApTFFc

### Opção 2: Port-Forward via node1

**Conectar ao node1 e executar:**
```bash
# Port-forward do Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &

# Verificar se está funcionando
sleep 2
curl -sS http://localhost:3000/api/health | jq .
```

**Depois, no seu computador, criar tunnel SSH:**
```powershell
ssh -L 3000:localhost:3000 porvir5g@192.168.10.16
```

### Opção 3: Port-Forward Direto (Se kubectl estiver configurado localmente)

**No seu computador:**
```powershell
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```

**Acessar:**
- URL: http://localhost:3000

## URLs do Dashboard

Após configurar port-forward, acesse:

1. **Grafana Home**: http://localhost:3000
2. **TriSLA Portal Dashboard**: http://localhost:3000/d/b8468b62-2aea-4261-9807-3979303485f0/trisla-portal-overview

## Credenciais

- **Usuário**: admin
- **Senha**: C30zAwgGdxm4JKUuNEK3WlUeBw765RplgDApTFFc

## Troubleshooting

Se o port-forward não funcionar:

1. **Verificar se o pod está rodando:**
   ```bash
   ssh porvir5g@node1
   kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana
   ```

2. **Verificar logs:**
   ```bash
   kubectl logs -n monitoring -l app.kubernetes.io/name=grafana --tail=50
   ```

3. **Testar conectividade no node1:**
   ```bash
   curl -sS http://localhost:30000/api/health | jq .
   ```




