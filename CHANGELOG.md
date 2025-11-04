# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [3.2.4] - 2024-XX-XX

### Adicionado
- Backend FastAPI com suporte a métricas Prometheus
- Frontend React + Vite com Nginx
- Helm charts para deploy no Kubernetes
- CI/CD com GitHub Actions
- Docker Compose para desenvolvimento local
- Scripts utilitários (build, test, deploy)
- Documentação completa de operações
- ServiceMonitor para coleta automática de métricas
- Dashboard Grafana via ConfigMap

### Documentação
- README.md com visão geral do projeto
- README_OPERATIONS_PROD.md com guia completo de operações
- CONTRIBUTING.md com diretrizes de contribuição
- env.example com exemplos de configuração

### Infraestrutura
- Health checks (liveness e readiness probes)
- Resource limits e requests configuráveis
- Variáveis de ambiente para configuração
- Nginx configurado com proxy reverso para API

[3.2.4]: https://github.com/abelisboa/trisla-public/releases/tag/v3.2.4



