# 📚 Apêndices TriSLA v3.3.0

Este diretório contém os apêndices técnicos da dissertação TriSLA, sincronizados entre o repositório GitHub e o Overleaf.

## 📋 Índice dos Apêndices

| Apêndice | Título | Descrição |
|----------|--------|-----------|
| [A](APENDICE_A_INTERFACES.md) | Catálogo de Interfaces Internas I-* | Interfaces I-01 a I-07, protocolos e SLOs |
| [B](APENDICE_B_NWDAF_NASP.md) | Mapeamento NWDAF ↔ NASP | Equivalência semântica NWDAF (3GPP) e NASP |
| [C](APENDICE_C_APIS_EXEMPLOS.md) | Contratos de API e Exemplos | REST, gRPC e Kafka com exemplos práticos |
| [D](APENDICE_D_TESTES_CONTRATO.md) | Testes de Contrato | Testes reproduzíveis para validação das interfaces |
| [E](APENDICE_E_OBSERVABILIDADE_SLOs.md) | Diretrizes de Observabilidade e SLOs | Plano unificado OpenTelemetry e Prometheus |
| [F](APENDICE_F_RASTREABILIDADE.md) | Matriz de Rastreabilidade | Correlação interfaces ↔ módulos ↔ testes |
| [G](APENDICE_G_LISTAGENS_CODIGO.md) | Listagens de Código | Códigos-fonte dos módulos TriSLA |
| [H](APENDICE_H_EXECUCAO_LOGS.md) | Plano de Execução e Logs | Plano experimental e logs de observabilidade |

## 🔄 Sincronização

Os apêndices são automaticamente sincronizados com o Overleaf:

- **Formato GitHub**: Markdown (`.md`)
- **Formato Overleaf**: LaTeX (`.tex`)
- **Conversão**: Automática via `scripts/sync_appendices_to_overleaf.py`
- **Trigger**: GitHub Actions ao alterar arquivos neste diretório

## 📖 Referências Cruzadas

- [Documentação Principal](../README_DOCUMENTACAO.md)
- [Interfaces da Arquitetura](../interfaces/README.md)
- [Guia de Observabilidade](../opentelemetry/README.md)

## 🔗 Relação com o Código

Cada apêndice referencia diretamente o código-fonte:

- **Apêndice A**: `/apps/*/` (interfaces gRPC/REST/Kafka)
- **Apêndice C**: `/apps/api/openapi.yaml`, `/apps/decision/trisla.v1.proto`
- **Apêndice E**: `/monitoring/`, `/grafana-dashboards/`
- **Apêndice G**: `/apps/sem_csmf/`, `/apps/ml_nsmf/`, `/apps/bc_nssmf/`, `/apps/agents/`

