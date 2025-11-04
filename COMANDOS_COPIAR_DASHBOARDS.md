# 🚀 Comandos Prontos para Copiar Dashboards

## Opção 1: Script PowerShell (Recomendado)

No seu terminal PowerShell (Windows), execute:

```powershell
.\COPIAR_DASHBOARDS.ps1
```

## Opção 2: Comandos Individuais

No PowerShell, execute um por um:

```powershell
# Criar diretório no node1
ssh porvir5g@192.168.10.16 "mkdir -p ~/gtp5g/trisla-portal/grafana-dashboards"

# Copiar cada arquivo
scp grafana-dashboards\trisla-complete-main.json porvir5g@192.168.10.16:~/gtp5g/trisla-portal/grafana-dashboards/
scp grafana-dashboards\trisla-slices-management.json porvir5g@192.168.10.16:~/gtp5g/trisla-portal/grafana-dashboards/
scp grafana-dashboards\trisla-metrics-detailed.json porvir5g@192.168.10.16:~/gtp5g/trisla-portal/grafana-dashboards/
scp grafana-dashboards\trisla-admin-panel.json porvir5g@192.168.10.16:~/gtp5g/trisla-portal/grafana-dashboards/
scp grafana-dashboards\trisla-create-slices.json porvir5g@192.168.10.16:~/gtp5g/trisla-portal/grafana-dashboards/
scp grafana-dashboards\trisla-centralized-view.json porvir5g@192.168.10.16:~/gtp5g/trisla-portal/grafana-dashboards/
```

## Opção 3: No Terminal do node1 (se já estiver conectado)

Você pode criar os arquivos diretamente no node1 usando `cat`:

```bash
# No node1
cd ~/gtp5g/trisla-portal
mkdir -p grafana-dashboards

# Depois, copie o conteúdo de cada arquivo JSON do repositório local
# e cole diretamente no node1 usando:
cat > grafana-dashboards/trisla-complete-main.json << 'EOF'
[paste JSON content here]
EOF
```

## Opção 4: Via Git (se arquivos estiverem no repo)

```bash
# No node1
cd ~/gtp5g/trisla-portal
git pull  # Se já tiver o repo
# ou adicionar os arquivos ao repo primeiro
```

## ✅ Após Copiar

No node1, verificar e importar:

```bash
# Verificar arquivos
ls -lh grafana-dashboards/*.json

# Importar dashboards
cd ~/gtp5g/trisla-portal
chmod +x scripts/import_grafana_dashboards_fixed.sh
./scripts/import_grafana_dashboards_fixed.sh
```

---

## 🎯 Recomendação

Use o **Script PowerShell** (`COPIAR_DASHBOARDS.ps1`) - é mais simples e automatiza tudo!




