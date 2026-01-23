# Documentação da Ontologia TriSLA

This directory contains the complete documentation da Ontologia TriSLA.

## 📚 Documentos Disponíveis

### [Guia Completo de Implementação](ONTOLOGY_IMPLEMENTATION_GUIDE.md)

Guia completo que inclui:

- ✅ **Visão Geral** da ontologia
- ✅ **Estrutura Completa** (classes, propriedades, indivíduos)
- ✅ **Hierarquia de Classes** detalhada
- ✅ **Diagramas Conceituais** (texto ASCII)
- ✅ **Guia de Uso no Protégé** (passo a passo)
- ✅ **Integração com SEM-CSMF** (código de exemplo)
- ✅ **Queries SPARQL** (exemplos práticos)
- ✅ **Validação e Reasoning** (como validar)
- ✅ **Exemplos de Uso** (código Python)
- ✅ **Manutenção e Extensão** (como adicionar classes/propriedades)

## 📁 Arquivos Relacionados

- **Ontologia:** `apps/sem-csmf/src/ontology/trisla.ttl`
- **Loader:** `apps/sem-csmf/src/ontology/loader.py`
- **Reasoner:** `apps/sem-csmf/src/ontology/reasoner.py`
- **Parser:** `apps/sem-csmf/src/ontology/parser.py`
- **Matcher:** `apps/sem-csmf/src/ontology/matcher.py`

## 📚 Documentação Relacionada

- **[Guia Completo do SEM-CSMF](../SEM_CSMF_COMPLETE_GUIDE.md)** — Guia completo do módulo SEM-CSMF
- **[README do SEM-CSMF](../README.md)** — Índice da documentação do SEM-CSMF

## 🎯 Início Rápido

1. **Ler o Guia:** [`ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ONTOLOGY_IMPLEMENTATION_GUIDE.md)
2. **Abrir no Protégé:** `File` → `Open` → `apps/sem-csmf/src/ontology/trisla.ttl`
3. **Validar:** `Reasoner` → `Check consistency`
4. **Exportar Diagramas:** `Window` → `Views` → `Class hierarchy (graph)`

## 📊 Diagramas

Os diagramas devem ser exportados do Protégé:

1. **Hierarquia de Classes:** `Window` → `Views` → `Class hierarchy (graph)`
2. **Relações de Propriedades:** `Window` → `Views` → `Property hierarchy (graph)`
3. **OntoGraf:** `Window` → `Views` → `OntoGraf`

**Nota:** Os diagramas conceituais estão descritos em texto ASCII no guia completo.

---

**Última atualização:** 2025-01-27

