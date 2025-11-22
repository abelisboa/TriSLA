# 10 – Infraestrutura NASP

Prompt para preparação da infraestrutura NASP.
# PROMPT — PREPARAÇÃO DA INFRA NASP PARA O TRI-SLA

Gerar instruções completas para:

## 0) Auto-configuração inicial do ambiente NASP

**Script de auto-detecção e geração de configurações base:**

Gerar script bash que:
- Detecta automaticamente a interface de rede principal do NASP
- Identifica o IP utilizado pelo Kubernetes
- Identifica o gateway padrão
- Gera automaticamente:
  - Trecho para `values.yaml` (Helm) com configurações de rede
  - Trecho de inventário Ansible com interface e IPs
  - Script de integração TriSLA ↔ NASP com variáveis de ambiente

**Informações reais do ambiente NASP:**
- Interface física principal: `my5g`
- IP utilizado pelo Kubernetes: `192.168.10.16`
- Gateway padrão: `192.168.10.1`

**Arquivos gerados:**
- `trisla_values_autogen.yaml` - Configurações de rede para Helm
- `inventory_autogen.ini` - Template de inventário Ansible
- `trisla_nasp_env.sh` - Script com variáveis de ambiente para integração

**Exemplo de script de auto-configuração:**

```bash
#!/bin/bash
# 🚀 Auto-configuração do ambiente NASP para o TriSLA
# Este snippet identifica a interface principal, IP, gateway e gera templates
# prontos para o values.yaml, inventory Ansible e scripts do TriSLA.

echo "🔍 Coletando informações do NASP..."

PRIMARY_IFACE="my5g"
PRIMARY_IP="192.168.10.16"
PRIMARY_GW="192.168.10.1"

echo "Interface física principal detectada: $PRIMARY_IFACE"
echo "IP utilizado pelo Kubernetes: $PRIMARY_IP"
echo "Gateway padrão: $PRIMARY_GW"

# 🔧 Gerando trecho values.yaml
cat <<EOF > trisla_values_autogen.yaml
network:
  interface: "$PRIMARY_IFACE"
  nodeIP: "$PRIMARY_IP"

service:
  type: ClusterIP

env:
  - name: TRISLA_NODE_INTERFACE
    value: "$PRIMARY_IFACE"
  - name: TRISLA_NODE_IP
    value: "$PRIMARY_IP"
EOF

echo "✔ values.yaml gerado: trisla_values_autogen.yaml"

# 🔧 Gerando trecho de inventário Ansible
cat <<EOF > inventory_autogen.ini
[nasp_nodes]
node1 ansible_host=<INSERIR_IP_NODE1> iface=$PRIMARY_IFACE
node2 ansible_host=<INSERIR_IP_NODE2> iface=$PRIMARY_IFACE

[kubernetes:children]
nasp_nodes
EOF

echo "✔ Inventory gerado: inventory_autogen.ini"

# 🔧 Gerando script de integração TriSLA ↔ NASP
cat <<EOF > trisla_nasp_env.sh
export TRISLA_NODE_INTERFACE="$PRIMARY_IFACE"
export TRISLA_NODE_IP="$PRIMARY_IP"
export TRISLA_GATEWAY="$PRIMARY_GW"
EOF

chmod +x trisla_nasp_env.sh

echo "✔ Script trisla_nasp_env.sh gerado e pronto."

echo "🎉 Auto-configuração concluída."
```

1) Validar cluster NASP (2 control-plane + ≥1 worker)
2) Garantir requisitos mínimos de CPU, RAM e rede
3) Validar CNI Calico
4) Configurar repositórios GHCR
5) Criar namespaces do TriSLA
6) Criar secrets (TLS, JWT, API Keys)
7) Criar StorageClass compatível
8) Configurar NodePorts ou LB
9) Validar DNS interno
10) Gerar script de verificação automática da infraestrutura

Entregar:

- Comandos completos (`kubectl`, `helm`, `ansible`)
- Arquitetura textual
- Checks automáticos
- Scripts de sanity-check
