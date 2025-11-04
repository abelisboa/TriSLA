# Como Copiar Dashboards para node1

## 📋 Opção 1: Copiar via SCP Manualmente

No seu terminal do Windows/PowerShell, execute:

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

## 📋 Opção 2: Criar Arquivos Diretamente no node1

Já que você já está conectado no node1, pode criar os arquivos diretamente:

### No node1, execute:

```bash
# Criar diretório
mkdir -p ~/gtp5g/trisla-portal/grafana-dashboards
cd ~/gtp5g/trisla-portal

# Os arquivos JSON dos dashboards precisam ser copiados do seu repositório local
# Ou você pode criar um arquivo temporário e depois importar via URL do GitHub
```

## 📋 Opção 3: Usar git clone/pull

Se os arquivos estão no repositório Git:

```bash
# No node1
cd ~/gtp5g/trisla-portal
git pull  # Se já tiver o repo clonado
# ou
git clone <repo-url>  # Se for um novo clone
```

## 📋 Opção 4: Copiar via interface web do Grafana

Alternativamente, você pode importar diretamente via interface web do Grafana:

1. Acessar: http://192.168.10.16:30000 (ou via port-forward)
2. Ir em: **Dashboards** > **Import**
3. Colar o conteúdo JSON de cada dashboard
4. Salvar

## ✅ Após Copiar, Importar

Depois de copiar os arquivos para o node1, execute:

```bash
# No node1
cd ~/gtp5g/trisla-portal

# Verificar arquivos
ls -lh grafana-dashboards/*.json

# Importar dashboards
chmod +x scripts/import_grafana_dashboards_fixed.sh
./scripts/import_grafana_dashboards_fixed.sh
```

## 🎯 Solução Mais Rápida

Se você tiver acesso SSH ao node1 e os arquivos estiverem em um repositório Git público, pode fazer:

```bash
# No node1
cd ~/gtp5g/trisla-portal
git pull origin main  # ou branch apropriada
```

Isso vai baixar os arquivos automaticamente se estiverem no repositório.




