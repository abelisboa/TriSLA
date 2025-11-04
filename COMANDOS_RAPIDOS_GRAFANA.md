# 🚀 Comandos Rápidos - Resolver Acesso ao Grafana

## ✅ Situação Atual

- ✅ **NodePort configurado**: `monitoring-grafana` na porta **30000**
- ✅ **Service Type**: NodePort (80:30000/TCP)
- ⚠️ **Senha não encontrada** no secret "grafana"
- ⚠️ **Timeout no IP** pode ser firewall

---

## 🔍 Encontrar Senha do Grafana

### No node1, execute:

```bash
# Opção 1: Script automático
chmod +x scripts/get_grafana_password.sh
./scripts/get_grafana_password.sh

# Opção 2: Manual - Listar todos os secrets
kubectl get secrets -n monitoring | grep -i grafana

# Opção 3: Verificar prometheus-grafana (ClusterIP)
kubectl get secret -n monitoring prometheus-grafana -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d

# Opção 4: Verificar todos os secrets do monitoring
for secret in $(kubectl get secrets -n monitoring -o name); do
    echo "=== $secret ==="
    kubectl get $secret -n monitoring -o json | jq -r '.data | keys[]' 2>/dev/null | grep -i password && {
        kubectl get $secret -n monitoring -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d && echo ""
    }
done
```

---

## 🔑 Senhas para Tentar

Se não encontrar a senha, tente estas:

```bash
# Testar login programaticamente
GRAFANA_URL="http://localhost:3000"

for pass in "admin" "TriSLA2025!" "trisla123" "prom-operator" "admin123"; do
    echo "Testando senha: $pass"
    curl -s -u "admin:${pass}" "${GRAFANA_URL}/api/user" | grep -q "login" && {
        echo "✅ Senha correta: $pass"
        break
    }
done
```

---

## 🌐 Resolver Timeout no IP (192.168.10.16:30000)

### 1. Verificar se NodePort está funcionando localmente:

```bash
# No node1
curl -s http://localhost:30000/api/health
# ou
curl -s http://192.168.10.16:30000/api/health
```

### 2. Se funcionar no node1 mas não no seu PC:

**Problema: Firewall**

```bash
# No node1, verificar firewall
sudo ufw status
sudo iptables -L -n | grep 30000

# Permitir porta 30000
sudo ufw allow 30000/tcp
sudo ufw reload
```

### 3. Verificar Service está correto:

```bash
# No node1
kubectl get svc -n monitoring monitoring-grafana -o yaml | grep -A 5 ports
```

Deve mostrar:
```yaml
ports:
  - nodePort: 30000
    port: 80
    targetPort: 3000
```

### 4. Verificar se Pod está rodando:

```bash
# No node1
kubectl get pods -n monitoring | grep grafana
kubectl logs -n monitoring -l app.kubernetes.io/name=grafana --tail=20
```

---

## ✅ Solução Completa

### Passo 1: Obter Senha

```bash
# No node1
# Método mais completo
kubectl get secrets -n monitoring | while read line; do
    SECRET=$(echo $line | awk '{print $1}')
    if [ "$SECRET" != "NAME" ]; then
        PASS=$(kubectl get secret -n monitoring $SECRET -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null)
        if [ ! -z "$PASS" ] && [ ${#PASS} -gt 3 ]; then
            echo "✅ Secret: $SECRET"
            echo "   Senha: $PASS"
            break
        fi
    fi
done
```

### Passo 2: Testar Login

```bash
# No node1
GRAFANA_PASS="<senha_encontrada>"
curl -u "admin:${GRAFANA_PASS}" http://localhost:30000/api/user | jq .
```

### Passo 3: Resolver Firewall (se necessário)

```bash
# No node1
sudo ufw allow 30000/tcp
sudo systemctl restart ufw
```

### Passo 4: Testar do seu PC

```bash
# No Windows/PowerShell
curl http://192.168.10.16:30000/api/health
```

---

## 🎯 Comandos Finais

```bash
# No node1 - Tudo de uma vez
echo "=== GRAFANA INFO ==="
echo ""
echo "Services:"
kubectl get svc -n monitoring | grep grafana
echo ""
echo "NodePort: 30000"
echo ""
echo "Senha:"
for s in $(kubectl get secrets -n monitoring -o name); do
    PASS=$(kubectl get $s -n monitoring -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d)
    [ ! -z "$PASS" ] && echo "$PASS" && break
done || echo "Tente: admin, TriSLA2025!, trisla123"
echo ""
echo "Acesso:"
echo "  - NodePort: http://192.168.10.16:30000"
echo "  - Local (node1): http://localhost:30000"
echo ""
```

---

## 💡 Se Nada Funcionar

**Redefinir senha do Grafana:**

```bash
# No node1
# Obter pod do Grafana
GRAFANA_POD=$(kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana -o jsonpath='{.items[0].metadata.name}')

# Redefinir senha
kubectl exec -it -n monitoring $GRAFANA_POD -- grafana-cli admin reset-admin-password TriSLA2025!

# Ou via API (se já estiver logado)
```

---

## ✅ Checklist

- [ ] Encontrar senha correta
- [ ] Testar login em localhost:30000
- [ ] Verificar firewall se timeout no IP
- [ ] Acessar http://192.168.10.16:30000
- [ ] Importar dashboards após login




