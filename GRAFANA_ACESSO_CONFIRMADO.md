# ✅ Grafana - Acesso Confirmado

## 🔑 Credenciais Encontradas

- **URL Local**: http://localhost:3000 ou http://localhost:30000
- **URL NodePort**: http://192.168.10.16:30000
- **Usuário**: `admin`
- **Senha**: `TriSLA2025!`
- **Secret**: `monitoring-grafana`

---

## ✅ Problema 1: Login (RESOLVIDO)

✅ **Senha encontrada**: `TriSLA2025!`

**Acesso local funcionando:**
- http://localhost:3000 ✅
- Login: admin / TriSLA2025! ✅

---

## ⚠️ Problema 2: Timeout no IP (Resolver)

**URL**: http://192.168.10.16:30000 → Timeout

**Causa**: Firewall bloqueando porta 30000

### Solução no node1:

```bash
# No node1 - Verificar firewall
sudo ufw status

# Permitir porta 30000
sudo ufw allow 30000/tcp
sudo ufw reload

# Verificar se está funcionando
curl -s http://192.168.10.16:30000/api/health

# Se ufw não estiver instalado, verificar iptables
sudo iptables -L -n | grep 30000

# Permitir via iptables (se necessário)
sudo iptables -A INPUT -p tcp --dport 30000 -j ACCEPT
sudo iptables-save
```

### Alternativa: SSH Tunnel

Se não conseguir resolver firewall, use SSH tunnel:

**No Windows (PowerShell):**

```powershell
# Criar tunnel SSH
ssh -L 30000:localhost:30000 porvir5g@192.168.10.16

# Manter terminal aberto
# Acessar: http://localhost:30000
```

---

## 🎯 Próximos Passos

### 1. Fazer Login no Grafana

**Via localhost (já funciona):**
- URL: http://localhost:3000
- Usuário: `admin`
- Senha: `TriSLA2025!`

**Via IP (após resolver firewall):**
- URL: http://192.168.10.16:30000
- Usuário: `admin`
- Senha: `TriSLA2025!`

### 2. Resolver Firewall (se timeout persistir)

```bash
# No node1
sudo ufw allow 30000/tcp
sudo ufw reload

# Testar
curl -s http://192.168.10.16:30000/api/health
```

### 3. Importar Dashboards TriSLA

Após fazer login:

1. **Via Interface Web** (Recomendado):
   - Acessar Grafana: http://localhost:3000
   - Ir em: **Dashboards** → **Import**
   - Escolher: **Paste JSON**
   - Colar conteúdo de cada dashboard JSON
   - Importar

2. **Via API** (se arquivos estiverem no node1):
   ```bash
   # No node1
   cd ~/gtp5g/trisla-portal
   ls grafana-dashboards/*.json
   
   # Se existirem, importar via script
   GRAFANA_USER="admin"
   GRAFANA_PASS="TriSLA2025!"
   GRAFANA_URL="http://localhost:3000"
   
   for dashboard in grafana-dashboards/*.json; do
     curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
       -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
       -H "Content-Type: application/json" \
       -d @"${dashboard}" | jq -r '.status // .message'
   done
   ```

---

## ✅ Checklist Final

- [x] ✅ Senha encontrada: `TriSLA2025!`
- [x] ✅ Login funcionando em localhost:3000
- [ ] ⚠️ Resolver firewall para acesso via IP (192.168.10.16:30000)
- [ ] Importar dashboards TriSLA
- [ ] Configurar datasource Prometheus (se necessário)
- [ ] Verificar métricas em tempo real

---

## 🔗 Resumo de Acesso

| Método | URL | Status |
|--------|-----|--------|
| **Local (port-forward)** | http://localhost:3000 | ✅ Funcionando |
| **NodePort (local node1)** | http://localhost:30000 | ✅ Funcionando |
| **NodePort (via IP)** | http://192.168.10.16:30000 | ⚠️ Timeout (firewall) |

**Credenciais:**
- Usuário: `admin`
- Senha: `TriSLA2025!`

---

## 💡 Dica Final

Se o timeout no IP persistir mesmo após configurar firewall, use **SSH Tunnel**:
- Mais seguro
- Não precisa abrir firewall
- Funciona de qualquer lugar

```powershell
# Windows PowerShell
ssh -L 30000:localhost:30000 porvir5g@192.168.10.16
# Manter aberto e acessar: http://localhost:30000
```




