# Contributing Guide — TriSLA

## 1. Introduction

### 1.1 Project Philosophy

**TriSLA** is an open-source project dedicated to automated management de SLAs in redes 5G/O-RAN. We value:

- **Quality over speed**: Código bem testado e documentado
- **Collaboration**: Respeito mútuo e comunicação construtiva
- **Transparency**: Decisões técnicas documentadas e discutidas
- **Continuous learning**: Espaço for crescimento e experimentação

### 1.2 Expectations for Contributors

**Before contributing, we expect you to:**

- Read this guide completely
- Familiarize yourself with a arquitetura of projeto (consulte `ARCHITECTURE_OVERVIEW.md`)
- Understand existing code antes de propor mudanças significativas
- Follow code standards e convenções estabelecidas
- Be respectful e construtivo in discussões

**Types of contributions welcome:**

- Bug fixes
- Implementation of new features
- Documentation improvements
- Performance optimizations
- Tests and code coverage
- Melhorias na experiência of desenvolvedor

### 1.3 Code of Conduct

This project segue o [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Ao participar, você concorda in manter this code. Comportamentos inaceitáveis incluem:

- Uso de linguagem ou imagens sexualizadas
- Comentários insultuosos ou depreciativos
- Ataques pessoais ou políticos
- Assédio público ou privado
- Publicação de informações privadas sem permissão

---

## 2. How to Open Issues

### 2.1 Bugs

**Before opening a bug report:**

1. Verifique se o bug já foi reportado (busque nas issues existentes)
2. Teste na versão mais recente of código
3. Tente reproduzir o bug de forma consistente

**Template for bug report:**

```markdown
## Description
Clear and concise description of bug.

## Passos for Reproduzir
1. Vá for '...'
2. Clique in '...'
3. Role até '...'
4. Veja o erro

## Comportamento Esperado
O que deveria acontecer.

## Comportamento Atual
O que está acontecendo.

## Screenshots
Se aplicável, adicione screenshots.

## Ambiente
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.10.5]
- Docker: [e.g., 20.10.12]
- Versão of TriSLA: [e.g., v1.0.0]

## Logs
```
Cole logs relevantes aqui
```

## Contexto Adicional
Qualquer outra informação relevante.
```

### 2.2 Features

**Antes de propor uma feature:**

1. Verifique se a feature has already been proposed
2. Considere se a feature se alinha com os objetivos of projeto
3. Prepare a detailed proposal

**Template for feature request:**

```markdown
## Description
Description clara of funcionalidade desejada.

## Motivação
Por que essa funcionalidade é necessária? Qual problema ela resolve?

## solution proposal
Como você imagina que isso funcionaria?

## Alternativas Consideradas
Outras soluções que você considerou.

## Impacto Esperado
- Módulos afetados: [e.g., SEM-CSMF, Decision Engine]
- Interfaces afetadas: [e.g., I-01, I-02]
- Breaking changes: [Sim/Não]

## Contexto Adicional
Qualquer outra informação relevante.
```

### 2.3 Documentação

**Issues de documentação podem incluir:**

- Correções de erros ortográficos ou gramaticais
- Melhorias na clareza e organização
- Adição de exemplos ou casos de uso
- Traduções (quando aplicável)

**Template for documentação:**

```markdown
## Arquivo(s) Afetado(s)
Liste os arquivos de documentação.

## Tipo de Mudança
- [ ] Correção de erro
- [ ] Melhoria de clareza
- [ ] Adição de conteúdo
- [ ] Reorganização

## Description
Description das mudanças propostas.
```

---

## 3. Como Criar um Fork of Repositório

### 3.1 Processo de Fork

**Passo 1: Criar Fork no GitHub**

1. Acesse: https://github.com/abelisboa/TriSLA
2. Clique no botão "Fork" no canto superior direito
3. Escolha sua conta/organização for o fork

**Passo 2: Clonar Fork Localmente**

```bash
# Clonar seu fork
git clone https://github.com/SEU_USUARIO/TriSLA.git
cd TriSLA

# Adicionar upstream (repositório original)
git remote add upstream https://github.com/abelisboa/TriSLA.git

# Verifiesr remotes
git remote -v
# Deve mostrar:
# origin    https://github.com/SEU_USUARIO/TriSLA.git (fetch)
# origin    https://github.com/SEU_USUARIO/TriSLA.git (push)
# upstream  https://github.com/abelisboa/TriSLA.git (fetch)
# upstream  https://github.com/abelisboa/TriSLA.git (push)
```

**Passo 3: Manter Fork Atualizado**

```bash
# Atualizar branch main of upstream
git fetch upstream
git checkout main
git merge upstream/main

# Push for seu fork
git push origin main
```

---

## 4. Setup Local Rápido

### 4.1 Python

**Verifiesr versão:**

```bash
python3 --version
# Deve ser Python 3.10 ou superior
```

**Instalar Python (se necessário):**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv python3-pip

# macOS
brew install python@3.10

# Windows (via Chocolatey)
choco install python310
```

### 4.2 Docker e Docker Compose

**Verifiesr instalação:**

```bash
docker --version
docker compose version
```

**Instalar Docker (se necessário):**

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin

# macOS
brew install docker docker-compose

# Windows
# Baixar Docker Desktop: https://www.docker.com/products/docker-desktop
```

### 4.3 Virtual Environment (venv)

**Criar e ativar venv:**

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar (Linux/macOS)
source .venv/bin/activate

# Ativar (Windows)
.venv\Scripts\activate

# Ativar (PowerShell)
.venv\Scripts\Activate.ps1
```

**Verifiesr ativação:**

```bash
which python
# Deve apontar for .venv/bin/python (Linux/macOS)
# ou .venv\Scripts\python.exe (Windows)
```

### 4.4 Instalar Dependências

**Dependências de desenvolvimento:**

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt
```

**Dependências por módulo (se necessário):**

```bash
# SEM-CSMF
cd apps/sem-csmf
pip install -r requirements.txt
cd ../..

# ML-NSMF
cd apps/ml-nsmf
pip install -r requirements.txt
cd ../..

# Decision Engine
cd apps/decision-engine
pip install -r requirements.txt
cd ../..
```

### 4.5 Docker Compose (Infraestrutura)

**start serviços de infraestrutura:**

```bash
# start PostgreSQL, Kafka, Prometheus, Grafana
docker compose up -d postgres kafka zookeeper prometheus grafana otlp-collector

# Verifiesr status
docker compose ps

# Ver logs
docker compose logs -f kafka
```

**Parar serviços:**

```bash
docker compose down
```

---

## 5. Criação de Branches

### 5.1 Convenções de Nomenclatura

**Formato:**

```
<tipo>/<Description-curta>
```

**Tipos de branch:**

- `feature/`: Nova funcionalidade
- `fix/` ou `bugfix/`: Correção de bug
- `hotfix/`: Correção urgente in produção
- `refactor/`: Refatoração de código
- `docs/`: Mudanças apenas in documentação
- `test/`: Adição ou correção de testes
- `chore/`: Tarefas de manutenção (dependências, build, etc.)

**Exemplos válidos:**

```bash
feature/add-owl-parser
fix/grpc-timeout-handling
hotfix/critical-memory-leak
refactor/decision-engine-service
docs/update-api-reference
test/add-integration-tests
chore/update-dependencies
```

**Exemplos inválidos:**

```bash
# Evitar:
my-feature
fix-bug
update
patch-1
```

### 5.2 Criar Branch

**A partir de main atualizada:**

```bash
# Atualizar main
git checkout main
git pull upstream main

# Criar nova branch
git checkout -b feature/nome-da-feature

# Verifiesr branch atual
git branch
# Deve mostrar * feature/nome-da-feature
```

**Push for seu fork:**

```bash
# Primeiro push (definir upstream)
git push -u origin feature/nome-da-feature

# Pushs subsequentes
git push
```

---

## 6. Padrões de Commit

### 6.1 Conventional Commits

O TriSLA segue o padrão [Conventional Commits](https://www.conventionalcommits.org/).

**Formato:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Tipos de commit:**

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças in documentação
- `style`: Formatação, ponto-e-vírgula faltando, etc. (não afeta código)
- `refactor`: Refatoração de código
- `test`: Adição ou correção de testes
- `chore`: Mudanças in build, dependências, etc.
- `perf`: Melhoria de performance
- `ci`: Mudanças in CI/CD

**Scopes (opcionais):**

- `sem-csmf`: Módulo SEM-CSMF
- `ml-nsmf`: Módulo ML-NSMF
- `decision-engine`: Módulo Decision Engine
- `bc-nssmf`: Módulo BC-NSSMF
- `sla-agent-layer`: Módulo SLA-Agent Layer
- `nasp-adapter`: Módulo NASP Adapter
- `ui-dashboard`: Módulo UI Dashboard
- `helm`: Helm charts
- `docs`: Documentação
- `ci`: CI/CD

### 6.2 Exemplos de Commits Válidos

**Commit simples:**

```bash
git commit -m "feat(sem-csmf): adicionar parser de ontologia OWL"
```

**Commit com corpo:**

```bash
git commit -m "fix(decision-engine): corrigir timeout in chamadas gRPC

O timeout estava configurado for 5s, mas in alguns casos
a chamada pode levar até 10s. Aumentar timeout for 15s
e adicionar retry com backoff exponencial.

Fixes #123"
```

**Commit com múltiplos escopos:**

```bash
git commit -m "refactor(decision-engine,ml-nsmf): padronizar tratamento de erros

Unificar tratamento de erros entre Decision Engine e ML-NSMF
usando exceções customizadas e logging estruturado."
```

**Commit de documentação:**

```bash
git commit -m "docs: atualizar guia de contribuição

Add section about testes E2E e melhorar exemplos
de commits."
```

**Commit de teste:**

```bash
git commit -m "test(decision-engine): adicionar testes unitários for rule engine

Cobrir casos de borda e cenários de falha."
```

### 6.3 Boas Práticas de Commit

**Subject (primeira linha):**

- Máximo 50 caracteres (idealmente)
- Use imperativo: "adicionar" não "adiciona" ou "adicionando"
- Não termine com ponto
- Seja específico e descritivo

**Body (opcional):**

- Explique o "o quê" e "por quê", não o "como"
- Quebre linhas in 72 caracteres
- Use for contexto adicional ou breaking changes

**Footer (opcional):**

- Referências a issues: `Fixes #123`, `Closes #456`
- Breaking changes: `BREAKING CHANGE: Description`

**Evitar:**

```bash
# ❌ Muito vago
git commit -m "fix: bug"

# ❌ Muito longo
git commit -m "fix: corrigir problema de timeout que ocorre quando o Decision Engine tenta se comunicar com o ML-NSMF in situações de alta carga"

# ❌ Não imperativo
git commit -m "feat: adicionando nova funcionalidade"

# ✅ Bom
git commit -m "fix(decision-engine): corrigir timeout in alta carga"
```

---

## 7. Como Abrir Pull Requests

### 7.1 Checklist Obrigatório

Antes de abrir um PR, verifique:

- [ ] Código segue os padrões of projeto (black, isort, flake8)
- [ ] Testes adicionados/atualizados e passando
- [ ] Documentação atualizada (se aplicável)
- [ ] Commits seguem Conventional Commits
- [ ] Branch atualizada com `main` of upstream
- [ ] Sem conflitos de merge
- [ ] CI passa (se configurado)
- [ ] Sem dados sensíveis ou tokens no código

### 7.2 Como Descrever Mudanças

**Template de PR:**

```markdown
## Description
Breve Description das mudanças.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação
- [ ] Refatoração
- [ ] Testes

## Módulos Afetados
- [ ] SEM-CSMF
- [ ] ML-NSMF
- [ ] Decision Engine
- [ ] BC-NSSMF
- [ ] SLA-Agent Layer
- [ ] NASP Adapter
- [ ] UI Dashboard
- [ ] Helm
- [ ] Documentação

## Interfaces Afetadas
- [ ] I-01 (gRPC)
- [ ] I-02 (REST)
- [ ] I-03 (Kafka)
- [ ] I-04 (Kafka)
- [ ] I-05 (Kafka)
- [ ] I-06 (REST)
- [ ] I-07 (REST)

## Como Testar
Passos for testar as mudanças:
1. ...
2. ...
3. ...

## Checklist
- [ ] Código segue padrões (black, isort, flake8)
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] CI passa
- [ ] Sem conflitos
- [ ] Sem dados sensíveis

## Screenshots (se aplicável)
...

## Contexto Adicional
Qualquer informação adicional relevante.
```

### 7.3 Política de Revisão

**Process:**

1. **Abertura of PR**: Mantenedor será notificado automaticamente
2. **Revisão inicial**: Verifiesção de checklist e CI
3. **Code review**: Pelo menos 1 aprovação necessária
4. **Feedback**: Discussão construtiva sobre mudanças
5. **Alterações**: Fazer alterações solicitadas
6. **Aprovação**: Após aprovação, mantenedor faz merge

**Expectativas:**

- **Revisores**: Sejam construtivos e respeitosos
- **Autores**: Respondam a feedback de forma profissional
- **Tempo**: Revisões podem levar alguns dias, seja paciente

**Critérios de aprovação:**

- Código segue padrões e convenções
- Testes adequados e passando
- Documentação atualizada
- Sem breaking changes não documentados
- Performance aceitável (se aplicável)

---

## 8. Rodar Testes Antes of PR

### 8.1 Testes Unitários

**Executar todos os testes unitários:**

```bash
# Na raiz of projeto
pytest tests/unit/ -v

# Com cobertura
pytest tests/unit/ --cov=apps --cov-report=html
```

**Executar testes de um módulo específico:**

```bash
# SEM-CSMF
pytest tests/unit/test_sem_csmf.py -v

# Decision Engine
pytest tests/unit/test_decision_engine.py -v
```

### 8.2 Testes de Integração

**Pré-requisitos:**

```bash
# start serviços de infraestrutura
docker compose up -d postgres kafka zookeeper
```

**Executar testes de integration:**

```bash
pytest tests/integration/ -v -m integration
```

### 8.3 Testes End-to-End (E2E)

**Pré-requisitos:**

```bash
# start stack completo
docker compose up -d
```

**Executar testes E2E:**

```bash
pytest tests/e2e/ -v -m e2e --timeout=300
```

### 8.4 Lint

**Executar todas as verificações de lint:**

```bash
# Black (formatação)
black --check apps/ tests/

# isort (imports)
isort --check-only apps/ tests/

# flake8 (linting)
flake8 apps/ tests/

# mypy (type checking, opcional)
mypy apps/
```

**Corrigir automaticamente:**

```bash
# Formatar com black
black apps/ tests/

# Ordenar imports
isort apps/ tests/
```

**Script unificado:**

```bash
# Se disponível
./scripts/validate-code.sh
```

---

## 9. Políticas de Qualidade

### 9.1 Black (Formatação)

**Configuração esperada:**

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py310']
```

**Uso:**

```bash
# Verifiesr
black --check apps/ tests/

# Formatar
black apps/ tests/
```

**Regras:**

- Linha máxima: 100 caracteres
- Aspas duplas for strings
- Trailing comma in estruturas multi-linha

### 9.2 isort (Ordenação de Imports)

**Configuração esperada:**

```toml
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
```

**Uso:**

```bash
# Verifiesr
isort --check-only apps/ tests/

# Ordenar
isort apps/ tests/
```

**Ordem de imports:**

1. Standard library
2. Third-party
3. Local application

### 9.3 mypy (Type Checking)

**Opcional, mas recomendado:**

```bash
# Verifiesr tipos
mypy apps/
```

**Configuration:**

```ini
# mypy.ini
[mypy]
python_version = 3.10
warn_return_any = True
ignore_missing_imports = True
```

### 9.4 flake8 (Linting)

**Configuration:**

```ini
# .flake8 ou setup.cfg
[flake8]
max-line-length = 100
exclude = .git,__pycache__,*.pyc,.venv,venv
ignore = E203, E501, W503
```

**Uso:**

```bash
flake8 apps/ tests/
```

**Regras importantes:**

- E203: Whitespace before ':'
- E501: Line too long (handled by black)
- W503: Line break before binary operator

---

## 10. Diretrizes de Código

### 10.1 Python

**Estilo:**

- Seguir PEP 8 (com exceções of black)
- Usar type hints quando possível
- Docstrings no formato Google ou NumPy

**Exemplo de função:**

```python
def process_intent(
    intent: Intent,
    tenant_id: str,
    validate: bool = True
) -> NEST:
    """
    Processa um intent e gera NEST.
    
    Args:
        intent: Objeto Intent a ser processado
        tenant_id: ID of tenant
        validate: Se True, valida o intent antes de processar
    
    Returns:
        NEST gerado a partir of intent
    
    Raises:
        ValueError: Se intent for inválido
        ProcessingError: Se processamento falhar
    """
    if validate:
        validate_intent(intent)
    
    # Processamento...
    nest = generate_nest(intent, tenant_id)
    return nest
```

**Nomenclatura:**

- Classes: `PascalCase` (ex: `IntentProcessor`)
- Funções/variáveis: `snake_case` (ex: `process_intent`)
- Constantes: `UPPER_SNAKE_CASE` (ex: `MAX_RETRIES`)
- Privado: prefixo `_` (ex: `_internal_method`)

**Imports:**

```python
# Standard library
import os
import sys
from typing import Dict, List, Optional

# Third-party
import fastapi
from pydantic import BaseModel

# Local
from apps.sem_csmf.src.models.intent import Intent
from apps.sem_csmf.src.nest_generator import generate_nest
```

### 10.2 TypeScript/React (UI Dashboard)

**Estilo:**

- Seguir ESLint e Prettier configurados
- Usar TypeScript strict mode
- Componentes funcionais com hooks

**Exemplo de componente:**

```typescript
import React, { useState, useEffect } from 'react';
import { Intent } from '../types/intent';

interface IntentListProps {
  tenantId: string;
  onSelect: (intent: Intent) => void;
}

export const IntentList: React.FC<IntentListProps> = ({
  tenantId,
  onSelect,
}) => {
  const [intents, setIntents] = useState<Intent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchIntents(tenantId).then(setIntents).finally(() => setLoading(false));
  }, [tenantId]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      {intents.map((intent) => (
        <div key={intent.id} onClick={() => onSelect(intent)}>
          {intent.name}
        </div>
      ))}
    </div>
  );
};
```

**Nomenclatura:**

- Componentes: `PascalCase` (ex: `IntentList`)
- Funções/variáveis: `camelCase` (ex: `fetchIntents`)
- Constantes: `UPPER_SNAKE_CASE` (ex: `API_BASE_URL`)
- Arquivos: `kebab-case` (ex: `intent-list.tsx`)

---

## 11. Como Atualizar Documentação

### 11.1 Tipos de Documentação

**Documentação de código:**

- Docstrings in funções e classes
- Type hints for clareza
- Comentários inline quando necessário

**Documentação de projeto:**

- `README.md`: Visão geral
- `ARCHITECTURE_OVERVIEW.md`: Arquitetura
- `DEVELOPER_GUIDE.md`: Guia de desenvolvimento
- `API_REFERENCE.md`: Referência de APIs
- `CONTRIBUTING.md`: This arquivo

**Documentação de módulos:**

- `apps/<module>/README.md`: Documentação específica of módulo

### 11.2 Quando Atualizar Documentação

**Sempre atualize documentação quando:**

- Adicionar nova funcionalidade
- Modificar comportamento existente
- Adicionar novos endpoints ou interfaces
- Mudar configurações ou variáveis de ambiente
- Adicionar novos módulos ou componentes

### 11.3 Formato de Documentação

**Markdown:**

- Use títulos hierárquicos (`#`, `##`, `###`)
- Blocos de código com syntax highlighting
- Listas for itens múltiplos
- Tabelas quando apropriado

**Exemplo:**

```markdown
## Nova Funcionalidade

Esta funcionalidade permite...

### Uso

```python
from apps.sem_csmf import process_intent

nest = process_intent(intent, tenant_id)
```

### Parâmetros

| Parâmetro | Tipo | Description |
|-----------|------|-----------|
| `intent` | `Intent` | Intent a ser processado |
| `tenant_id` | `str` | ID of tenant |

### Exemplo

```python
intent = Intent(
    tenant_id="tenant-001",
    intent="Criar slice for AR"
)
nest = process_intent(intent, "tenant-001")
```
```

---

## 12. Segurança

### 12.1 Não Subir Tokens

**Nunca commite:**

- Tokens de API (GitHub, GHCR, etc.)
- Chaves privadas
- Senhas ou credenciais
- Certificados privados
- Secrets de Kubernetes

**O que fazer:**

- Use variáveis de ambiente
- Use arquivos `.env` (já no `.gitignore`)
- Use secrets management (Kubernetes Secrets, etc.)
- Documente variáveis necessárias in `README.md`

**Exemplo incorreto:**

```python
# ❌ NUNCA FAÇA ISSO
API_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Exemplo correto:**

```python
# ✅ CORRETO
import os
API_TOKEN = os.getenv("GITHUB_TOKEN")
```

### 12.2 Não Expor Dados Sensíveis

**Evite:**

- Dados de produção in código de exemplo
- IPs ou hostnames de ambientes reais
- Estruturas de dados com informações reais
- Logs com informações sensíveis

**Use:**

- Dados de exemplo genéricos
- Variáveis de ambiente
- Configurações de desenvolvimento
- Sanitização de logs

### 12.3 Não Alterar Branch main Diretamente

**Regra fundamental:**

- **Nunca** faça commit direto na branch `main`
- **Sempre** crie uma branch for suas mudanças
- **Sempre** use Pull Requests for merge in `main`

**Proteção:**

- A branch `main` está protegida
- PRs são obrigatórios for merge
- Revisão de código é necessária

**Exceções:**

- Apenas mantenedores podem fazer hotfixes diretos (raramente)
- Mesmo assim, preferir branch e PR

---

## 13. Estrutura Recomendada for Contribuições Grandes

### 13.1 Planejamento

**Para contribuições grandes (>500 linhas):**

1. **Discutir primeiro**: Abra uma issue for discutir a proposal
2. **Dividir in partes**: Quebre in PRs menores e incrementais
3. **Documentar**: Documente a arquitetura e decisões técnicas
4. **Testar**: Garanta cobertura de testes adequada

### 13.2 Estratégia de Branch

**Para features grandes:**

```bash
# Branch principal of feature
feature/nova-funcionalidade

# Branches de sub-features (opcionais)
feature/nova-funcionalidade-part1
feature/nova-funcionalidade-part2
feature/nova-funcionalidade-part3
```

**Fluxo:**

1. Criar branch principal
2. Desenvolver incrementalmente
3. Abrir PRs incrementais (se possível)
4. Ou um PR grande com commits bem organizados

### 13.3 Organização de Commits

**Commits atômicos:**

```bash
# ✅ Bom: commits pequenos e focados
git commit -m "feat: adicionar parser de ontologia"
git commit -m "feat: adicionar validação de NEST"
git commit -m "test: adicionar testes for parser"

# ❌ Evitar: commit gigante com tudo
git commit -m "feat: adicionar nova funcionalidade completa"
```

**Histórico limpo:**

- Use `git rebase -i` for organizar commits antes of PR
- Combine commits relacionados
- Remova commits de WIP ou debug

### 13.4 Documentação de Contribuições Grandes

**Incluir no PR:**

- Diagrama de arquitetura (se aplicável)
- Decisões de design documentadas
- Plano de migração (se breaking change)
- Guia de teste

---

## 14. Boas Práticas for PRs Limpos e Fáceis de Revisar

### 14.1 Tamanho of PR

**Ideal:**

- **Pequeno**: < 200 linhas (fácil de revisar)
- **Médio**: 200-500 linhas (aceitável)
- **Grande**: > 500 linhas (considerar dividir)

**Dicas:**

- Divida PRs grandes in múltiplos PRs menores
- Cada PR deve ter um propósito claro
- PRs incrementais são mais fáceis de revisar

### 14.2 Organização of Código

**Estrutura:**

- Commits lógicos e bem organizados
- Mudanças relacionadas agrupadas
- Sem código comentado ou debug
- Sem arquivos temporários

**Exemplo de PR bem organizado:**

```
PR: feat(sem-csmf): adicionar suporte a múltiplas ontologias

Commits:
1. feat: adicionar parser de ontologia OWL
2. feat: adicionar suporte a múltiplas ontologias
3. test: adicionar testes for parser
4. docs: atualizar documentação of módulo
```

### 14.3 Description Clara

**Inclua:**

- **O que** foi mudado
- **Por quê** foi mudado
- **Como** testar
- **Impacto** (breaking changes, etc.)

**Exemplo:**

```markdown
## O que foi mudado
Adicionado suporte for múltiplas ontologias OWL no SEM-CSMF.

## Por quê
Permite que diferentes tenants usem ontologias customizadas,
aumentando flexibilidade of sistema.

## Como testar
1. Criar intent com ontologia customizada
2. Verifiesr que NEST é gerado corretamente
3. Executar testes: `pytest tests/unit/test_sem_csmf.py`

## Impacto
- Nova configuração: `ONTOLOGY_PATH`
- Breaking change: Nenhum
- Compatibilidade: Retrocompatível
```

### 14.4 Responder a Feedback

**Quando receber feedback:**

1. **Leia cuidadosamente**: Entenda o que está sendo pedido
2. **Pergunte se necessário**: Se algo não estiver claro, pergunte
3. **Faça alterações**: Implemente as mudanças solicitadas
4. **Comunique**: Informe quando alterações estiverem prontas
5. **Seja profissional**: Mantenha tom respeitoso e construtivo

**Exemplo de resposta:**

```markdown
Obrigado pelo feedback! Fiz as alterações solicitadas:

- ✅ Refatorei a função `parse_ontology` for melhor legibilidade
- ✅ Adicionei testes for o caso de borda mencionado
- ✅ Atualizei a documentação

Por favor, revise novamente quando tiver tempo.
```

### 14.5 Manter PR Atualizado

**Atualizar com main:**

```bash
# Atualizar branch of PR
git checkout feature/minha-feature
git fetch upstream
git rebase upstream/main

# Resolver conflitos se houver
# ...

# Force push (após rebase)
git push origin feature/minha-feature --force-with-lease
```

**Evitar:**

- Force push sem `--force-with-lease`
- Commits de merge desnecessários
- Histórico confuso

---

## Conclusão

This guia fornece as diretrizes necessárias for contribuir efetivamente com o TriSLA. Lembre-se:

- **Quality over speed**: Código bem testado e documentado
- **Comunicação**: Seja claro e respeitoso
- **Aprendizado**: This é um espaço for crescer e aprender

**Recursos adicionais:**

- `DEVELOPER_GUIDE.md`: Guia completo de desenvolvimento
- `ARCHITECTURE_OVERVIEW.md`: Visão geral of arquitetura
- `API_REFERENCE.md`: Referência de APIs
- Issues no GitHub: Para discussões e perguntas

**Dúvidas?**

Abra uma issue no GitHub com a tag `question` ou entre in contato com os mantenedores.

**Obrigado por contribuir com o TriSLA! 🚀**

---

**Última atualização:** 2025-01-XX  
**Versão of documento:** 1.0.0


