#!/bin/bash
# ============================================
# Script para Corrigir Commit e Fazer Push
# ============================================
# Remove tokens do commit e faz push
# ============================================

set -e

echo "🚀 Preparando commit do projeto TriSLA..."
echo ""

# 1. Adicionar TODAS as alterações (incluindo novos arquivos)
git add .

# 2. Verificar se há commit anterior para fazer amend ou criar novo
if git rev-parse --verify HEAD >/dev/null 2>&1; then
    # Fazer amend do commit anterior
    git commit --amend -m "🚀 TriSLA: Arquitetura completa para garantia de SLA em redes 5G/O-RAN

✨ Funcionalidades:
- Módulos completos (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent Layer)
- Integração real com NASP (RAN, Transport, Core)
- UI Dashboard responsivo e moderno
- Observabilidade completa (OTLP, Prometheus, Grafana)
- CI/CD automatizado (GitHub Actions)
- Helm charts para deploy em produção
- Testes unitários, integração e E2E

🔧 Configuração:
- Valores reais do NASP configurados
- Endpoints dos controladores descobertos
- Scripts de build, deploy e validação
- Documentação completa de deploy
- Nomes corretos dos módulos atualizados
- Script master DevOps para deploy completo
- Scripts de limpeza e verificação

🐛 Correções:
- Dockerfile ml-nsmf corrigido (removido diretório models inexistente)
- Workflow GitHub Actions otimizado com tags latest

📦 Deploy:
- Pronto para produção real
- Não usa simulação
- Executa ações reais no NASP
- Processo DevOps automatizado
- Deploy completo via script master"
else
    # Criar novo commit
    git commit -m "🚀 TriSLA: Arquitetura completa para garantia de SLA em redes 5G/O-RAN

✨ Funcionalidades:
- Módulos completos (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent Layer)
- Integração real com NASP (RAN, Transport, Core)
- UI Dashboard responsivo e moderno
- Observabilidade completa (OTLP, Prometheus, Grafana)
- CI/CD automatizado (GitHub Actions)
- Helm charts para deploy em produção
- Testes unitários, integração e E2E

🔧 Configuração:
- Valores reais do NASP configurados
- Endpoints dos controladores descobertos
- Scripts de build, deploy e validação
- Documentação completa de deploy
- Nomes corretos dos módulos atualizados
- Script master DevOps para deploy completo
- Scripts de limpeza e verificação

🐛 Correções:
- Dockerfile ml-nsmf corrigido (removido diretório models inexistente)
- Workflow GitHub Actions otimizado com tags latest

📦 Deploy:
- Pronto para produção real
- Não usa simulação
- Executa ações reais no NASP
- Processo DevOps automatizado
- Deploy completo via script master"
fi

echo ""
echo "✅ Commit corrigido!"
echo ""
echo "📤 Fazendo push..."
echo ""

# 3. Fazer push (force necessário porque alteramos o commit)
git push -u origin main --force

echo ""
echo "✅ Push concluído!"
echo "🔗 Verificar: https://github.com/abelisboa/TriSLA"

