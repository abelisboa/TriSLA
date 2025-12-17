# PROMPT S3 — BC-NSSMF (LOCAL)

## Contexto

Este prompt orienta a execução LOCAL do Sprint 3 (BC-NSSMF) da arquitetura TriSLA, alinhado à proposta da dissertação (5G / O-RAN / 3GPP / GSMA / ETSI). Todas as operações são executadas no ambiente local de desenvolvimento, sem deploy ou acesso ao NASP.

**Diretório raiz local:** `C:\Users\USER\Documents\TriSLA-clean`  
**Registry:** `ghcr.io/abelisboa`  
**Namespace Kubernetes:** `trisla`  
**Helm Chart:** `helm/trisla/`

---

## Objetivo

Implementar, empacotar e versionar o módulo **BC-NSSMF** (Blockchain Network Slice Subnet Management Function), garantindo:

1. **Smart Contracts** executáveis em rede Besu
2. **Deploy de contratos** com endereços versionados
3. **Vínculo SLA ↔ contrato ↔ transações** (tx hash, eventos)
4. **Estados do SLA** (CREATED, ACTIVE, VIOLATED, RENEGOTIATED, CLOSED)
5. **Eventos on-chain** (SlaCreated, SlaActivated, SlaViolation, etc.)
6. **Integração com Decision Engine** (interface I-03)
7. **Observabilidade** completa (métricas, logs, traces)

---

## Pré-condições

1. Ambiente de desenvolvimento configurado (Python 3.10+, Docker, kubectl, Helm)
2. Acesso ao GitHub Container Registry (GHCR) com token válido
3. Repositório local atualizado e sincronizado
4. Docker Desktop ou Docker Engine em execução
5. Helm 3.12+ instalado
6. Smart Contract Solidity presente em `apps/bc-nssmf/src/contracts/SLAContract.sol`
7. Script de deploy presente em `apps/bc-nssmf/src/deploy_contracts.py`

---

## Escopo LOCAL

### Incluído
- Engenharia e correção de código do módulo BC-NSSMF
- Validação do Smart Contract Solidity
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
- Deploy de contratos em rede real (apenas validação)

---

## Paths e Artefatos Reais

| Artefato | Path Real |
|----------|-----------|
| **Código fonte** | `apps/bc-nssmf/` |
| **Dockerfile** | `apps/bc-nssmf/Dockerfile` |
| **Requirements** | `apps/bc-nssmf/requirements.txt` |
| **Smart Contract** | `apps/bc-nssmf/src/contracts/SLAContract.sol` |
| **Endereço do contrato** | `apps/bc-nssmf/src/contracts/contract_address.json` |
| **Script de deploy** | `apps/bc-nssmf/src/deploy_contracts.py` |
| **Wallet/Chaves** | `apps/bc-nssmf/src/blockchain/wallet.py` |
| **Helm values** | `helm/trisla/values.yaml` |
| **Helm templates** | `helm/trisla/templates/` |
| **Documentação técnica** | `docs/technical/03_BC_NSSMF.md` |

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

# Verificar se web3/solc disponível (para contratos)
python -c "import web3; print('web3 OK')" 2>/dev/null || echo "web3 não instalado"
```

### 2. Validação do Smart Contract

```bash
# Navegar para o diretório do módulo
cd C:\Users\USER\Documents\TriSLA-clean\apps\bc-nssmf

# Verificar presença do contrato
type src\contracts\SLAContract.sol

# Verificar endereço do contrato (se já deployado)
type src\contracts\contract_address.json

# Validar estrutura do contrato:
# - Estados do SLA (CREATED, ACTIVE, VIOLATED, RENEGOTIATED, CLOSED)
# - Eventos (SlaCreated, SlaActivated, SlaViolation, etc.)
# - Funções (createSla, activateSla, reportViolation, etc.)
```

### 3. Análise do Código Fonte

```bash
# Verificar estrutura
dir /s /b *.py

# Verificar arquivos principais
type src\main.py
type src\service.py
type src\blockchain\tx_sender.py
type src\blockchain\wallet.py
type src\deploy_contracts.py

# Verificar requirements
type requirements.txt
```

### 4. Validação da Integração Blockchain

**4.1. Verificar conexão com Besu**
- Abrir `apps/bc-nssmf/src/config.py`
- Verificar `TRISLA_RPC_URL` ou `BESU_RPC_URL`
- Validar chain ID (1337)
- Verificar tratamento de erros de conexão

**4.2. Verificar deploy de contratos**
- Abrir `apps/bc-nssmf/src/deploy_contracts.py`
- Verificar compilação do contrato Solidity
- Validar deploy e salvamento do endereço
- Verificar tratamento de erros

**4.3. Verificar transações**
- Abrir `apps/bc-nssmf/src/blockchain/tx_sender.py`
- Verificar assinatura de transações
- Validar envio e confirmação
- Verificar tratamento de falhas

**4.4. Verificar eventos on-chain**
- Abrir `apps/bc-nssmf/src/service.py`
- Verificar leitura de eventos
- Validar parsing de eventos
- Verificar filtros de eventos

### 5. Revisão do Dockerfile

```bash
# Abrir e revisar Dockerfile
type Dockerfile

# Verificar:
# - Base image versionada (não latest)
# - Cópia do contrato Solidity para a imagem
# - Instalação de dependências (web3, solc, etc.)
# - Exposição de porta (8083)
# - Comando de entrada correto
# - Variáveis de ambiente (TRISLA_RPC_URL, etc.)
```

### 6. Correção e Melhorias do Código

**6.1. Validar API REST**
- Abrir `apps/bc-nssmf/src/api_rest.py`
- Verificar rotas REST (porta 8083)
- Validar endpoints:
  - `/api/v1/sla/create` (criar SLA)
  - `/api/v1/sla/activate` (ativar SLA)
  - `/api/v1/sla/violation` (reportar violação)
  - `/api/v1/sla/renegotiate` (renegociar)
  - `/api/v1/sla/close` (fechar)
  - `/api/v1/sla/status` (consultar estado)
- Verificar códigos de resposta HTTP

**6.2. Validar integração com Decision Engine**
- Verificar cliente gRPC ou REST para Decision Engine
- Validar formato de payload de resposta
- Verificar interface I-03 (consumidor)

**6.3. Validar observabilidade**
- Abrir `apps/bc-nssmf/src/observability/`
- Verificar métricas Prometheus (tx_count, tx_failed, etc.)
- Verificar traces OpenTelemetry
- Verificar logs estruturados com trace_id e tx_hash

**6.4. Validar segurança**
- Verificar gestão de chaves privadas (wallet.py)
- Validar que chaves não são hardcoded
- Verificar uso de secrets/volumes para chaves
- Validar assinatura de transações

### 7. Atualização de Dependências

```bash
# Verificar requirements.txt
type requirements.txt

# Verificar dependências blockchain:
# - web3 (versionado)
# - py-solc-x ou solcx (para compilação)
# - eth-account (para assinatura)
# - grpcio (se usar gRPC)

# Atualizar se necessário (sem usar versões latest)
# Instalar dependências localmente para teste
pip install -r requirements.txt
```

### 8. Teste Local do Código

```bash
# Validar sintaxe
python -m py_compile src/**/*.py

# Teste de compilação do contrato (se possível)
# python src/deploy_contracts.py --compile-only

# Executar testes unitários (se existirem)
python -m pytest tests/ -v
```

### 9. Build da Imagem Docker

```bash
# Definir tag versionada (NÃO usar latest)
# Versão canônica: v3.7.11 (padronizada no PASSO 0)
$VERSION = "v3.7.11"
$IMAGE_NAME = "ghcr.io/abelisboa/trisla-bc-nssmf"
$FULL_TAG = "${IMAGE_NAME}:${VERSION}"

# Build local
docker build -t $FULL_TAG -f apps/bc-nssmf/Dockerfile apps/bc-nssmf/

# Validar imagem criada
docker images | Select-String "trisla-bc-nssmf"
```

### 10. Teste Local da Imagem

```bash
# Executar container localmente (sem Besu, apenas validação de build)
docker run -d --name trisla-bc-nssmf-test -p 8083:8083 $FULL_TAG

# Verificar logs
docker logs trisla-bc-nssmf-test

# Testar endpoint REST (pode falhar sem Besu, mas valida que o serviço inicia)
curl http://localhost:8083/health

# Parar e remover container
docker stop trisla-bc-nssmf-test
docker rm trisla-bc-nssmf-test
```

### 11. Push para GHCR

```bash
# Fazer login no GHCR (se não feito)
docker login ghcr.io -u abelisboa

# Push da imagem
docker push $FULL_TAG

# Verificar push bem-sucedido
docker manifest inspect $FULL_TAG
```

### 12. Atualização do Helm Chart

**12.1. Atualizar values.yaml**

```bash
# Abrir helm/trisla/values.yaml
# Localizar seção bcNssmf
# Atualizar tag da imagem:
#   image:
#     repository: trisla-bc-nssmf
#     tag: v3.7.11  # Versão canônica padronizada no PASSO 0
# Verificar TRISLA_RPC_URL será injetado automaticamente se Besu habilitado
```

**12.2. Validar templates Helm**

```bash
# Verificar template do deployment
type helm\trisla\templates\deployment-bc-nssmf.yaml

# Verificar:
# - Referência correta à imagem
# - Porta exposta (8083)
# - Variáveis de ambiente (TRISLA_RPC_URL, BESU_RPC_URL)
# - Recursos (CPU/memória)
# - Replicas (2)
# - Healthcheck (pode estar desabilitado em modo degraded)
```

**12.3. Validar chart (sem instalar)**

```bash
# Navegar para o chart
cd helm\trisla

# Validar sintaxe
helm lint .

# Renderizar templates (dry-run)
helm template trisla . --namespace trisla --set bcNssmf.enabled=true
```

### 13. Atualização da Documentação Técnica

**13.1. Atualizar docs/technical/03_BC_NSSMF.md**

- Preencher seções vazias:
  - Arquitetura on-chain (config Besu, RPC endpoints, chainId)
  - Modelo de contrato (estados, eventos, funções)
  - Endereço do contrato deployado
  - Tx hash de deploy
  - Exemplo de evento emitido
  - Integração com Decision Engine
  - Evidências de implementação

**13.2. Documentar mudanças**

- Registrar versão da imagem
- Registrar endereço do contrato (se já deployado)
- Registrar mudanças no código
- Registrar atualizações no Helm

### 14. Versionamento

```bash
# Atualizar CHANGELOG ou similar
# Registrar:
# - Versão da imagem: v3.7.11 (versão canônica padronizada no PASSO 0)
# - Endereço do contrato (se aplicável)
# - Data da build
# - Mudanças implementadas
```

---

## Evidências Obrigatórias

### Checklist de Conclusão LOCAL

- [ ] Código fonte revisado e corrigido
- [ ] Smart Contract Solidity presente e validado (SLAContract.sol)
- [ ] Dockerfile validado e build bem-sucedido
- [ ] Imagem Docker buildada localmente
- [ ] Imagem testada localmente (container inicia)
- [ ] Imagem publicada no GHCR com tag versionada (não latest)
- [ ] Helm chart atualizado (values.yaml com nova tag)
- [ ] Helm chart validado (helm lint)
- [ ] Documentação técnica atualizada (03_BC_NSSMF.md)
- [ ] Logs de build e push salvos
- [ ] Versão da imagem documentada
- [ ] Tag padronizada: v3.7.11 (corrigido no PASSO 0)

### Artefatos Gerados

1. **Imagem Docker**: `ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.11` (versão canônica)
2. **Helm values atualizado**: `helm/trisla/values.yaml`
3. **Documentação atualizada**: `docs/technical/03_BC_NSSMF.md`
4. **Logs de build**: Salvar em `docs/technical/logs/` (se existir)

---

## Critério de Conclusão

O Sprint 3 LOCAL está concluído quando:

1. ✅ Imagem Docker buildada e publicada no GHCR com tag versionada
2. ✅ Smart Contract validado e documentado
3. ✅ Helm chart atualizado e validado (sem erros de lint)
4. ✅ Documentação técnica atualizada com evidências
5. ✅ Código fonte revisado e alinhado à proposta
6. ✅ Integração com Decision Engine documentada
7. ✅ Tag padronizada (resolver inconsistência)

**NÃO executar deploy ou testes no NASP neste momento.**

---

## Nota sobre Tag BC-NSSMF

✅ **VERSÃO CANÔNICA:** `v3.7.11` (padronizada no PASSO 0)

---

## Próximo Passo

Após conclusão do S3 LOCAL, executar **PROMPT_S3_NASP.md** para deploy e validação no ambiente NASP.

---

**FIM DO PROMPT S3 LOCAL**

