# TEMPLATE — Registro de Unidade de Trabalho (WU)
# Projeto: TriSLA
# Base: Workflow Oficial TriSLA_NASP + Referência Técnica (docs/Referencia_Tecnica_TriSLA.md)

---

## 📘 Cabeçalho da Unidade de Trabalho

| Campo | Informação |
|--------|-------------|
| **WU-ID** | WU-<número> |
| **Fase** | <0 a 8 conforme Workflow Oficial> |
| **Título** | <descrição curta da tarefa> |
| **Data de Início** | <dd/mm/aaaa> |
| **Data de Conclusão** | <dd/mm/aaaa> |
| **Responsável** | Abel José Rodrigues Lisboa |
| **Branch Git / Estado Base** | <hash ou STATE anterior> |
| **IA Utilizada** | <ChatGPT / Claude / outra> |

---

## 🧩 1. Contexto e Escopo

Descreva brevemente o que esta unidade de trabalho pretende realizar, com base no Workflow Oficial e na Referência Técnica.

**Exemplo:**  
Implementação dos contratos I-01 a I-07, com autenticação mTLS/JWT, geração dos arquivos OpenAPI/Protobuf/Avro e testes automatizados de contrato.

**Arquivos/Pastas Envolvidos:**  
```
contracts/, tests/, infra/
```

**Referências (capítulo/apêndice):**  
- Capítulo: <ex: 4.4.1 ou 5.3>  
- Apêndice: <ex: A, C ou E>  

---

## ⚙️ 2. Instruções Executadas

Descreva o prompt ou comandos principais usados com a IA para esta WU.

```
[SESSION HEADER]
...
[TASK SPEC]
...
[CODEGEN or TEST TEMPLATE]
...
```

**Arquivos Gerados/Alterados:**  
- <arquivo1>  
- <arquivo2>  
- <arquivo3>

---

## 🧠 3. Ações Realizadas pela IA

| Ação | Descrição | Resultado |
|------|------------|------------|
| Criação de Código | Exemplo: geração do arquivo `I-02.proto` | ✅ Sucesso |
| Teste de Contrato | Execução de `pytest tests/test_I02_contracts.py` | ✅ Aprovado |
| Atualização de STATE | Registro em `STATE/002_contracts.md` | ✅ Concluído |
| Documentação | Atualização de `docs/` com novos endpoints | ✅ Feito |

---

## 📈 4. Resultados e Métricas

| Métrica | Valor Obtido | Meta | Status |
|----------|---------------|------|---------|
| Latência média (p99) | <valor> ms | ≤ 50 ms | ✅ |
| Taxa de erro | <valor>% | ≤ 1% | ✅ |
| Cobertura de testes | <valor>% | ≥ 90% | ✅ |
| Contratos válidos | <valor>/total | 100% | ✅ |
| Logs padronizados (Ap. H) | <Sim/Não> | Sim | ✅ |

---

## 📊 5. Evidências (logs, prints, dashboards)

Cole aqui prints ou trechos de logs/dashboards relevantes.

**Exemplo:**  
```
timestamp | módulo | interface | métrica | valor | status | explicação
2025-10-17 13:45 | ML-NSMF | I-02 | Latência | 42 ms | OK | Predição executada
```

**Capturas de Tela:**  
- ./docs/evidencias/WU-<número>_grafana.png  
- ./docs/evidencias/WU-<número>_fabric_explorer.png

---

## 🧾 6. Conclusões

- <Resumo do que foi implementado e validado>  
- <Observações sobre comportamento, desempenho ou ajustes necessários>  

**Exemplo:**  
A integração I-02 (ML-NSMF → Decision Engine) foi concluída com sucesso, os testes de contrato foram aprovados e a latência média permaneceu abaixo de 50 ms. Logs e métricas registrados em conformidade com o Apêndice H.

---

## 🚀 7. Próximos Passos

| Nº | Próxima WU | Objetivo | Status |
|----|-------------|-----------|---------|
| 1 | WU-<seguinte> | <descrição curta> | 🔜 Planejada |
| 2 | — | — | — |

**Observação:** Após revisão, atualizar `STATE/000_INDEX.md` para marcar esta WU como concluída.  

---

📅 **Última Atualização:** <dd/mm/aaaa>  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
