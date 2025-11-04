# TriSLA Build & Publish Automation

Este diretório contém scripts de automação para o pipeline de build e publicação do TriSLA.

## Arquivos

- `trisla_build_publish.py` - Script principal em Python
- `trisla_build_publish.ps1` - Script principal em PowerShell (Windows)
- `test_automation.py` - Script de teste em Python
- `test_automation.ps1` - Script de teste em PowerShell (Windows)

## Funcionalidades

### Script Principal
- Lê o arquivo CSV de acompanhamento (`PROMPTS/automation/TRISLA_PIPELINE_TRACKER.csv`)
- Identifica itens pendentes (status ❌ ou ⚙️)
- Executa comandos automaticamente
- Atualiza o status no CSV após execução
- Fornece relatório detalhado de execução

### Script de Teste
- Valida a estrutura do CSV
- Identifica itens pendentes
- Testa a lógica sem executar comandos reais

## Uso

### Python (Linux/macOS)
```bash
# Testar primeiro
python automation/test_automation.py

# Executar automação
python automation/trisla_build_publish.py
```

### PowerShell (Windows)
```powershell
# Testar primeiro
powershell -ExecutionPolicy Bypass -File automation/test_automation.ps1

# Executar automação
powershell -ExecutionPolicy Bypass -File automation/trisla_build_publish.ps1

# Modo dry-run (sem executar comandos)
powershell -ExecutionPolicy Bypass -File automation/trisla_build_publish.ps1 -DryRun
```

## Estrutura do CSV

O arquivo CSV deve conter as seguintes colunas:
- `Etapa` - Número da etapa
- `Item` - Nome do item
- `Descrição` - Descrição do item
- `Comando Principal` - Comando a ser executado
- `Status Atual` - Status atual (❌, ⚙️, ✅)
- `Próxima Ação` - Próxima ação necessária
- `Data Última Atualização` - Timestamp da última atualização
- `Responsável` - Responsável pelo item

## Status dos Itens

- ❌ - Falha/Pendente
- ⚙️ - Em execução/Pendente
- ✅ - Concluído com sucesso

## Exemplo de Uso

1. **Preparação**: Verificar se o arquivo CSV existe e está atualizado
2. **Teste**: Executar o script de teste para validar a estrutura
3. **Execução**: Executar o script principal para processar itens pendentes
4. **Verificação**: Verificar o relatório de execução e status atualizado no CSV

## Comandos Suportados

O script executa qualquer comando shell válido, incluindo:
- Docker build e push
- Helm deployments
- Kubectl commands
- Git operations
- Validações e testes

## Logs e Relatórios

O script fornece:
- Log detalhado de cada comando executado
- Status de sucesso/falha
- Output dos comandos
- Resumo final da execução
- Atualização automática do CSV

## Troubleshooting

### Problemas Comuns

1. **CSV não encontrado**: Verificar o caminho do arquivo
2. **Permissões**: Verificar permissões de execução e escrita
3. **Comandos falhando**: Verificar se os comandos estão corretos no CSV
4. **Encoding**: Verificar encoding UTF-8 do arquivo CSV

### Modo Dry-Run

Use o parâmetro `-DryRun` para testar sem executar comandos reais:
```powershell
powershell -ExecutionPolicy Bypass -File automation/trisla_build_publish.ps1 -DryRun
```

## Integração com CI/CD

O script pode ser integrado em pipelines CI/CD:
- Executar após mudanças no código
- Atualizar status automaticamente
- Gerar relatórios de build
- Notificar sobre falhas

## Manutenção

- Atualizar comandos no CSV conforme necessário
- Revisar logs de execução regularmente
- Manter backup do arquivo CSV
- Testar mudanças antes de executar em produção