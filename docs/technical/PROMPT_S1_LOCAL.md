# PROMPT S1 — SEM-CSMF (LOCAL)

## Contexto

Este prompt orienta a execução LOCAL do Sprint 1 (SEM-CSMF) da arquitetura TriSLA, alinhado à proposta da dissertação (5G / O-RAN / 3GPP / GSMA / ETSI). Todas as operações são executadas no ambiente local de desenvolvimento, sem deploy ou acesso ao NASP.

**Diretório raiz local:** `C:\Users\USER\Documents\TriSLA-clean`  
**Registry:** `ghcr.io/abelisboa`  
**Namespace Kubernetes:** `trisla`  
**Helm Chart:** `helm/trisla/`

---

## Objetivo

Implementar, empacotar e versionar o módulo **SEM-CSMF** (Semantic-enhanced Communication Service Management Function), garantindo:

1. **Interpretação semântica** de intenções de alto nível usando ontologia OWL
2. **Mapeamento GST → NEST** conforme padrões 3GPP e GSMA
3. **Validação e normalização** de intents com NLP
4. **Geração de NESTs** (Network Slice Templates) para provisionamento
5. **Integração gRPC** com Decision Engine (interface I-01)
6. **Observabilidade** completa (métricas, logs, traces)

---

## Pré-condições

1. Ambiente de desenvolvimento configurado (Python 3.10+, Docker, kubectl, Helm)
2. Acesso ao GitHub Container Registry (GHCR) com token válido
3. Repositório local atualizado e sincronizado
4. Docker Desktop ou Docker Engine em execução
5. Helm 3.12+ instalado

---

## Escopo LOCAL

### Incluído
- Engenharia e correção de código do módulo SEM-CSMF
- Build da imagem Docker localmente
- Push da imagem para GHCR com tag versionada
- Atualização do Helm chart (sem aplicar)
- Atualização da documentação técnica
- Validação local (sem deploy)

### Excluído
- Deploy no Kubernetes
- Execução de testes no NASP
- Acesso ao ambiente NASP
- Execução de código em produção

---

## Paths e Artefatos Reais

| Artefato | Path Real |
|----------|-----------|
| **Código fonte** | `apps/sem-csmf/` |
| **Dockerfile** | `apps/sem-csmf/Dockerfile` |
| **Requirements** | `apps/sem-csmf/requirements.txt` |
| **Ontologia OWL** | `apps/sem-csmf/src/ontology/` |
| **Helm values** | `helm/trisla/values.yaml` |
| **Helm templates** | `helm/trisla/templates/` |
| **Documentação técnica** | `docs/technical/01_SEM_CSMF.md` |

---

## Passos Numerados

### 1. Validação do Ambiente Local

```bash
# Verificar Python
python --version  # Deve ser 3.10+

# Verificar Docker
docker --version
docker ps

# Verificar Helm
helm version

# Verificar acesso ao GHCR
docker login ghcr.io -u abelisboa
```

### 2. Análise do Código Fonte

```bash
# Navegar para o diretório do módulo
cd C:\Users\USER\Documents\TriSLA-clean\apps\sem-csmf

# Verificar estrutura
dir /s /b *.py
dir /s /b *.ttl
dir /s /b *.owl

# Verificar requirements
type requirements.txt
```

### 3. Validação da Ontologia

```bash
# Verificar presença da ontologia
dir src\ontology\*.ttl
dir src\ontology\*.owl

# Validar que a ontologia está versionada
# (verificar arquivo de versionamento ou comentário no código)
```

### 4. Revisão do Dockerfile

```bash
# Abrir e revisar Dockerfile
type Dockerfile

# Verificar:
# - Base image versionada (não latest)
# - Cópia correta de arquivos
# - Instalação de dependências
# - Exposição de portas (8080 HTTP, 50051 gRPC)
# - Comando de entrada correto
```

### 5. Correção e Melhorias do Código

**5.1. Validar mapeamento GST → NEST**
- Abrir `apps/sem-csmf/src/nest_generator.py`
- Verificar tabela de mapeamento GST → NEST
- Garantir que todos os campos obrigatórios estão mapeados
- Documentar regras de inferência

**5.2. Validar integração com ontologia**
- Abrir `apps/sem-csmf/src/intent_processor.py`
- Verificar uso da ontologia OWL
- Garantir validação semântica de intents
- Verificar tratamento de erros

**5.3. Validar API REST e gRPC**
- Abrir `apps/sem-csmf/src/main.py`
- Verificar rotas REST (porta 8080)
- Verificar servidor gRPC (porta 50051)
- Validar códigos de resposta HTTP
- Verificar logs estruturados

**5.4. Validar observabilidade**
- Abrir `apps/sem-csmf/src/observability/`
- Verificar métricas Prometheus
- Verificar traces OpenTelemetry
- Verificar logs estruturados com trace_id

### 6. Atualização de Dependências

```bash
# Verificar requirements.txt
type requirements.txt

# Atualizar se necessário (sem usar versões latest)
# Instalar dependências localmente para teste
pip install -r requirements.txt
```

### 7. Teste Local do Código

```bash
# Executar testes unitários (se existirem)
python -m pytest tests/ -v

# Validar sintaxe
python -m py_compile src/**/*.py
```

### 8. Build da Imagem Docker

```bash
# Definir tag versionada (NÃO usar latest)
$VERSION = "v3.7.11"  # Versão canônica padronizada
$IMAGE_NAME = "ghcr.io/abelisboa/trisla-sem-csmf"
$FULL_TAG = "${IMAGE_NAME}:${VERSION}"

# Build local
docker build -t $FULL_TAG -f apps/sem-csmf/Dockerfile apps/sem-csmf/

# Validar imagem criada
docker images | Select-String "trisla-sem-csmf"
```

### 9. Teste Local da Imagem

```bash
# Executar container localmente
docker run -d --name trisla-sem-csmf-test -p 8080:8080 -p 50051:50051 $FULL_TAG

# Verificar logs
docker logs trisla-sem-csmf-test

# Testar endpoint REST
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/intents

# Parar e remover container
docker stop trisla-sem-csmf-test
docker rm trisla-sem-csmf-test
```

### 10. Push para GHCR

```bash
# Fazer login no GHCR (se não feito)
docker login ghcr.io -u abelisboa

# Push da imagem
docker push $FULL_TAG

# Verificar push bem-sucedido
docker manifest inspect $FULL_TAG
```

### 11. Atualização do Helm Chart

**11.1. Atualizar values.yaml**

```bash
# Abrir helm/trisla/values.yaml
# Localizar seção semCsmf
# Atualizar tag da imagem:
#   image:
#     repository: trisla-sem-csmf
#     tag: v3.7.11  # Versão canônica padronizada
```

**11.2. Validar templates Helm**

```bash
# Verificar template do deployment
type helm\trisla\templates\deployment-sem-csmf.yaml

# Verificar:
# - Referência correta à imagem
# - Portas expostas (8080, 50051)
# - Variáveis de ambiente
# - Recursos (CPU/memória)
# - Replicas
```

**11.3. Validar chart (sem instalar)**

```bash
# Navegar para o chart
cd helm\trisla

# Validar sintaxe
helm lint .

# Renderizar templates (dry-run)
helm template trisla . --namespace trisla
```

### 12. Atualização da Documentação Técnica

**12.1. Atualizar docs/technical/01_SEM_CSMF.md**

- Preencher seções vazias:
  - Entradas e saídas (payloads JSON reais)
  - Tabela de mapeamento GST → NEST
  - Regras de inferência
  - Rotas da API
  - Evidências de implementação

**12.2. Documentar mudanças**

- Registrar versão da imagem
- Registrar mudanças no código
- Registrar atualizações no Helm

### 13. Versionamento

```bash
# Atualizar CHANGELOG ou similar
# Registrar:
# - Versão da imagem: v3.7.11 (versão canônica padronizada)
# - Data da build
# - Mudanças implementadas
```

---

## Evidências Obrigatórias

### Checklist de Conclusão LOCAL

- [ ] Código fonte revisado e corrigido
- [ ] Ontologia OWL presente e versionada
- [ ] Dockerfile validado e build bem-sucedido
- [ ] Imagem Docker buildada localmente
- [ ] Imagem testada localmente (container)
- [ ] Imagem publicada no GHCR com tag versionada (não latest)
- [ ] Helm chart atualizado (values.yaml com nova tag)
- [ ] Helm chart validado (helm lint)
- [ ] Documentação técnica atualizada (01_SEM_CSMF.md)
- [ ] Logs de build e push salvos
- [ ] Versão da imagem documentada

### Artefatos Gerados

1. **Imagem Docker**: `ghcr.io/abelisboa/trisla-sem-csmf:v3.7.11` (versão canônica)
2. **Helm values atualizado**: `helm/trisla/values.yaml`
3. **Documentação atualizada**: `docs/technical/01_SEM_CSMF.md`
4. **Logs de build**: Salvar em `docs/technical/logs/` (se existir)

---

## Critério de Conclusão

O Sprint 1 LOCAL está concluído quando:

1. ✅ Imagem Docker buildada e publicada no GHCR com tag versionada
2. ✅ Helm chart atualizado e validado (sem erros de lint)
3. ✅ Documentação técnica atualizada com evidências
4. ✅ Código fonte revisado e alinhado à proposta
5. ✅ Ontologia OWL presente e funcional
6. ✅ Mapeamento GST → NEST documentado e implementado

**NÃO executar deploy ou testes no NASP neste momento.**

---

## Próximo Passo

Após conclusão do S1 LOCAL, executar **PROMPT_S1_NASP.md** para deploy e validação no ambiente NASP.

---

**FIM DO PROMPT S1 LOCAL**

