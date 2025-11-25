# Documentação do SEM-CSMF

Este diretório contém a documentação completa do módulo SEM-CSMF (Semantic-enhanced Communication Service Management Function).

## 📚 Documentos Disponíveis

### [Guia Completo do SEM-CSMF](SEM_CSMF_COMPLETE_GUIDE.md)

Guia completo que inclui:

- ✅ **Visão Geral** do módulo
- ✅ **Arquitetura** detalhada
- ✅ **Pipeline de Processamento** (Intent → Ontology → GST → NEST)
- ✅ **Ontologia OWL** (subpasta `ontology/`)
- ✅ **NLP** (Natural Language Processing)
- ✅ **Integração** com outros módulos
- ✅ **Interface I-01** (gRPC)
- ✅ **Interface I-02** (Kafka)
- ✅ **Exemplos de Uso** (código Python e REST)
- ✅ **Troubleshooting** (soluções para problemas comuns)

### [Documentação da Ontologia](ontology/)

Documentação completa da Ontologia TriSLA:

- ✅ [Guia de Implementação da Ontologia](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)
- ✅ [README da Ontologia](ontology/README.md)

## 📁 Arquivos Relacionados

- **Código:** `apps/sem-csmf/src/`
- **Ontologia:** `apps/sem-csmf/src/ontology/trisla.ttl`
- **NLP:** `apps/sem-csmf/src/nlp/parser.py`
- **Intent Processor:** `apps/sem-csmf/src/intent_processor.py`
- **NEST Generator:** `apps/sem-csmf/src/nest_generator.py`
- **gRPC Server:** `apps/sem-csmf/src/grpc_server.py`
- **Kafka Producer:** `apps/sem-csmf/src/kafka_producer.py`

## 🎯 Início Rápido

1. **Ler o Guia:** [`SEM_CSMF_COMPLETE_GUIDE.md`](SEM_CSMF_COMPLETE_GUIDE.md)
2. **Entender a Ontologia:** [`ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)
3. **Usar o Módulo:** Ver exemplos no guia completo

## 🔗 Integrações

- **Decision Engine (I-01):** gRPC `localhost:50051`
- **ML-NSMF (I-02):** Kafka `sem-csmf-nests`
- **PostgreSQL:** Persistência de intents e NESTs
- **NASP Adapter:** Coleta de métricas (indireto)

---

**Última atualização:** 2025-01-27

