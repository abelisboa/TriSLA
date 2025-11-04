# 🚀 Prompts Sequenciais para Geração de Dashboard TriSLA

Este documento contém uma série de prompts estruturados para gerar um Dashboard TriSLA completo usando qualquer IA generativa. Os prompts são organizados em sequência, com mecanismos de controle para garantir a continuidade entre múltiplas interações.

## 📋 Índice de Prompts
1. [Prompt #1: Configuração Inicial](#prompt-1-configuração-inicial)
2. [Prompt #2: Backend FastAPI](#prompt-2-backend-fastapi)
3. [Prompt #3: Frontend React Básico](#prompt-3-frontend-react-básico)
4. [Prompt #4: Integração com Prometheus](#prompt-4-integração-com-prometheus)
5. [Prompt #5: Componentes de Dashboard](#prompt-5-componentes-de-dashboard)
6. [Prompt #6: Visualizações e Gráficos](#prompt-6-visualizações-e-gráficos)
7. [Prompt #7: Scripts de Automação](#prompt-7-scripts-de-automação)
8. [Prompt #8: Finalização e Documentação](#prompt-8-finalização-e-documentação)
9. [Prompt de Recuperação](#prompt-de-recuperação)

---

## Prompt #1: Configuração Inicial

```
PROMPT #1 | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Preciso desenvolver um Dashboard TriSLA completo para monitoramento de métricas do sistema TriSLA. O dashboard deve conectar-se ao Prometheus via túnel SSH e exibir métricas em tempo real.

ARQUIVOS CRIADOS:
Nenhum ainda.

PRÓXIMOS PASSOS:
1. Criar estrutura de diretórios do projeto
2. Configurar ambiente de desenvolvimento
3. Inicializar projetos backend e frontend

INSTRUÇÕES:
Crie a estrutura inicial do projeto Dashboard TriSLA com:

1. Uma pasta raiz chamada "trisla-dashboard-local" contendo:
   - Pasta "backend" para API FastAPI
   - Pasta "frontend" para aplicação React/TypeScript
   - Pasta "scripts" para scripts de automação

2. Para o backend:
   - Arquivo requirements.txt com dependências (FastAPI, uvicorn, httpx)
   - Estrutura básica do arquivo main.py

3. Para o frontend:
   - Configuração do projeto React com TypeScript e Vite
   - package.json com dependências necessárias
   - Configuração de TailwindCSS

4. Arquivos README.md básicos explicando a estrutura

Forneça comandos de inicialização para ambos os projetos.
```

---

## Prompt #2: Backend FastAPI

```
PROMPT #2 | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Estrutura básica criada. Agora preciso implementar o backend FastAPI que servirá como proxy para o Prometheus.

ARQUIVOS CRIADOS:
- trisla-dashboard-local/
  - backend/
    - requirements.txt
    - main.py (estrutura básica)
  - frontend/
    - package.json
    - tsconfig.json
    - vite.config.ts
  - scripts/
  - README.md

PRÓXIMOS PASSOS:
1. Implementar API FastAPI completa
2. Criar endpoints para consultas ao Prometheus
3. Implementar tratamento de erros e fallbacks

INSTRUÇÕES:
Desenvolva o backend FastAPI completo em main.py com:

1. Configuração da aplicação FastAPI com título e descrição
2. Middleware CORS para permitir requisições do frontend
3. Variável de ambiente para URL do Prometheus (padrão: http://localhost:9090)
4. Cliente HTTP assíncrono (httpx) com timeout configurável
5. Funções para consultar o Prometheus:
   - query_prometheus() para consultas simples
   - query_range_prometheus() para consultas de intervalo
6. Endpoints principais:
   - GET /health - Health check que funciona mesmo sem Prometheus
   - GET /api/prometheus/health - Verifica conexão com Prometheus
   - GET /api/prometheus/metrics/slices - Métricas de slices
   - GET /api/prometheus/metrics/system - Métricas do sistema
   - GET /api/prometheus/metrics/jobs - Métricas de jobs
   - GET /api/prometheus/metrics/timeseries - Séries temporais para gráficos
   - POST /api/prometheus/query - Executa query PromQL customizada
7. Tratamento de erros para funcionar mesmo quando Prometheus estiver inacessível

O código deve ser assíncrono, bem documentado e seguir boas práticas.
```

---

## Prompt #3: Frontend React Básico

```
PROMPT #3 | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Backend FastAPI implementado com endpoints para Prometheus. Agora preciso desenvolver o frontend React básico.

ARQUIVOS CRIADOS:
- backend/ (completo com endpoints)
- frontend/ (estrutura básica)
- scripts/ (vazio)

PRÓXIMOS PASSOS:
1. Configurar estrutura do frontend React/TypeScript
2. Criar componentes básicos
3. Configurar roteamento e layout

INSTRUÇÕES:
Desenvolva o frontend React básico com:

1. Estrutura de diretórios organizada:
   - src/components/ - Componentes reutilizáveis
   - src/pages/ - Páginas da aplicação
   - src/services/ - Serviços de API
   - src/utils/ - Funções utilitárias

2. Arquivos principais:
   - src/main.tsx - Ponto de entrada
   - src/App.tsx - Componente principal com roteamento
   - src/index.css - Estilos globais com TailwindCSS
   - src/components/Layout.tsx - Layout compartilhado
   - src/pages/Dashboard.tsx - Página principal (vazia por enquanto)
   - src/pages/SlicesManagement.tsx - Página de gestão de slices (vazia)
   - src/pages/Metrics.tsx - Página de métricas detalhadas (vazia)
   - src/services/api.ts - Cliente Axios para API backend

3. Configuração:
   - React Router para navegação
   - React Query para gerenciamento de estado e cache
   - Cliente Axios para comunicação com o backend

4. Layout básico com:
   - Barra de navegação
   - Menu lateral ou tabs
   - Área de conteúdo principal
   - Rodapé simples

Use TailwindCSS para estilização e garanta que a aplicação seja responsiva.
```

---

## Prompt #4: Integração com Prometheus

```
PROMPT #4 | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Backend e frontend básicos implementados. Agora preciso integrar o frontend com o backend para consultar métricas do Prometheus.

ARQUIVOS CRIADOS:
- backend/ (completo)
- frontend/ (estrutura básica com componentes vazios)
- scripts/ (vazio)

PRÓXIMOS PASSOS:
1. Implementar serviço de API no frontend
2. Criar funções utilitárias para processar dados do Prometheus
3. Implementar hooks React Query para consultas

INSTRUÇÕES:
Desenvolva a integração do frontend com o backend:

1. Em src/services/api.ts:
   - Configure cliente Axios com URL base do backend
   - Implemente funções para cada endpoint do backend
   - Adicione tipagem TypeScript para respostas

2. Em src/utils/dataHelpers.ts:
   - Crie funções para processar dados do Prometheus de forma segura
   - Implemente validações para evitar erros com dados ausentes
   - Adicione funções para formatação de valores numéricos

3. Hooks React Query:
   - Configure React Query Provider em main.tsx
   - Implemente hooks para cada tipo de consulta
   - Configure refetch intervals adequados
   - Implemente tratamento de erros e estados de loading

4. Atualize src/pages/Dashboard.tsx para:
   - Consultar o endpoint /api/prometheus/health
   - Exibir status de conexão com Prometheus
   - Implementar fallbacks para quando Prometheus estiver indisponível

Garanta que o frontend funcione mesmo quando o Prometheus não estiver acessível, exibindo mensagens apropriadas e valores padrão.
```

---

## Prompt #5: Componentes de Dashboard

```
PROMPT #5 | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Integração com backend implementada. Agora preciso desenvolver os componentes principais do dashboard.

ARQUIVOS CRIADOS:
- backend/ (completo)
- frontend/ (com integração backend)
  - src/services/api.ts (completo)
  - src/utils/dataHelpers.ts (completo)
  - src/pages/ (estrutura básica)

PRÓXIMOS PASSOS:
1. Desenvolver componentes reutilizáveis
2. Implementar página Dashboard principal
3. Implementar página de gestão de Slices

INSTRUÇÕES:
Desenvolva os componentes principais do dashboard:

1. Componentes reutilizáveis em src/components/:
   - MetricCard.tsx - Card para exibir métricas individuais
   - StatusIndicator.tsx - Indicador de status (up/down)
   - LoadingSpinner.tsx - Indicador de carregamento
   - ErrorMessage.tsx - Mensagem de erro padronizada

2. Página Dashboard (src/pages/Dashboard.tsx):
   - Status de conexão com Prometheus
   - Cards de métricas principais:
     - Slices Ativos
     - Componentes UP
     - CPU Médio
     - Memória (MB)
   - Seção de informações adicionais do sistema

3. Página SlicesManagement (src/pages/SlicesManagement.tsx):
   - Lista de slices ativos
   - Agrupamento por tipo
   - Indicadores de status
   - Métricas por slice

Use TailwindCSS para estilização e garanta que os componentes sejam responsivos. Implemente tratamento para estados de loading, erro e dados vazios.
```

---

## Prompt #6: Visualizações e Gráficos

```
PROMPT #6 | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Componentes básicos e páginas principais implementados. Agora preciso adicionar visualizações e gráficos para métricas.

ARQUIVOS CRIADOS:
- backend/ (completo)
- frontend/ (com páginas básicas)
  - src/components/ (componentes básicos)
  - src/pages/Dashboard.tsx (implementado)
  - src/pages/SlicesManagement.tsx (implementado)
  - src/pages/Metrics.tsx (vazio)

PRÓXIMOS PASSOS:
1. Implementar página de métricas detalhadas
2. Adicionar gráficos e visualizações
3. Implementar consultas de séries temporais

INSTRUÇÕES:
Desenvolva visualizações e gráficos para métricas:

1. Instale e configure Recharts:
   - Adicione a biblioteca ao package.json
   - Crie componentes reutilizáveis para gráficos

2. Implemente a página Metrics (src/pages/Metrics.tsx):
   - Gráfico de linha para requisições HTTP ao longo do tempo
   - Gráfico de barras para uso de CPU por componente
   - Gráfico de área para uso de memória
   - Seletor de intervalo de tempo (1h, 6h, 24h)

3. Adicione gráficos menores ao Dashboard:
   - Sparkline de requisições recentes
   - Indicador de tendência para uso de recursos

4. Implemente consultas de séries temporais:
   - Use o endpoint /api/prometheus/metrics/timeseries
   - Configure atualização periódica de dados
   - Implemente cache com React Query

5. Adicione interatividade aos gráficos:
   - Tooltips ao passar o mouse
   - Zoom/pan em séries temporais
   - Legendas clicáveis

Garanta que os gráficos sejam responsivos e se adaptem a diferentes tamanhos de tela. Implemente estados de loading e fallbacks para quando não houver dados.
```

---

## Prompt #7: Scripts de Automação

```
PROMPT #7 | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Dashboard funcional implementado. Agora preciso criar scripts de automação para facilitar o uso.

ARQUIVOS CRIADOS:
- backend/ (completo)
- frontend/ (completo com visualizações)
- scripts/ (vazio)

PRÓXIMOS PASSOS:
1. Criar scripts para Windows (PowerShell)
2. Criar scripts para Linux/WSL (Bash)
3. Implementar menu interativo para WSL

INSTRUÇÕES:
Desenvolva scripts de automação para o projeto:

1. Scripts PowerShell (pasta scripts/):
   - start-backend-and-open.ps1 - Inicia backend e abre no navegador
   - start-frontend.ps1 - Inicia frontend
   - start-all.ps1 - Inicia backend, frontend e abre navegador
   - start-ssh-tunnel.ps1 - Estabelece túnel SSH para Prometheus

2. Scripts Bash (pasta scripts-wsl/):
   - start-backend.sh - Inicia backend
   - start-frontend.sh - Inicia frontend
   - start-all.sh - Inicia backend e frontend
   - start-ssh-tunnel.sh - Estabelece túnel SSH para Prometheus
   - stop-all.sh - Para todos os serviços

3. Menu interativo para WSL (scripts-wsl/dashboard-menu.sh):
   - Interface de menu com opções numeradas
   - Opções para iniciar/parar serviços
   - Opções para abrir URLs no navegador
   - Status dos serviços
   - Visualização de logs

Os scripts devem ser robustos, com verificações de erro e mensagens claras. O menu interativo deve ser colorido e fácil de usar.
```

---

## Prompt #8: Finalização e Documentação

```
PROMPT #8 | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Dashboard e scripts de automação implementados. Agora preciso finalizar o projeto com documentação.

ARQUIVOS CRIADOS:
- backend/ (completo)
- frontend/ (completo)
- scripts/ (completo)
- scripts-wsl/ (completo)

PRÓXIMOS PASSOS:
1. Criar documentação abrangente
2. Implementar melhorias finais
3. Preparar guias de uso

INSTRUÇÕES:
Finalize o projeto com documentação e melhorias:

1. Documentação principal:
   - README.md atualizado com visão geral e instruções
   - SETUP.md com passos detalhados de instalação
   - USAGE.md com guia de uso
   - ARCHITECTURE.md explicando a arquitetura

2. Melhorias finais:
   - Tratamento de erros aprimorado
   - Validação de dados mais robusta
   - Otimizações de performance

3. Guias específicos:
   - WINDOWS_GUIDE.md para usuários Windows
   - WSL_GUIDE.md para usuários WSL
   - TROUBLESHOOTING.md para resolução de problemas

4. Documentação técnica:
   - API_REFERENCE.md para endpoints do backend
   - PROMETHEUS_INTEGRATION.md explicando a integração

A documentação deve ser clara, com exemplos e capturas de tela quando apropriado. Inclua diagramas simples para explicar a arquitetura.
```

---

## Prompt de Recuperação

Use este prompt se precisar retomar o desenvolvimento após uma interrupção ou se a IA perder o contexto:

```
PROMPT #RECOVERY | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Estou desenvolvendo um Dashboard TriSLA e preciso retomar o trabalho. O último estado conhecido é:

[Descreva o último estado conhecido do projeto, incluindo:
- Quais partes foram implementadas
- Quais arquivos existem
- Onde você parou]

ARQUIVOS CRIADOS:
[Liste os principais arquivos já criados]

ÚLTIMO ESTADO:
[Descreva o último estado funcional]

PRÓXIMOS PASSOS:
[Liste os próximos passos planejados]

INSTRUÇÕES:
Continue a implementação do Dashboard TriSLA a partir do ponto onde paramos. Primeiro, analise o estado atual e confirme seu entendimento. Em seguida, continue com a implementação dos próximos passos.

[Adicione instruções específicas para o que precisa ser feito agora]
```

---

## Instruções de Uso dos Prompts

1. **Sequência**: Use os prompts na ordem numerada (1-8)
2. **Controle de Contexto**: Cada prompt contém um hash de contexto (TRISLA-INIT) para manter a continuidade
3. **Arquivos Criados**: Atualize a lista de arquivos criados em cada prompt subsequente
4. **Recuperação**: Use o prompt de recuperação se a IA perder o contexto
5. **Adaptação**: Ajuste os prompts conforme necessário com base nas respostas da IA

Para projetos maiores, você pode dividir cada prompt em partes menores, mantendo o mesmo hash de contexto e incrementando o número do prompt (ex: #5.1, #5.2).

---

## Dicas para Gerenciamento de Tokens

1. **Foco em um componente por vez**: Em vez de pedir todo o código de uma vez, peça por componentes específicos
2. **Priorize estrutura sobre implementação**: Primeiro obtenha a estrutura, depois os detalhes
3. **Use referências cruzadas**: Mencione arquivos já criados para estabelecer contexto
4. **Solicite código parcial**: Para arquivos grandes, peça implementações parciais
5. **Verifique a compreensão**: Peça à IA para resumir o que entendeu antes de continuar

Seguindo estas instruções e usando os prompts sequenciais, você poderá gerar um Dashboard TriSLA completo e funcional usando qualquer IA generativa, mantendo a continuidade entre múltiplas interações.




