# 🔧 Resolver Problemas de Acesso ao Grafana

## ❌ Problemas Identificados

1. **localhost:3000** → Abre página mas erro no login
2. **192.168.10.16:30000** → Erro de conexão timeout

---

## 🔍 Diagnóstico

### Execute no node1:

```bash
# Diagnosticar problemas
chmod +x scripts/diagnose_grafana_access.sh
./scripts/diagnose_grafana_access.sh
```

---

## ✅ Soluções

### Problema 1: Erro no Login (localhost:3000)

#### Causa:
- Senha incorreta ou não encontrada
- Usuário incorreto

#### Soluções:

**1. Obter senha correta:**

```bash
# No node1
# Método 1: Secret padrão
kubectl get secret -n monitoring grafana -o jsonpath='{.data.admin-password}' | base64 -d
echo ""

# Método 2: Outro secret
kubectl get secrets -n monitoring | grep grafana
kubectl get secret -n monitoring <grafana-secret-name> -o jsonpath='{.data.admin-password}' | base64 -d

# Método 3: Listar todos os secrets
kubectl get secrets -n monitoring
```

**2. Senhas comuns a tentar:**
- `admin` (padrão Grafana)
- `TriSLA2025!` (senha que configuramos)
- `trisla123` (senha nos scripts)
- `prom-operator` (se instalado via kube-prometheus-stack)

**3. Redefinir senha (se necessário):**

```bash
# No node1, redefinir senha do Grafana
kubectl exec -it -n monitoring deployment/monitoring-grafana -- grafana-cli admin reset-admin-password novaSenha123
```

---

### Problema 2: Timeout no IP (192.168.10.16:30000)

#### Causas Possíveis:

1. **Grafana não tem NodePort configurado**
2. **Firewall bloqueando porta**
3. **Porta NodePort incorreta**

#### Soluções:

**1. Verificar tipo de Service:**

```bash
# No node1
kubectl get svc -n monitoring | grep grafana
```

Se mostrar `ClusterIP`, o Grafana **não está exposto via NodePort**.

**2. Verificar NodePort (se configurado):**

```bash
# No node1
kubectl get svc -n monitoring -o jsonpath='{.items[?(@.metadata.name==*"grafana"*)].spec.ports[?(@.port==80||@.port==3000)].nodePort}'
```

**3. Configurar NodePort (se necessário):**

```bash
# No node1
kubectl patch svc -n monitoring monitoring-grafana -p '{"spec":{"type":"NodePort"}}'

# Ou criar/editar service
kubectl get svc -n monitoring monitoring-grafana -o yaml > grafana-svc.yaml
# Editar grafana-svc.yaml: mudar type para NodePort
kubectl apply -f grafana-svc.yaml
```

**4. Verificar Firewall:**

```bash
# No node1
sudo ufw status
sudo iptables -L -n | grep 30000

# Se firewall estiver bloqueando, permitir:
sudo ufw allow 30000/tcp
# ou
sudo iptables -A INPUT -p tcp --dport 30000 -j ACCEPT
```

**5. Usar Port-Forward (Alternativa):**

```bash
# No node1
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &

# No seu Windows, configurar SSH tunnel:
ssh -L 3000:localhost:3000 porvir5g@192.168.10.16

# Depois acessar: http://localhost:3000
```

---

## 🎯 Solução Recomendada

### Para Login (localhost:3000):

```bash
# No node1
# 1. Obter senha
GRAFANA_PASS=$(kubectl get secret -n monitoring grafana -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d)
echo "Usuário: admin"
echo "Senha: $GRAFANA_PASS"

# Se não encontrar, tentar senhas comuns:
# - TriSLA2025!
# - trisla123
# - admin
```

### Para Acesso via IP (192.168.10.16):

**Opção A: Configurar NodePort**

```bash
# No node1
# Verificar se existe NodePort
kubectl get svc -n monitoring | grep grafana

# Se não tiver, configurar:
kubectl patch svc -n monitoring monitoring-grafana -p '{"spec":{"type":"NodePort","ports":[{"port":80,"targetPort":3000,"nodePort":30000}]}}'

# Verificar NodePort
kubectl get svc -n monitoring monitoring-grafana
```

**Opção B: Usar Port-Forward com SSH Tunnel**

No seu Windows:
```powershell
# Criar tunnel SSH
ssh -L 3000:localhost:3000 porvir5g@192.168.10.16

# Manter terminal aberto
# Acessar: http://localhost:3000
```

---

## ✅ Checklist de Resolução

- [ ] Obter senha correta do Grafana
- [ ] Fazer login em localhost:3000 com senha correta
- [ ] Verificar se Grafana tem NodePort
- [ ] Se não tiver, configurar NodePort
- [ ] Verificar firewall se NodePort não funcionar
- [ ] Ou usar SSH tunnel como alternativa

---

## 💡 Comandos Rápidos

```bash
# No node1 - Obter tudo de uma vez
echo "=== GRAFANA INFO ==="
echo "Service Type:"
kubectl get svc -n monitoring | grep grafana
echo ""
echo "Senha:"
kubectl get secret -n monitoring grafana -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d || echo "Tente: TriSLA2025! ou trisla123"
echo ""
echo "NodePort:"
kubectl get svc -n monitoring monitoring-grafana -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "Não configurado"
```




