# Ansible - TriSLA NASP

Playbooks e configurações Ansible para deploy do TriSLA no NASP.

## Estrutura

```
ansible/
├── inventory.ini          # Inventory INI
├── inventory.yaml         # Inventory YAML (alternativo)
├── ansible.cfg           # Configuração do Ansible
├── group_vars/           # Variáveis por grupo
│   ├── all.yml
│   ├── control_plane.yml
│   └── workers.yml
└── playbooks/           # Playbooks
    ├── validate-cluster.yml
    ├── setup-namespace.yml
    └── deploy-trisla-nasp.yml
```

## Uso

### Validar Cluster

```bash
ansible-playbook -i inventory.ini playbooks/validate-cluster.yml
```

### Setup Namespace

```bash
ansible-playbook -i inventory.ini playbooks/setup-namespace.yml
```

### Deploy TriSLA

```bash
ansible-playbook -i inventory.ini playbooks/deploy-trisla-nasp.yml
```

## Configuração

1. Editar `inventory.ini` e substituir `<INSERIR_IP_NODE1>` e `<INSERIR_IP_NODE2>` pelos IPs reais
2. Revisar variáveis em `group_vars/all.yml`
3. Executar playbooks na ordem acima

