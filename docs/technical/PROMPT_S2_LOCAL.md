# PROMPT S2 — ML-NSMF (LOCAL)

## Contexto

Este prompt orienta a execução LOCAL do Sprint 2 (ML-NSMF) da arquitetura TriSLA, alinhado à proposta da dissertação (5G / O-RAN / 3GPP / GSMA / ETSI). Todas as operações são executadas no ambiente local de desenvolvimento, sem deploy ou acesso ao NASP.

**Diretório raiz local:** `C:\Users\USER\Documents\TriSLA-clean`  
**Registry:** `ghcr.io/abelisboa`  
**Namespace Kubernetes:** `trisla`  
**Helm Chart:** `helm/trisla/`

---

## Objetivo

Implementar, empacotar e versionar o módulo **ML-NSMF** (Machine Learning Network Slice Management Function), garantindo:

1. **Modelo LSTM operacional** treinado e versionado
2. **Inferência ativa** de viabilidade e risco de violação de SLA
3. **Explicabilidade (XAI)** integrada (SHAP ou equivalente)
4. **Ingestão de métricas** do Prometheus/NASP
5. **Integração com Decision Engine** (interface I-02)
6. **Observabilidade** completa (métricas ML, logs, traces)

---

## Pré-condições

1. Ambiente de desenvolvimento configurado (Python 3.10+, Docker, kubectl, Helm)
2. Acesso ao GitHub Container Registry (GHCR) com token válido
3. Repositório local atualizado e sincronizado
4. Docker Desktop ou Docker Engine em execução
5. Helm 3.12+ instalado
6. Modelo LSTM treinado presente em `apps/ml-nsmf/models/viability_model.pkl`
7. Scaler presente em `apps/ml-nsmf/models/scaler.pkl`

---

## Escopo LOCAL

### Incluído
- Engenharia e correção de código do módulo ML-NSMF
- Validação do modelo LSTM e scaler
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
- Treinamento de novo modelo (usar modelo existente)

---

## Paths e Artefatos Reais

| Artefato | Path Real |
|----------|-----------|
| **Código fonte** | `apps/ml-nsmf/` |
| **Dockerfile** | `apps/ml-nsmf/Dockerfile` |
| **Requirements** | `apps/ml-nsmf/requirements.txt` |
| **Modelo LSTM** | `apps/ml-nsmf/models/viability_model.pkl` |
| **Scaler** | `apps/ml-nsmf/models/scaler.pkl` |
| **Metadata do modelo** | `apps/ml-nsmf/models/model_metadata.json` |
| **Dataset** | `apps/ml-nsmf/data/datasets/trisla_ml_dataset.csv` |
| **Helm values** | `helm/trisla/values.yaml` |
| **Helm templates** | `helm/trisla/templates/` |
| **Documentação técnica** | `docs/technical/02_ML_NSMF.md` |

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

### 2. Validação do Modelo LSTM

```bash
# Navegar para o diretório do módulo
cd C:\Users\USER\Documents\TriSLA-clean\apps\ml-nsmf

# Verificar presença do modelo
dir models\viability_model.pkl
dir models\scaler.pkl
dir models\model_metadata.json

# Validar tamanho dos arquivos (não devem estar vazios)
Get-Item models\viability_model.pkl | Select-Object Length
Get-Item models\scaler.pkl | Select-Object Length
```

### 3. Análise do Código Fonte

```bash
# Verificar estrutura
dir /s /b *.py

# Verificar arquivos principais
type src\main.py
type src\predictor.py
type src\nasp_prometheus_client.py

# Verificar requirements
type requirements.txt
```

### 4. Validação do Predictor

**4.1. Verificar carregamento do modelo**
- Abrir `apps/ml-nsmf/src/predictor.py`
- Verificar que o modelo é carregado corretamente
- Verificar que o scaler é aplicado nas features
- Validar formato de entrada e saída

**4.2. Verificar XAI (Explicabilidade)**
- Verificar implementação de SHAP ou método equivalente
- Validar que explicações são geradas junto com predições
- Verificar formato da saída explicável

**4.3. Verificar integração com Prometheus**
- Abrir `apps/ml-nsmf/src/nasp_prometheus_client.py`
- Verificar queries Prometheus
- Validar janela temporal de coleta
- Verificar tratamento de métricas faltantes

### 5. Revisão do Dockerfile

```bash
# Abrir e revisar Dockerfile
type Dockerfile

# Verificar:
# - Base image versionada (não latest)
# - Cópia do modelo e scaler para a imagem
# - Instalação de dependências ML (tensorflow/pytorch, shap, etc.)
# - Exposição de porta (8081)
# - Comando de entrada correto
# - Variáveis de ambiente (KAFKA_ENABLED=false em modo degraded)
```

### 6. Correção e Melhorias do Código

**6.1. Validar pipeline de inferência**
- Abrir `apps/ml-nsmf/src/predictor.py`
- Verificar pré-processamento de features
- Validar aplicação do scaler
- Verificar formato de saída (viability_score, risk_level, explanation)

**6.2. Validar API REST**
- Abrir `apps/ml-nsmf/src/main.py`
- Verificar rotas REST (porta 8081)
- Validar endpoint de predição: `/api/v1/predict`
- Verificar endpoint de health: `/health`
- Validar códigos de resposta HTTP

**6.3. Validar integração com Decision Engine**
- Verificar cliente gRPC ou REST para Decision Engine
- Validar formato de payload de resposta
- Verificar estados: ACCEPT/REJECT/RENEG

**6.4. Validar observabilidade**
- Abrir `apps/ml-nsmf/src/observability/`
- Verificar métricas Prometheus (prediction_count, prediction_latency, etc.)
- Verificar traces OpenTelemetry
- Verificar logs estruturados com trace_id

### 7. Atualização de Dependências

```bash
# Verificar requirements.txt
type requirements.txt

# Verificar dependências ML:
# - tensorflow ou pytorch (versionado)
# - shap (para XAI)
# - scikit-learn (para scaler)
# - prometheus-client
# - grpcio (se usar gRPC)

# Atualizar se necessário (sem usar versões latest)
# Instalar dependências localmente para teste
pip install -r requirements.txt
```

### 8. Teste Local do Código

```bash
# Teste de carregamento do modelo
python -c "from src.predictor import Predictor; p = Predictor(); print('Model loaded successfully')"

# Executar testes unitários (se existirem)
python -m pytest tests/ -v

# Validar sintaxe
python -m py_compile src/**/*.py
```

### 9. Build da Imagem Docker

```bash
# Definir tag versionada (NÃO usar latest)
$VERSION = "v3.7.11"  # Versão canônica padronizada
$IMAGE_NAME = "ghcr.io/abelisboa/trisla-ml-nsmf"
$FULL_TAG = "${IMAGE_NAME}:${VERSION}"

# Build local (importante: incluir models/ no build context)
docker build -t $FULL_TAG -f apps/ml-nsmf/Dockerfile apps/ml-nsmf/

# Validar imagem criada
docker images | Select-String "trisla-ml-nsmf"

# Verificar tamanho da imagem (modelos podem ser grandes)
docker images $FULL_TAG
```

### 10. Teste Local da Imagem

```bash
# Executar container localmente
docker run -d --name trisla-ml-nsmf-test -p 8081:8081 $FULL_TAG

# Verificar logs
docker logs trisla-ml-nsmf-test

# Testar endpoint REST
curl http://localhost:8081/health
curl http://localhost:8081/api/v1/predict -X POST -H "Content-Type: application/json" -d '{"features": [1.0, 2.0, 3.0]}'

# Verificar métricas
curl http://localhost:8081/metrics

# Parar e remover container
docker stop trisla-ml-nsmf-test
docker rm trisla-ml-nsmf-test
```

### 11. Push para GHCR

```bash
# Fazer login no GHCR (se não feito)
docker login ghcr.io -u abelisboa

# Push da imagem (pode demorar devido ao tamanho do modelo)
docker push $FULL_TAG

# Verificar push bem-sucedido
docker manifest inspect $FULL_TAG
```

### 12. Atualização do Helm Chart

**12.1. Atualizar values.yaml**

```bash
# Abrir helm/trisla/values.yaml
# Localizar seção mlNsmf
# Atualizar tag da imagem:
#   image:
#     repository: trisla-ml-nsmf
#     tag: v3.7.11  # Versão canônica padronizada
# Verificar KAFKA_ENABLED: "false" (modo degraded)
```

**12.2. Validar templates Helm**

```bash
# Verificar template do deployment
type helm\trisla\templates\deployment-ml-nsmf.yaml

# Verificar:
# - Referência correta à imagem
# - Porta exposta (8081)
# - Variáveis de ambiente (KAFKA_ENABLED)
# - Recursos (CPU/memória - ML pode precisar de mais)
# - Replicas (2)
# - Volume mounts para modelo (se necessário)
```

**12.3. Validar chart (sem instalar)**

```bash
# Navegar para o chart
cd helm\trisla

# Validar sintaxe
helm lint .

# Renderizar templates (dry-run)
helm template trisla . --namespace trisla --set mlNsmf.enabled=true
```

### 13. Atualização da Documentação Técnica

**13.1. Atualizar docs/technical/02_ML_NSMF.md**

- Preencher seções vazias:
  - Arquitetura do modelo LSTM (camadas, tamanho, janela)
  - Features e targets
  - Métricas de treinamento (MAE, RMSE)
  - Método XAI adotado (SHAP)
  - Formato de resposta (score + explicação)
  - Integração com Decision Engine
  - Evidências de implementação

**13.2. Documentar mudanças**

- Registrar versão da imagem
- Registrar versão do modelo (se houver)
- Registrar mudanças no código
- Registrar atualizações no Helm

### 14. Versionamento

```bash
# Atualizar CHANGELOG ou similar
# Registrar:
# - Versão da imagem: v3.7.11 (versão canônica padronizada)
# - Versão do modelo: (se aplicável)
# - Data da build
# - Mudanças implementadas
```

---

## Evidências Obrigatórias

### Checklist de Conclusão LOCAL

- [ ] Código fonte revisado e corrigido
- [ ] Modelo LSTM presente e validado (viability_model.pkl)
- [ ] Scaler presente e validado (scaler.pkl)
- [ ] XAI implementado e funcional (SHAP ou equivalente)
- [ ] Dockerfile validado e build bem-sucedido
- [ ] Imagem Docker buildada localmente (com modelo incluído)
- [ ] Imagem testada localmente (container com predição funcional)
- [ ] Imagem publicada no GHCR com tag versionada (não latest)
- [ ] Helm chart atualizado (values.yaml com nova tag)
- [ ] Helm chart validado (helm lint)
- [ ] Documentação técnica atualizada (02_ML_NSMF.md)
- [ ] Logs de build e push salvos
- [ ] Versão da imagem documentada

### Artefatos Gerados

1. **Imagem Docker**: `ghcr.io/abelisboa/trisla-ml-nsmf:v3.7.11` (versão canônica)
2. **Helm values atualizado**: `helm/trisla/values.yaml`
3. **Documentação atualizada**: `docs/technical/02_ML_NSMF.md`
4. **Logs de build**: Salvar em `docs/technical/logs/` (se existir)

---

## Critério de Conclusão

O Sprint 2 LOCAL está concluído quando:

1. ✅ Imagem Docker buildada e publicada no GHCR com tag versionada
2. ✅ Modelo LSTM incluído na imagem e validado
3. ✅ XAI implementado e funcional
4. ✅ Helm chart atualizado e validado (sem erros de lint)
5. ✅ Documentação técnica atualizada com evidências
6. ✅ Código fonte revisado e alinhado à proposta
7. ✅ Integração com Decision Engine documentada

**NÃO executar deploy ou testes no NASP neste momento.**

---

## Próximo Passo

Após conclusão do S2 LOCAL, executar **PROMPT_S2_NASP.md** para deploy e validação no ambiente NASP.

---

**FIM DO PROMPT S2 LOCAL**

