# 🎯 Solução Final: Importar Dashboards TriSLA

## ✅ Situação Atual

- ✅ Você está no node1
- ✅ Grafana está acessível em http://localhost:3000
- ⚠️ Arquivos JSON dos dashboards não existem no node1 ainda
- ✅ Pode importar diretamente via interface web

---

## 🚀 SOLUÇÃO RECOMENDADA: Interface Web do Grafana

### Passos no node1:

```bash
# 1) Verificar se Grafana está acessível
curl -s http://localhost:3000/api/health | jq .

# 2) Se não estiver, configurar port-forward (se necessário)
# Mas parece que já está acessível!
```

### No navegador do seu computador:

#### Opção A: Via NodePort (se configurado)

1. **Acessar**: http://192.168.10.16:30000
   - Verificar NodePort: `kubectl get svc -n monitoring | grep grafana`

2. **Login**: 
   - Usuário: `admin`
   - Senha: `TriSLA2025!`

3. **Importar Dashboards**:
   - Ir em: **Dashboards** → **Import**
   - Escolher: **Upload JSON file** ou **Paste JSON**
   - Para cada dashboard:
     - Abrir arquivo JSON no Windows (ex: `trisla-complete-main.json`)
     - Copiar todo conteúdo (Ctrl+A, Ctrl+C)
     - Colar no Grafana (Paste JSON)
     - Clicar em **Load**
     - Clicar em **Import**

#### Opção B: Via Port-Forward do node1 para seu PC

1. **No node1, configurar port-forward**:
   ```bash
   # Verificar se porta 3000 já está em uso
   netstat -tlnp | grep 3000
   
   # Se não estiver, configurar port-forward para sua máquina
   # Mas você precisaria de acesso SSH reverso ou VPN
   ```

2. **Ou usar NodePort diretamente**: http://192.168.10.16:30000

---

## 📋 Arquivos para Importar (na ordem)

1. ✅ `trisla-complete-main.json` - Dashboard Principal
2. ✅ `trisla-slices-management.json` - Gestão de Slices  
3. ✅ `trisla-metrics-detailed.json` - Métricas Detalhadas
4. ✅ `trisla-admin-panel.json` - Painel Admin
5. ✅ `trisla-create-slices.json` - Criar Slices
6. ✅ `trisla-centralized-view.json` - Visão Centralizada

---

## 🔧 Alternativa: Criar Arquivos no node1 via cat

Se você quiser criar os arquivos no node1 para depois importar via API:

```bash
# No node1
cd ~/gtp5g/trisla-portal
mkdir -p grafana-dashboards

# Exemplo: Criar primeiro dashboard
# Você precisa ter o conteúdo JSON completo
cat > grafana-dashboards/trisla-complete-main.json << 'EOF'
[colar conteúdo JSON completo aqui]
EOF

# Depois importar via API
./scripts/import_grafana_dashboards_fixed.sh
```

---

## 🎯 RECOMENDAÇÃO FINAL

**Use a interface web do Grafana** - é mais simples:

1. **Acessar Grafana**: http://192.168.10.16:30000 (NodePort)
2. **Login**: admin / TriSLA2025!
3. **Importar cada dashboard via UI** (Paste JSON)
4. ✅ Pronto! Dashboards funcionando em tempo real

---

## 📝 Checklist

- [ ] Verificar NodePort do Grafana: `kubectl get svc -n monitoring | grep grafana`
- [ ] Acessar Grafana no navegador: http://192.168.10.16:30000
- [ ] Fazer login: admin / TriSLA2025!
- [ ] Importar cada dashboard via UI (Paste JSON)
- [ ] Verificar se dashboards aparecem na lista
- [ ] Verificar se métricas aparecem em tempo real

---

## 💡 Dica

Se você tiver os arquivos JSON no seu Windows:
1. Abra cada arquivo no Windows
2. Copie todo conteúdo (Ctrl+A, Ctrl+C)
3. No Grafana, cola no "Paste JSON"
4. Importa e repete para cada dashboard

**Muito mais simples que copiar arquivos via SSH!**




