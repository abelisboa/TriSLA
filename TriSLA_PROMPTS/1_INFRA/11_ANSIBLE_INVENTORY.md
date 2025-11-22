# 11 – Ansible Inventory

Prompt para gerar inventário Ansible.
# PROMPT — GERAR INVENTÁRIO ANSIBLE COMPLETO PARA O NASP E TRI-SLA

Gerar:

1) Inventory INI completo
2) Inventory YAML alternativo
3) Grupos:
   - control-plane
   - workers
   - nasp-services
   - trisla-services
4) Variáveis por host
5) Variáveis globais
6) Templates Jinja2 para instalação
7) Playbook para:
   - Instalar dependências
   - Copiar configs
   - Validar cluster
   - Deploy do TriSLA
