# Documentação do BC-NSSMF

Este diretório contém a documentação completa do módulo BC-NSSMF.

## 📚 Documentos Disponíveis

### [Guia Completo do BC-NSSMF](BC_NSSMF_COMPLETE_GUIDE.md)

Guia completo que inclui:

- ✅ **Visão Geral** do módulo
- ✅ **Arquitetura** detalhada
- ✅ **Smart Contracts** (Solidity)
- ✅ **Integração Web3** (web3.py)
- ✅ **API REST e gRPC** (endpoints)
- ✅ **Oracle de Métricas** (integração NASP)
- ✅ **Integração** com outros módulos
- ✅ **Interface I-04** (Kafka)
- ✅ **Deploy e Configuração** (Besu, contratos)
- ✅ **Exemplos de Uso** (código Python e REST)
- ✅ **Troubleshooting** (soluções para problemas comuns)

## 📁 Arquivos Relacionados

- **Serviço:** `apps/bc-nssmf/src/service.py`
- **Smart Contract:** `apps/bc-nssmf/src/contracts/SLAContract.sol`
- **Deploy:** `apps/bc-nssmf/src/deploy_contracts.py`
- **API REST:** `apps/bc-nssmf/src/api_rest.py`
- **Oracle:** `apps/bc-nssmf/src/oracle.py`
- **Kafka Consumer:** `apps/bc-nssmf/src/kafka_consumer.py`
- **Besu:** `apps/bc-nssmf/blockchain/besu/docker-compose-besu.yaml`

## 🎯 Início Rápido

1. **Ler o Guia:** [`BC_NSSMF_COMPLETE_GUIDE.md`](BC_NSSMF_COMPLETE_GUIDE.md)
2. **Iniciar Besu:** `docker-compose -f apps/bc-nssmf/blockchain/besu/docker-compose-besu.yaml up -d`
3. **Deploy Contrato:** `python apps/bc-nssmf/src/deploy_contracts.py`
4. **Iniciar Aplicação:** `uvicorn apps.bc-nssmf.src.main:app --port 8083`

## 🔗 Integrações

- **Decision Engine (I-04):** Kafka `trisla-i04-decisions`
- **SLO Reporter:** HTTP REST `POST /bc/update`
- **NASP Adapter:** HTTP REST para métricas

---

**Última atualização:** 2025-01-27

