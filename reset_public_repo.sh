#!/usr/bin/env bash

# ============================================================
# 🧨 RESET GERAL — PUBLICAÇÃO PÚBLICA TRI-SLA v3.3.4
# ============================================================
# Este script:
#  1️⃣ Limpa arquivos não rastreados localmente
#  2️⃣ Mantém somente os arquivos permitidos pelo .gitignore
#  3️⃣ Gera e publica o novo README oficial (v3.3.4 Ansible)
# ============================================================

cd /mnt/c/Users/USER/Documents/trisla-deploy/release/TriSLA

echo "------------------------------------------------------------"
echo "🚀 Iniciando RESET GERAL do repositório TriSLA..."
echo "------------------------------------------------------------"

# ⚠️ 1️⃣ Confirmar variáveis e autenticação
REPO_URL="https://github.com/abelisboa/TriSLA.git"
REPO="abelisboa/TriSLA"
BRANCH="main"

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "❌ ERRO: variável GITHUB_TOKEN não definida!"
  echo "Defina com: export GITHUB_TOKEN=<token>"
  exit 1
fi

# 🧹 2️⃣ Limpar arquivos não rastreados (mas NÃO deletar o repositório remoto)
echo "🧹 Limpando arquivos locais não rastreados..."
git clean -fd
git reset --hard HEAD

# ⚙️ 3️⃣ Verificar .gitignore
echo "🔒 Verificando .gitignore..."
if [ -f .gitignore ]; then
  echo "✅ .gitignore encontrado"
  cat .gitignore
else
  echo "⚠️  .gitignore não encontrado, criando básico..."
  cat > .gitignore << 'GITIGNORE'
# Build e cache
*.zip
*.tar.gz
*.log
__pycache__/
venv/
node_modules/

# Backup e temporários
backup*/
*.tmp
*.bak

# Arquivos internos
*.pptx
*.pdf
*.tex
GITIGNORE
fi

# 📘 4️⃣ Gerar README público (v3.3.4)
echo "📘 Gerando README público (v3.3.4)..."

cat > README.md << 'EOF'
# 🛰️ TriSLA v3.3.4  

### Uma Arquitetura SLA-Aware Baseada em Inteligência Artificial, Ontologia e Contratos Inteligentes para Garantia de SLA em Redes 5G/O-RAN

---

## 📘 **1. Introdução e Contexto**

O **TriSLA** é uma arquitetura modular e híbrida que automatiza o **ciclo de vida de SLAs em redes 5G/O-RAN**, integrando:

- **Ontologia Semântica (SEM-NSMF)** — interpretação de solicitações em linguagem natural;
- **Inteligência Artificial (ML-NSMF)** — tomada de decisão sobre viabilidade e alocação;
- **Contratos Inteligentes (BC-NSSMF)** — execução e auditoria automatizada via blockchain.

A implantação é feita **via Ansible + Helm**, garantindo consistência entre ambientes locais e distribuídos.

---

## ⚙️ **2. Requisitos e Dependências**

| Componente | Versão mínima | Descrição |
|-------------|----------------|------------|
| Ubuntu | 22.04 LTS+ | Sistema base |
| Docker / BuildKit | 27+ | Build de imagens |
| Python | 3.10+ | Backend (IA e Ontologia) |
| Node.js / npm | 18+ | Frontend UI/Dashboard |
| Helm | 3.14+ | Orquestração Kubernetes |
| kubectl | 1.28+ | Gerenciamento |
| Ansible | 2.16+ | Automação |
| Prometheus / Grafana | Latest | Observabilidade |

---

## 🧱 **3. Estrutura de Diretórios**

```
trisla/
├── ansible/              # Automação híbrida via playbooks
│   └── playbooks/
├── apps/                 # Backend e frontend
├── helm/                 # Charts Kubernetes
├── monitoring/           # Prometheus / Grafana
├── scripts/              # Automação e manutenção
└── docs/                 # Documentação e exemplos
```

---

## 🚀 **4. Instalação via Ansible**

### Configurar inventário (`ansible/inventory.yml`)

```yaml
all:
  hosts:
    node1:
      ansible_host: <IP_DO_NODE1>
      ansible_user: <USUARIO>
    node2:
      ansible_host: <IP_DO_NODE2>
      ansible_user: <USUARIO>
  children:
    trisla_nodes:
      hosts:
        node1:
        node2:
```

### Executar o playbook

```bash
cd ansible
ansible-playbook -i inventory.yml playbooks/deploy_trisla.yaml
```

---

## 📊 **5. Observabilidade**

### Instalar Prometheus e Grafana

```bash
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace
```

### Dashboards esperados

- SLA Success Ratio
- API Latency
- Resource Usage
- Blockchain Audit

---

## 🧾 **6. Licença e Créditos**

**TriSLA © 2025**

**Autor:** Abel Lisboa — Mestrando PPGCA / UNISINOS

**Licença:** MIT (uso acadêmico e pesquisa)

**Repositório:** https://github.com/abelisboa/TriSLA

EOF

# 🖼️ 5️⃣ Criar placeholders básicos (se convert disponível)
echo "🖼️  Criando placeholders de dashboards..."
mkdir -p docs/img

if command -v convert >/dev/null 2>&1; then
  convert -size 1093x585 xc:white -gravity center \
    -pointsize 28 -fill gray -annotate +0-100 "TriSLA Dashboard Overview" \
    -pointsize 18 -fill black -annotate +0+20 "Módulos SEM-NSMF, ML-NSMF e BC-NSSMF" \
    -pointsize 14 -fill darkgray -annotate +0+80 "Indicadores SLA Success | Resource Usage | API Latency" \
    docs/img/expected_dashboard_overview.png
  echo "✅ Placeholder criado"
else
  echo "⚠️  ImageMagick não disponível, pulando criação de placeholders"
fi

# 📦 6️⃣ Commit inicial
echo "📦 Preparando commit inicial público..."

git add .
git commit -m "🚀 Publicação pública inicial — TriSLA v3.3.4 (Ansible)" || echo "Nenhuma mudança para commitar"
git push -u origin main --force

echo "------------------------------------------------------------"
echo "✅ Repositório TriSLA limpo e publicado com versão pública!"
echo "🌐 Acesse: https://github.com/abelisboa/TriSLA"
echo "------------------------------------------------------------"
